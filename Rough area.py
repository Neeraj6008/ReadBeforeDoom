import requests

print(requests.get("https://data.iana.org/TLD/tlds-alpha-by-domain.txt", timeout=5).text.split())
