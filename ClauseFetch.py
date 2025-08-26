'''
What this function does:
1. Gets the filtered url from linkgate
2. Check if the link is valid (from the dictionary that is returned by linkgate)
3. If its valid, extract all the stuff that matters (Terms and Conditions, Cookies, and whatever there is)
4. Parse it and return it as readable text.
'''

import requests as r
from bs4 import BeautifulSoup as b
import regex as re
import urllib.parse as up
from Linkgate import linkgate as lg

header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
    }

terms_fragments =[
    # Agreement and acceptance phrases
    "terms of service", "terms and conditions", "user agreement", "service agreement",
    "by using", "by accessing", "by visiting", "you agree", "you accept", "you acknowledge",
    "agreement", "accept", "acceptance", "binding", "bound", "constitute",
    
    # Legal and liability terms
    "liability", "limitation of liability", "disclaimer", "warranty", "warranties",
    "damages", "indemnify", "indemnification", "hold harmless", "at your own risk",
    "disclaim", "exclude", "limit", "maximum extent", "fullest extent",
    
    # Rights and restrictions
    "rights", "reserve the right", "intellectual property", "proprietary", "copyright",
    "trademark", "license", "permitted", "prohibited", "restricted", "violation",
    "infringement", "unauthorized", "modify", "distribute", "reproduce",
    
    # Service and usage terms
    "service", "services", "website", "platform", "content", "materials",
    "user", "users", "account", "registration", "access", "available",
    "suspend", "terminate", "termination", "discontinue", "modify",
    
    # Privacy and data
    "privacy", "privacy policy", "personal information", "data", "collect",
    "information", "cookies", "tracking", "third party", "share", "disclose",
    
    # Payment and financial terms
    "payment", "fees", "charges", "billing", "subscription", "refund",
    "purchase", "transaction", "price", "cost", "currency",
    
    # Legal jurisdiction and disputes
    "governing law", "jurisdiction", "dispute", "arbitration", "court",
    "legal", "laws", "regulations", "compliance", "enforce", "enforcement",
    
    # Changes and updates
    "changes", "modifications", "updates", "revisions", "notice", "notification",
    "effective date", "last updated", "from time to time", "sole discretion",
    
    # Common legal phrases
    "as is", "as available", "without warranty", "may not", "shall not",
    "responsible", "responsibility", "obligation", "requirements", "conditions",
    "subject to", "in accordance with", "breach", "violation", "compliance"
]


# Helper function 1 to check if Terms and Conditions are in the current page:
def tac_in_page(tac):
    for i in tac.splitlines():
        if any(fragment in i.lower() for fragment in terms_fragments):
            return {
                "success": True,
                "found_in_page": True,
                "found_in_links": False,
                "content": tac,
                "links": None,
                "error": None
            }
    
    return {
        "success": False,
        "found_in_page": False,
        "found_in_links": False,
        "content": None,
        "links": None,
        "error": None
    }

#Helper function 2 if Terms and Conditions are not in the current page (search for links)
def tac_notin_page(soup, base_url):
    links = []
    keywords = ["terms", "conditions", "policy", "legal", "privacy"]

    for a in soup.find_all('a', href=True):
        href = a['href']
        if any(keyword.lower() in href.lower() for keyword in keywords):
            full_url = up.urljoin(base_url, href)
            links.append(full_url)

    if links:
        return {
            "success": False,
            "found_in_page": False,
            "found_in_links": True,
            "content": None,
            "links": links,
            "error": None
        }
    else:
        return {
            "success": False,
            "found_in_page": False,
            "found_in_links": False,
            "content": None,
            "links": None,
            "error": None
        }


# Main function starts here
def Clausefetch(url):
    # Checks the URL again just in case
    try:
        response = r.get(url, headers= header, timeout= 10)
    except r.exceptions.RequestException:
        return {
                "success": False,
                "found_in_page": False,
                "found_in_links": False,
                "content": None,
                "links": None,
                "error": "Connection error while trying to fetch URL"
                }

    # Gets the text and whatever out of the url
    soup = b(response.text, 'lxml')
    tac = soup.text

    idkwhattonamevariablesatthispoint = tac_in_page(tac)
    helpmeplease = tac_notin_page(soup, url)

    # If the page contains the T&Cs
    if idkwhattonamevariablesatthispoint["success"]:
        return {
                "success": True,
                "found_in_page": True,
                "found_in_links": False,
                "content": idkwhattonamevariablesatthispoint["content"],
                "links": None,
                "error": None
                }
    
    # If the page doesn't contain the T&Cs
    elif not idkwhattonamevariablesatthispoint["success"]:
        final_links = []
        if helpmeplease["found_in_links"]:
            links = helpmeplease["links"]
            for l in links:
                if "www." not in l:
                    final_links.append(l.replace("://", "://www."))
                else:
                    final_links.append(l)
        
            # Links extraction done, now time to extract the stuff from it
            text = []  
            for link in final_links:
                print(f"Checking link: {link}")
                try:
                    response2 = r.get(link, headers= header, timeout= 5)
                    print(f"Successfully fetched {link}, status: {response2.status_code}")
                except r.exceptions.RequestException:
                    continue
                soup2 = b(response2.text, "lxml")
                tac_final = soup2.text
                
                if tac_in_page(tac_final)["success"]:
                    text.append(tac_in_page(tac_final)["content"])

            return text


if __name__ == "__main__":
    print(Clausefetch("https://www.fitgirlrepacks.org"))