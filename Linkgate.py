'''
What linkgate(url) does:
1. Takes a url
2. Verifies the format of the url, or returns "url is invalid"
3. Verifies if the url is reachable
4. returns a dictionary containing info about validity of url, status code, custom message, and the url itself
'''

import validators as v
import requests
import whitelist
import urllib.parse
import ipaddress
import sys

# Checks the status of the website linked to the url
def check_status(scode,url):
        if scode in range(200, 400):
            return {
                    "valid" : True,
                    "status_code" : scode,
                    "message" : "Page is valid",
                    "url" : url
                    }
        
        elif scode == 403:
            return {"valid" : False,
                    "status_code" : scode,
                    "message" :"No Permission to access this page",
                    "url" : url
                    }
        
        elif scode == 404:
            return {"valid" : False,
                    "status_code" : scode,
                    "message" : "Page not found",
                    "url" : url
                    }
        
        elif scode == 500:
            return {"valid" : False,
                    "status_code" : scode,
                    "message" : "Internal Server error",
                    "url" : url
                    }
        
        elif scode == 503:
            return {"valid" : False,
                    "status_code" : scode,
                    "message" : "Server is down or overloaded",
                    "url" : url
                    }
        
        else:
            return {"valid": False,
                    "status_code": scode,
                    "message" : "Unhandled status code",
                    "url" : url
                    }

# Checks if the give url has valid format or not.
def subfunc_linkformat_check(url):
        try:
            parsed = urllib.parse.urlparse(url)
            
            if parsed.scheme not in ("http", "https"):
                    return False
            if not parsed.hostname:
                    return False
            try:
                ip = ipaddress.ip_address(parsed.hostname)
                if ip.is_private or ip.is_loopback or ip.is_reserved:
                    return False
            except ValueError:
                pass # not an ip address so its skipped
            return True
        except Exception:
            return False
        
# Checks if the input given by the user is a legit website or not
def Linkgate(url):
    if subfunc_linkformat_check(url):
        if whitelist.whitelisted_sites(url):
            print("This website is well-known and trusted. No need to worry, you're good to go!")
            sys.exit(0)
        
        else:
            if not url.startswith(("https://", "http://")):        #Todo: Check if the site supports https OR https
                url = "https://" + url

            if v.url(url):
                header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"}
                try:
                    r = requests.head(url, headers=header, timeout=5)
                    response = r.status_code
                    return check_status(response, url)

                except requests.exceptions.RequestException:
                    try:
                        r = requests.get(url, headers=header, timeout=5)
                        response = r.status_code
                        return check_status(response, url)

                    except requests.exceptions.RequestException:
                        return "Failed to connect to the website"              
            else:
                return {
                    "valid": False,
                    "status_code": None,
                    "message": "Unknown failure",
                    "url": url}
    else:
        return 


if __name__ == "__main__":
     url = input("Enter a URL: ")
     print(Linkgate(url))


# TODO: Improve subfunc_linkformat_check pre-validation
# - Reject non-ASCII hostnames early (regex check) OR handle IDN via idna.encode()
# - Validate TLD against IANA list (https://data.iana.org/TLD/tlds-alpha-by-domain.txt)
#   Reject unknown/reserved TLDs
# - Reject reserved/private/loopback/multicast IPs before connect
# - Strictly allow only http/https schemes
# - (Optional) Normalize punycode domains and handle encoding errors
