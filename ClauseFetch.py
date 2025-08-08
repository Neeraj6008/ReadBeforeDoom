'''
What this function does:
1. Gets the filtered url from linkgate
2. Check if the link is valid (from the dictionary that is returned by linkgate)
3. If its valid, extract all the stuff that matters (Terms and Conditions, Cookies, and whatever there is)
4. Parse it and return it as readable text.
'''
import Linkgate

def ClauseFetch(url: str) -> str:
    x = Linkgate.linkgate(url)
    print(f"Value: {x['valid']}, Status Code: {x.get('status_code', 'N/A')}")

if __name__ == "__main__":
    print(ClauseFetch("www.openai.com"))