import validators as v
import requests

def linkgate(url):
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

    # Function to check if the input given by the user is a legit website or not
    def Check_link(url):
        if "@" in url and "." in url and not url.startswith(("http://", "https://")):
            return {"valid" : False,
                    "status_code" : None,
                    "message" : "This seems to be an email, not a URL.",
                    "url" : url
                    }

        if not url.startswith(("https://", "http://")):
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
    return Check_link(url)


if __name__ == "__main__":
    test_url = input("Enter a URL to test: ")
    result = linkgate(test_url)
    print(result)
