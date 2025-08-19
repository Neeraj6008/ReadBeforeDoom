'''
What linkgate(url) does:
1. Takes a url
2. Verifies the format of the url, or returns "url is invalid"
3. Verifies if the url is reachable
4. returns a dictionary containing info about validity of url, status code, custom message, and the url itself

✅ = function is done 100%
'''

# Standard library
import sys
import re
import ipaddress
from urllib.parse import urlparse, urlunparse

# Third-party libraries
import requests
import idna
import dns.resolver

# Local application imports
import whitelist


def ipvcollector(hostname):
    try:
        answers = dns.resolver.resolve(hostname, 'A')
        ipv4_add = [rdata.address for rdata in answers]
    except dns.resolver.NXDOMAIN:
        return {
            "valid" : False,
            "url" : hostname,
            "message" : f"Hostname does not exist: {hostname}"
        }

    except dns.resolver.Timeout:
       return {
            "valid" : False,
            "url" : hostname,
            "message" : f"DNS query timed out for: {hostname}"
        }

    except dns.resolver.NoAnswer:
        ipv4_add = []

    try:
        answers6 = dns.resolver.resolve(hostname, 'AAAA')  # IPv6
        ipv6_add = [rdata.address for rdata in answers6]
    except (dns.resolver.NXDOMAIN, dns.resolver.Timeout, dns.resolver.NoAnswer):
        ipv6_add = []

    return {
        "iplist" : ipv4_add + ipv6_add
        }


# Checks if the given url has a valid format and is reachable.
def linkgate(url):
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
        parsed = urlparse(url)

# Checks if the scheme of the url follows http/https scheme or any other (rejects any other scheme).
    elif parsed.scheme not in ("http", "https"):
        return {"valid" : False,
                "url" : url,
                "message": "The given link doesn't have a valid scheme (http or https)."
                }

# Checks if the hostname (the www.site.com/org/... part of the link.) is valid or not.        
    elif not parsed.hostname:
        return {
            "valid" : False,
            "url" : url,
            "message" : "The hostname of the given url is invalid."
        }


# This block verifies the TLD of the hostname (the .com/org/... part of hostname), if not, program exits.
    IDN = (parsed.hostname.split('.')[-1])  
    try:
        TLD = requests.get("https://data.iana.org/TLD/tlds-alpha-by-domain.txt", timeout=5).text.split()
        if not IDN.upper() in TLD:
            return {
                "valid" : False,
                "url" : url,
                "message" : "This url has an invalid TLD." 
            }
        
    except requests.RequestException:
        return {
            "valid" : False,
            "url" : url,
            "message" : "Couldn't load TLDs from https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
        }


# This block check if the hostname is a non-ASCII hostname, if yes, it decodes into an ASCII-equivalent.
    try:
        if re.search(r'[^\x00-\x7F]', parsed.hostname): 
            url0 = idna.encode(parsed.hostname).decode("ascii")
        else:
            url0 = parsed.hostname

    except idna.IDNAError:
        return {
            "valid" : False,
            "url" : url0,
            "message" : f"Invalid Internationalized domain: {parsed.hostname}"
        }

    ips = ipvcollector(url0)
    if ips:
        for ip_str in ips:
            ipobject = ipaddress.ip_address(ip_str)
            if ipobject.is_private or ipobject.is_loopback or ipobject.is_reserved or ipobject.is_multicast:
                return {
            "valid" : False,
            "url" : url0,
            "message" : f"Reserved/Loopback/private/multicast URL: {url0}"
        }

    port = ""
    if ':' in parsed.netloc:
        port = ":" + parsed.netloc.split(":")[1]
    normalized_netloc = url0 + port

    reconstructed_url = urlunparse((
        parsed.scheme, normalized_netloc,
        parsed.path, parsed.params,
        parsed.query, parsed.fragment
    ))

    return {
        "valid": True,
        "url": reconstructed_url,
        "message": "URL is valid"
}


    

# TODO: Implement TLD list caching to improve performance and reduce network usage
# - Store TLD list locally in a cache file (e.g., tld_cache.txt or JSON)
# - Track cache timestamp to enable cache expiration (e.g., refresh if older than 7 days)
# - On validation, check cache freshness and load cached TLD list if valid
# - Refresh cache by fetching from https://data.iana.org/TLD/tlds-alpha-by-domain.txt when expired or missing
# - Handle network failures gracefully by falling back to cached data if available
# - Use file I/O (read/write), datetime for timestamps, and exception handling for robustness
# - Integrate caching logic to replace live network calls in the TLD validation step


if __name__ == "__main__":
    url = input("Enter url: ")
    linkgate(url)