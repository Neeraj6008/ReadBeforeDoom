'''
So, turns out, some websites are pretty well known, and this program can't scrape them for data (against their
Terms and Conditions, ironically).
so this function maintains a database of such sites and if the give link belongs to such site, then the program
tells the user that its safe and no need to check Terms and Conditions.
'''
whtlst_web = [
    "google.com",      "facebook.com",   "twitter.com",    "linkedin.com",   "youtube.com",   "amazon.com",
    "microsoft.com",   "apple.com",      "openai.com",     "github.com",     "wikipedia.org", "reddit.com",
    "instagram.com",   "paypal.com",     "stackoverflow.com","netflix.com",  "dropbox.com",  "mozilla.org",
    "etsy.com",        "salesforce.com", "zoom.us",        "airbnb.com",     "spotify.com",  "slack.com",
    "tumblr.com",      "quora.com",      "bbc.com",        "cnn.com",        "nytimes.com",  "imdb.com",
    "medium.com",      "adobe.com",      "nasa.gov",       "shopify.com",    "stripe.com"
            ]


def whitelisted_sites(url):
    if url.replace("https://", '').replace("http://", '').replace("www.", '').rstrip('/') in whtlst_web:
        return True
    else:
        return False