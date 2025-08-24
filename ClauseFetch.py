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

terms_fragments = [
    "by using this service", "by accessing this website", "you agree to",
    "you hereby agree to be bound by", "limitation of liability", "to the fullest extent permitted by law",
    "we reserve the right to", "without prior notice", "indemnify and hold harmless",
    "governing law", "these terms constitute the entire agreement", "modification of terms"
]

# Helper function 1 to check if Terms and Conditions are in the current page:
def tac_in_page(tac):
    for line in tac.splitlines():
        if any(fragment in line.lower() for fragment in terms_fragments):
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
            "found_in_links": False,
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
    try:
        response = r.get(url)
    except r.exceptions.RequestException:
        return {
                "success": False,
                "found_in_page": False,
                "found_in_links": False,
                "content": None,
                "links": None,
                "error": "Connection error while trying to fetch URL"
                }

    soup = b(response.text, 'lxml')
    tac = soup.text

    idkwhattonamevariablesatthispoint = tac_in_page(tac)
    helpmeplease = tac_notin_page(soup)

    if idkwhattonamevariablesatthispoint["tacinpage"]:
        return {
                "success": True,
                "found_in_page": True,
                "found_in_links": False,
                "content": idkwhattonamevariablesatthispoint["content"],
                "links": None,
                "error": None
                }

    elif helpmeplease:
        return {
                "success": False,
                "found_in_page": False,
                "found_in_links": False,
                "content": None,
                "links": helpmeplease["links"],
                "error": None
                }

    else:
        return False


# TODO:
# 1. Implement recursive or iterative fetching of candidate links found by tac_notin_page
#    to check those pages for Terms and Conditions content.
#    - Limit depth or max number of links checked to avoid excessive crawling.
# 2. Ensure Clausefetch returns consistent dictionary format in all cases,
#    including when neither T&Cs nor candidate links are found (avoid returning False).
# 3. (Optional) Add more detailed error handling for other exceptions or parse errors.


if __name__ == "__main__":
    Clausefetch("https://www.fitgirlrepacks.org")