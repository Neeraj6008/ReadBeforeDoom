'''
What this function does:
1. Gets the filtered url from linkgate
2. Check if the link is valid (from the dictionary that is returned by linkgate)
3. If its valid, extract all the stuff that matters (Terms and Conditions, Cookies, and whatever there is)
4. Parse it and return it as readable text.
'''
import Linkgate as lg
from bs4 import BeautifulSoup as bs
import requests as req

def ClauseFetch(url):
    x = lg.Linkgate(url)  # Gets the filtered url from the url that the user inputted.

    if x['valid']:
        html = bs(req.get(x['url']).text, 'html.parser')    # Gets the stuff from the website that we need to work on.
        for a_tag in html.find_all('a', href=True):         # Finds all the links that are in the webpage
            href = a_tag['href']
            if href.lower() in ["terms", "conditions", "cookie", "privacy", "legal", "policy"]: # Identifies the link to the Terms and conditions page and returns it.
                terms_url = href if href.startswith('http') else req.compat.urljoin(x['url'], href)
                return f"Terms and Conditions found at: {terms_url}"   
    else:
        return f"Invalid URL or unable to fetch data. Status Code: {x.get('status_code', 'N/A')}, Message: {x.get('message', 'No message provided')}"
    

if __name__ == "__main__":
    print(ClauseFetch("https://www.google.com"))

# TODOs for ClauseFetch:
# *MAIN THING TO DO: LEARN EVERYTHING ABOUT STATIC WEB SCRAPING*
# 1. Add try-except for requests.get to handle errors.
# 2. Use User-Agent header and timeout.
# 3. Check response status before parsing.
# 4. Return structured dict result.
# 5. Handle case where no T&C link is found.
# 6. Skip mailto/tel.
# 7. Match keywords in href and anchor text.
# 8. Rate limit requests.
# 9. Log attempts/results.

# Future:
# - Check robots.txt before scraping.
# - Parse Terms page content.
# - Handle JS-rendered pages.
# - Add tests.
# - Improve CLI output and save JSON.
