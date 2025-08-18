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
import urllib.parse

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
        sys.exit(f"Hostname does not exist: {hostname}")
    except dns.resolver.Timeout:
        sys.exit(f"DNS query timed out for: {hostname}")
    except dns.resolver.NoAnswer:
        ipv4_add = []

    try:
        answers6 = dns.resolver.resolve(hostname, 'AAAA')  # IPv6
        ipv6_add = [rdata.address for rdata in answers6]
    except (dns.resolver.NXDOMAIN, dns.resolver.Timeout, dns.resolver.NoAnswer):
        ipv6_add = []

    return ipv4_add + ipv6_add


def linkgate(url):  # Checks if the given url has a valid format and is reachable.
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
        parsed = urllib.parse.urlparse(url)

    elif parsed.scheme not in ("http", "https"):  # Checks if the scheme of the url is http or https, if not, program exits.
        sys.exit("The given link doesn't have a valid scheme (http or https).")
        
    elif not parsed.hostname:   # Checks if the hostname (the www.site.com/org/... part of the link.) is valid, if not, program exits.
        sys.exit("The hostname of the given url is invalid.")


    IDN = (parsed.hostname.split('.')[-1])  # This block verifies the TLD of the hostname (the .com/org/... part of hostname), if not, program exits.
    try:
        TLD = requests.get("https://data.iana.org/TLD/tlds-alpha-by-domain.txt", timeout=5).text.split()
        if not IDN.upper() in TLD:
            sys.exit("This url has an invalid TLD.")
    except requests.RequestException:
        sys.exit("Couldn't load TLDs from https://data.iana.org/TLD/tlds-alpha-by-domain.txt")


    try:    # This block check if the hostname is a non-ASCII hostname, if yes, it decodes into an ASCII-equivalent.
        if re.search(r'[^\x00-\x7F]', parsed.hostname): 
            ascii_hostname = idna.encode(parsed.hostname).decode("ascii")
        else:
            ascii_hostname = parsed.hostname
    except idna.IDNAError:
        sys.exit(f"Invalid Internationalized domain: {parsed.hostname}")

    if not len(ipvcollector(ascii_hostname)) == 0:
        for ip_str in ipvcollector(ascii_hostname):
            ipobject = ipaddress.ip_address(ip_str)
            if ipobject.is_private or ipobject.is_loopback or ipobject.is_reserved or ipobject.is_multicast:
                sys.exit(f"Reserved/Loopback/private/multicast URL: {url}")
    print(ascii_hostname)
    return ascii_hostname

    

# TODO: Improve subfunc_linkformat_check pre-validation
# - Reject non-ASCII hostnames early (regex check) OR handle IDN via idna.encode() ✅
# - Validate TLD against IANA list (https://data.iana.org/TLD/tlds-alpha-by-domain.txt) ✅
#   Reject unknown/reserved TLDs ✅
# - Reject reserved/private/loopback/multicast IPs before connect ✅
# - Strictly allow only http/https schemes ✅
# - (Optional) Normalize punycode domains and handle encoding errors ✅
# - Add logic to cache the TLD list to make the program faster and reduce data usage

if __name__ == "__main__":
    url = input("Enter url: ")
    linkgate(url)