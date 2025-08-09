'''
What this function does:
1. Gets the filtered url from linkgate
2. Check if the link is valid (from the dictionary that is returned by linkgate)
3. If its valid, extract all the stuff that matters (Terms and Conditions, Cookies, and whatever there is)
4. Parse it and return it as readable text.
'''
import Linkgate

def ClauseFetch(url):
    x = Linkgate.linkgate(url)

    if x['valid']:
        #Will start after learning about requests beautifulsoup regular expressions and other stuff
        return "Fetching and parsing Terms and Conditions is not yet implemented."
    else:
        return f"Invalid URL or unable to fetch data. Status Code: {x.get('status_code', 'N/A')}, Message: {x.get('message', 'No message provided')}"
    

if __name__ == "__main__":
    print(ClauseFetch("https://www.openai.com"))