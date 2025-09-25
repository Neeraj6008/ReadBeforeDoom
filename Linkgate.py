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
import re
import ipaddress
from urllib.parse import urlparse, urlunparse, urljoin
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
def tld_check():
    cache_dir = os.path.expanduser("~/.linkgate_cache")
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, "tld_cache.json")
    max_age = 604800  # 7 days in seconds

    # Check cache validity and load if fresh
    try:
        if (os.path.exists(cache_path) and 
            (time.time() - os.path.getmtime(cache_path)) < max_age):
            try:
                with open(cache_path, 'r') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                pass  # Fall through to fetch fresh data
    except OSError:
        pass  # Permission issues with cache file, fall through to fetch

    # Fetch fresh data from IANA
    try:
        response = requests.get(
            "https://data.iana.org/TLD/tlds-alpha-by-domain.txt",
            timeout=10
        )
        response.raise_for_status()
        tld_list = response.text.split()
        
        # Save to cache
        try:
            with open(cache_path, 'w') as f:
                json.dump(tld_list, f)
        except Exception:
            pass  # Cache save failure shouldn't break functionality
            
        return tld_list
        
    except requests.RequestException:
        # if ntwork fails try to use stale cache as backup.
        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except Exception:
            raise

# Main function that Checks if the given url has a valid format and is reachable.
def linkgate(url):
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
        parsed = urlparse(url)

    # Validate scheme and hostname
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

    # TLD verification using the merged function
    IDN = parsed.hostname.split(".")[-1] if parsed.hostname else ""
    try:
        TLD = tld_check()  # Uses the new merged function
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
            "message": "Couldn't load TLDs from IANA",
        }

    # IDNA processing
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

    # IP validation
    ips = ipvcollector(url0)
    if isinstance(ips, dict) and "iplist" not in ips:
        return ips

    iplist = ips.get("iplist", []) if isinstance(ips, dict) else []
    if not iplist:
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

    # URL reconstruction
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

    # HTTP validation
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
    }

    try:
        response = requests.head(url1, timeout=5, headers=header, allow_redirects=False)
        status_code_valid = status_code_checker(response)
        redir = status_code_valid.get("redirect/link")
        
        if status_code_valid["valid"]:
            if isinstance(redir, str) and redir:
                url_final = urljoin(url1, redir)
            else:
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