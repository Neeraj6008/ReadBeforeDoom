# ReadBeforeDoom

## A Python program to analyze Terms & Conditions so you don't fall prey to corporate legal loopholes.

### The Problem

We've all done it - clicking "I Agree" without reading those impossibly long Terms & Conditions. After all, who has time to read 47 pages of legal jargon just to use a website? But sometimes, that lazy click can have serious consequences.

Consider the Disney+ arbitration case: when a man attempted to sue Disney after his wife's death from food allergies at a Disney resort, the company argued he had waived his right to a trial by accepting their streaming service's terms. Buried in those terms was an arbitration clause that prevented him from even taking them to court. This is exactly the kind of critical information hidden in agreements that users never read.

### The Solution

ReadBeforeDoom is a Python tool that actually reads Terms & Conditions for you. It scrapes websites, analyzes their legal agreements, and identifies potentially problematic clauses and suggests you about continuing or not.
Features
* Automated T&C extraction from websites
* Analysis of legal terms for concerning clauses
* Clear, actionable summaries of what you're agreeing to
* Modular architecture designed for future expansion

## How to install:
* Clone the repo to your device using `git clone https://github.com/Neeraj6008/readbeforeDoom`
* move to the repo's directory: `cd readbeforedoom`
* run `pip -r requirements.txt` to install the dependencies

And you are good to go!

## How to use
- run `python main.py` in RBD's directory
- Accept or reject the disclaimer (will exit the program if rejected)
- paste the link of the website you want to check
- Result

## Tech Stack
- **Python 3.13+**
- Web scraping: `requests`, `BeautifulSoup4`, `urllib`
- Data storage: `sqlite`
- Security: `hashlib`
- NLP: `Regex`
- Network: `dns`, `ipaddress`, `idna`

## Future Plans

The current program is still in like version 1 and needs a lot of working, such as:
* enabling to be able to work for dynamic pages
* Improving the NLP
* Making the suggestions better and detailed

And after I make the above changes, I will work on turning this small program into:
* A browser extension for real-time T&C analysis
* A full-featured application with enhanced analysis capabilities
* Integration with additional legal document types

## DISCLAIMER:
ReadBeforeDoom is an experimental tool designed to help identify potentially concerning clauses in Terms & Conditions. However:
* This is NOT legal advice and should not be treated as such
* The analysis may be incomplete, inaccurate, or outdated
* You are solely responsible for any decisions made based on this tool's output
* The author accepts ZERO liability for any losses, damages, or legal issues arising from use of this software
* Always consult a qualified legal professional for actual legal advice

By using this tool, you accept full responsibility for your actions and agree that the author bears no liability whatsoever.
