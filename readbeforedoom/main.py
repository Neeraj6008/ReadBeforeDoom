from readbeforedoom.Linkgate import linkgate
from readbeforedoom.ClauseFetch import Clausefetch
from readbeforedoom.textsifter import textsifter
from readbeforedoom.Database import sql_cache_check, store_analysis_result


def show_disclaimer():
    """Display disclaimer and get user acceptance."""
    separator = "=" * 70
    print(separator)
    print("READBEFOREDOOM DISCLAIMER")
    print(separator)
    print(
        "By using this program, you accept that if you make decisions based on the results, and it is harmful to you, I am NOT liable for it."
    )
    print("This program is in VERSION 0 and may have false positives/errors.")
    print(separator)
    while True:
        print("\nDo you accept these terms? (Type 'accept' or 'reject')")
        choice = input("Your choice: ").strip().lower()
        if choice in ["accept", "a", "yes", "y"]:
            print("\nTerms accepted! Welcome to ReadBeforeDoom!")
            print("Let's analyze some Terms & Conditions!\n")
            return True
        elif choice in ["reject", "r", "no", "n"]:
            print("\n❌ Terms rejected.\nGoodbye!")
            return False
        else:
            print("Please type 'accept' or 'reject'")


def check_terms_and_conditions(url):
    print(f"Analyzing website: {url}")
    print("Checking database for previous analysis...")
    cache_result = sql_cache_check(url)
    if cache_result["link_in_db"]:
        print("Found previous analysis in database!")
        return {
            "url": url,
            "from_cache": True,
            "safety_rating": cache_result["safety_rating"],
            "recommendation": cache_result["recommendation"],
            "suspicious_clauses": cache_result["suspicious_clauses"],
        }
    print("Validating URL...")
    url_check = linkgate(url)
    if not url_check["valid"]:
        return {"url": url, "error": f"Invalid URL: {url_check['message']}"}
    verified_url = url_check["url"]
    print(f"URL is valid: {verified_url}")
    print("Looking for Terms & Conditions on website...")
    tc_result = Clausefetch(verified_url)  # type: ignore
    if not tc_result["success"]:
        return {
            "url": verified_url,
            "error": f"Could not find Terms & Conditions: {tc_result.get('error', 'Unknown error')}",
        }
    tc_text = ""
    if tc_result["found_in_page"]:
        tc_text = tc_result["content"]
        print("Found Terms & Conditions on main page")
    elif tc_result["found_in_links"]:
        content = tc_result["content"]
        if isinstance(content, list) and content:
            tc_text = content["content"]  # type: ignore
            print(f"Found Terms & Conditions in linked page: {content['url']}")  # type: ignore
        else:
            tc_text = str(content)
            print("Found Terms & Conditions in linked pages")
    if not tc_text or len(tc_text) < 100:
        return {
            "url": verified_url,
            "error": "Terms & Conditions text too short or empty",
        }
    print(f"Extracted {len(tc_text)} characters of text")
    print("Analyzing text for risky phrases...")
    analysis = textsifter(tc_text)
    print("Saving results to database...")
    try:
        analysis_result = {
            "suspicious_clauses": analysis.get("suspicious_clauses", []),
            "safety_rating": analysis.get("safety_rating", "0/10"),
            "recommendation": analysis.get("recommendation", "No analysis available"),
            "risk_categories": analysis.get("risks_found", 0),
        }
        store_result = store_analysis_result(
            url=verified_url, tc_text=tc_text, analysis_result=analysis_result
        )
        if store_result.get("success"):
            print("Results saved successfully!")
        else:
            print(
                f"Warning: Could not save to database: {store_result.get('message', 'Unknown error')}"
            )
    except Exception as e:
        print(f"Warning: Could not save to database: {e}")
    return {
        "url": verified_url,
        "from_cache": False,
        "safety_rating": analysis["safety_rating"],
        "recommendation": analysis["recommendation"],
        "suspicious_clauses": analysis["suspicious_clauses"][:3],
        "total_risks": analysis["risks_found"],
    }


def print_results(result):
    """Print the analysis results in formatted style."""
    print("\n" + "=" * 60)
    print("TERMS & CONDITIONS ANALYSIS RESULTS")
    print("=" * 60)
    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
        return
    print(f"Website: {result['url']}")
    print(
        "Source: Previous analysis (from database)"
        if result.get("from_cache")
        else "Source: Fresh analysis"
    )
    print(f"\nSafety Rating: {result['safety_rating']}")
    print(f"Recommendation: {result['recommendation']}")
    if result.get("total_risks", 0) > 0:
        print(f"\n found {result['total_risks']} potential risk(s)")
        print("\nSuspicious clauses found:")
        for i, clause in enumerate(result.get("suspicious_clauses", []), 1):
            display_clause = clause[:150] + "..." if len(clause) > 150 else clause
            print(f"{i}. {display_clause}")
    else:
        print("\nNo major risks detected in Terms & Conditions")
    print("\n" + "=" * 60)


def main():
    """Main interactive program."""
    if not show_disclaimer():
        return
    print("This program analyzes website Terms & Conditions for safety.\n")
    while True:
        try:
            url = input("Enter a website URL (or 'quit' to exit): ").strip()
            if url.lower() in ["quit", "exit", "q"]:
                print("Thanks for using ReadBeforeDoom!")
                break
            if not url:
                print("Please enter a valid URL.")
                continue
            result = check_terms_and_conditions(url)
            print_results(result)
        except KeyboardInterrupt:
            print("\n\nExiting program...")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}\nPlease try again with a different URL.")


def test_program():
    """Test the program with a sample URL."""
    test_url = "https://www.google.com"
    print(f"Testing with URL: {test_url}")
    result = check_terms_and_conditions(test_url)
    print_results(result)


if __name__ == "__main__":
    # Uncomment below to run a test instead of interactive mode
    # test_program()
    main()
