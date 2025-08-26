'''This is the start of the python part of the t&c analyzer that we are making for the class 12 board CS practical project.
This is just a prototype, starting with a simple CLI application which:
1. Takes a website link as an input from the user
2. Searches that website for its T&C page
3. Scans the T&C for dangerous clauses
4. Cuts all the crap and summarizer it into simple word and notifies the user about the dangers accepting it could pose.


Future Updates: Replace the CLI application to a GUI app, and in the further future convert this into a web extension that does some stuff...
'''
from Linkgate import linkgate as l
from ClauseFetch import Clausefetch as cf

def main():
    print("Welcome to the Terms and Conditions Analyzer!")
    url = input("Please enter the URL of the website you want to analyze: ")
    url_ = l(url)["url"]
    url_0 = cf(url_)
    return url_0


print(main())