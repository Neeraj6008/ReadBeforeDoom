"""
What linkgate(url) does:

1. Takes a url
2. Verifies the format of the url, or returns "url is invalid"
3. Verifies if the url is reachable
4. returns a dictionary containing info about validity of url, status code, custom message, and the url itself

✅ = function is done 100%
"""

import os
import json
import time
import sys
import re
import ipaddress
from urllib.parse import urlparse, urlunparse, urljoin  # added urljoin for relative redirects
import requests
import idna
import dns.resolver
import dns.name

# Helper Functions:
def ipvcollector(hostname):
    try:
        answers = dns.resolver.resolve(hostname, "A")
        ipv4_add = [rdata.to_text() for rdata in answers]
    except dns.resolver.NXDOMAIN:
        return {
            "valid": False,
            "url": hostname,
            "message": f"Hostname does not exist: {hostname}",
        }
    except dns.resolver.Timeout:
        return {
            "valid": False,
            "url": hostname,
            "message": f"DNS query timed out for: {hostname}",
        }
    except dns.resolver.NoAnswer:
        ipv4_add = []
    except dns.name.LabelTooLong:
        return {"valid": False, "url": hostname, "message": f"DNS label too long in hostname: {hostname}"}

    try:
        answers6 = dns.resolver.resolve(hostname, "AAAA")  # IPv6
        ipv6_add = [rdata.to_text() for rdata in answers6]
    except (dns.resolver.NXDOMAIN, dns.resolver.Timeout, dns.resolver.NoAnswer):
        ipv6_add = []

    return {"iplist": ipv4_add + ipv6_add}

# Checks if the hostname (specifically the subdomain part) is valid or not.
def is_valid_hostname(hostname):
    if len(hostname) > 253:
        return False
    labels = hostname.split(".")
    # Check each label length must be <= 63
    for label in labels:
        if len(label) > 63:
            return False
    pattern = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$", re.IGNORECASE)
    for label in labels:
        if not pattern.match(label):
            return False
    for label in labels:
        if re.match(r"^(.)\1{3,}$", label, re.IGNORECASE):
            return False
    return True

# Function to check the status code of the website and check if we can continue with scraping the website.
def status_code_checker(response):
    if 300 <= response.status_code <= 399:
        return {"valid": True, "redirect/link": response.headers.get("Location")}
    elif response.status_code < 300:
        return {"valid": True, "redirect/link": response.url}
    else:
        return {"valid": False, "redirect/link": False}

# Functions to cache the TLD IDNA list, because getting it each time from the internet is wasteful.
def get_tld_cache_path():
    cache_dir = os.path.expanduser("~/.linkgate_cache")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, "tld_cache.json")

def is_cache_valid(cache_path, max_age_seconds=604800):  # One week = 604800 seconds
    if not os.path.exists(cache_path):
        return False
    file_age = time.time() - os.path.getmtime(cache_path)
    return file_age < max_age_seconds

def load_tld_cache(cache_path):
    try:
        with open(cache_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def save_tld_cache(cache_path, tld_list):
    with open(cache_path, 'w') as f:
        json.dump(tld_list, f)

def get_tld_list():
    cache_path = get_tld_cache_path()
    # Try to use cached data first
    if is_cache_valid(cache_path):
        cached_data = load_tld_cache(cache_path)
        if cached_data:
            return cached_data
    # Fetch fresh data if cache is invalid/missing
    try:
        response = requests.get(
            "https://data.iana.org/TLD/tlds-alpha-by-domain.txt",
            timeout=10)
        tld_list = response.text.split()
        # Save to cache
        save_tld_cache(cache_path, tld_list)
        return tld_list
    except requests.RequestException:
        # Fall back to cached data if network fails
        cached_data = load_tld_cache(cache_path)
        if cached_data:
            return cached_data
        raise  # Re-raise if no cache available

# Main Function:
# Checks if the given url has a valid format and is reachable.
def linkgate(url):
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
        parsed = urlparse(url)  # ensure scheme added

    # After normalizing the scheme, validate scheme/host in independent checks
    if parsed.scheme not in ("http", "https"):
        return {
            "valid": False,
            "url": url,
            "message": "The given link doesn't have a valid scheme (http or https).",
        }

    if parsed.hostname and not is_valid_hostname(parsed.hostname):
        return {
            "valid": False,
            "url": url,
            "message": "The hostname of the given url is invalid.",
        }

    # This block verifies the TLD of the hostname (the .com/org/... part of hostname)
    IDN = parsed.hostname.split(".")[-1] if parsed.hostname else ""
    try:
        TLD = get_tld_list()
        if IDN.upper() not in TLD:
            return {
                "valid": False,
                "url": url,
                "message": "This url has an invalid hostname.",
            }
    except requests.RequestException:
        return {
            "valid": False,
            "url": url,
            "message": "Couldn't load TLDs from https://data.iana.org/TLD/tlds-alpha-by-domain.txt",
        }

    # Decode Internationalized domain to ASCII-equivalent if needed.
    try:
        if parsed.hostname and re.search(r"[^\x00-\x7F]", parsed.hostname):
            url0 = idna.encode(parsed.hostname).decode("ascii")
        else:
            url0 = parsed.hostname or ""
    except idna.IDNAError:
        return {
            "valid": False,
            "url": parsed.hostname or "",
            "message": f"Invalid Internationalized domain: {parsed.hostname}",
        }

    # Checks if the url directs to a private, loopback, reserved or multicast website.
    ips = ipvcollector(url0)
    # If ipvcollector returned an error dict (without "iplist"), pass it through
    if isinstance(ips, dict) and "iplist" not in ips:
        return ips

    iplist = ips.get("iplist", []) if isinstance(ips, dict) else []
    if not iplist:  # Check if IP list is empty
        return {
            "valid": False,
            "url": url0,
            "message": f"No IP addresses found for hostname: {url0}",
        }

    for ip_str in iplist:
        ipobject = ipaddress.ip_address(ip_str)
        if (
            ipobject.is_private
            or ipobject.is_loopback
            or ipobject.is_reserved
            or ipobject.is_multicast
        ):
            return {
                "valid": False,
                "url": url0,
                "message": f"Reserved/Loopback/private/multicast URL: {url0}",
            }
    # (no premature return here; proceed when all IPs are acceptable)

    # All the pre validation checks have been done, remake the verified url into usable form.
    port = ""
    if parsed.netloc and ":" in parsed.netloc:
        parts = parsed.netloc.split(":")
        if len(parts) == 2 and parts[1].isdigit():
            port = ":" + parts[1]

    normalized_netloc = url0 + port
    url1 = urlunparse((
        parsed.scheme,
        normalized_netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment,
    ))

    # Validation Part
    # Using headers increases the chances of the website allowing this program to access it.
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
    }

    try:
        # Avoid auto-follow so we can normalize relative Location headers
        response = requests.head(url1, timeout=5, headers=header, allow_redirects=False)
        status_code_valid = status_code_checker(response)
        redir = status_code_valid.get("redirect/link")
        if status_code_valid["valid"]:
            if isinstance(redir, str) and redir:
                # Only join when it's actually a string (relative or absolute)
                url_final = urljoin(url1, redir)
            else:
                # For 2xx (no Location) or when redirect/link isn't a string
                url_final = response.url or url1
        else:
            return {"valid": False, "url": url1, "message": "Invalid response status code"}
    
    except requests.exceptions.RequestException as e:
        return {"valid": False, "url": url1, "message": f"Connection failed: {str(e)}"}

    return {
        "valid": True,
        "url": url_final,
        "message": "URL is valid and reachable",
    }

if __name__ == "__main__":
    print(linkgate("www.fitgirlrepacks.org")["url"])
