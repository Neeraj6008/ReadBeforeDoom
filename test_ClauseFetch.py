from ClauseFetch import tac_notin_page as tnip
import requests
import bs4
r = requests.get("https://www.fitgirlrepacks.org")
soup = bs4.BeautifulSoup(r.text, 'lxml')

print(tnip(soup, "https://www.fitgirlrepacks.org"))