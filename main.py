"""
ReadBeforeDoom - Terms & Conditions Risk Analysis System

Main integration module that combines all components of the ReadBeforeDoom project
to provide comprehensive analysis of website Terms & Conditions for potential risks.

This module serves as the primary entry point and orchestrates the complete pipeline:
1. URL validation and sanitization (linkgate module)
2. Terms & Conditions text extraction (clausefetch module) 
3. Natural language processing and risk detection (textsifter module)
4. Hash-based caching for performance optimization
5. Database storage and retrieval of analysis results
6. User-friendly risk scoring and recommendations

Components Integrated:
---------------------
- Linkgate.py: URL validation and safety checks
- ClauseFetch.py: Web scraping and T&C text extraction  
- textsifter.py: spaCy/regex-based risk pattern detection
- Database.py: SQLite storage with hash-based caching
- Risk scoring: 1-10 safety rating system
- Recommendation engine: User-friendly guidance

Main Functions:
--------------
- process_url_complete(): End-to-end pipeline from URL to final recommendation
- validate_and_extract(): URL processing and text extraction
- analyze_and_score(): Risk analysis and safety rating calculation
- cache_and_store(): Database operations and caching management

Usage:
------
Run as standalone script or import functions for integration with web interfaces.
Designed for educational demonstration of NLP, web scraping, and database concepts.

Example Output:
--------------
{
    'url': 'https://example.com/terms',
    'safety_rating': '4/10',
    'recommendation': 'High risk - consider alternatives',
    'suspicious_clauses': ['We collect personal data...', 'Company not liable...'],
    'risks_found': 3
}

Author: [Your Name]
Project: ReadBeforeDoom - CS Project
Timeline: Completed under pressure in final weeks before half-yearly exams
"""

# Import all the modules we created
from Linkgate import linkgate
from ClauseFetch import Clausefetch  
from textsifter import textsifter
from Database import sql_cache_check, store_analysis_result

def show_disclaimer():
    """
    Shows disclaimer and gets user acceptance before running the program.
    Returns True if accepted, False if rejected.
    """
    print("=" * 70)
    print("🛡️  READBEFOREDOOM DISCLAIMER")
    print("=" * 70)
    print()
    print("📋 LEGAL NOTICE:")
    print("By using this program, you accept that if you make your decisions")
    print("based on the results of this program, and it turns out to be harmful")
    print("to you in any way, I am NOT liable for it.")
    print()
    print("⚠️  VERSION WARNING:")
    print("This program is still in VERSION 0, and there WILL be some false")
    print("positives and errors, so mind you.")
    print()
    print("😄 META-IRONY ALERT:")
    print("It would be ironic if the above stuff ends up sounding like those")
    print("general long-ass Terms & Conditions we're trying to protect you from, right?")
    print()
    print("=" * 70)
    
    while True:
        print("\nDo you accept these terms? (Type 'accept' or 'reject')")
        choice = input("👉 Your choice: ").strip().lower()
        
        if choice in ['accept', 'a', 'yes', 'y']:
            print("\n✅ Terms accepted! Welcome to ReadBeforeDoom!")
            print("🚀 Let's analyze some Terms & Conditions!\n")
            return True
        elif choice in ['reject', 'r', 'no', 'n']:
            print("\n❌ Terms rejected.")
            print("🏃‍♂️ Thanks for considering ReadBeforeDoom. Goodbye!")
            return False
        else:
            print("❓ Please type 'accept' or 'reject'")

def check_terms_and_conditions(url):
    """
    Main function that checks a website's Terms & Conditions for safety.
    
    Takes a website URL and returns safety analysis results.
    """
    
    print(f"Analyzing website: {url}")
    
    # Step 1: Check if we already analyzed this URL before
    print("Checking database for previous analysis...")
    cache_result = sql_cache_check(url)
    
    if cache_result['link_in_db']:
        print("Found previous analysis in database!")
        return {
            'url': url,
            'from_cache': True,
            'safety_rating': cache_result['safety_rating'],
            'recommendation': cache_result['recommendation'],
            'suspicious_clauses': cache_result['suspicious_clauses']
        }
    
    # Step 2: Validate the URL 
    print("Validating URL...")
    url_check = linkgate(url)
    
    if not url_check['valid']:
        return {
            'url': url,
            'error': f"Invalid URL: {url_check['message']}"
        }
    
    verified_url = url_check['url']
    print(f"URL is valid: {verified_url}")
    
    # Step 3: Extract Terms & Conditions text
    print("Looking for Terms & Conditions on website...")
    tc_result = Clausefetch(verified_url) # type: ignore
    
    if not tc_result['success']:
        return {
            'url': verified_url,
            'error': f"Could not find Terms & Conditions: {tc_result.get('error', 'Unknown error')}"
        }
    
    # Get the text content
    tc_text = ""
    if tc_result['found_in_page']:
        tc_text = tc_result['content']
        print("Found Terms & Conditions on main page")
    elif tc_result['found_in_links']:
        content = tc_result['content']
        if isinstance(content, list) and content:
            tc_text = content[0]['content']
            print(f"Found Terms & Conditions in linked page: {content[0]['url']}")
        else:
            tc_text = str(content)
            print("Found Terms & Conditions in linked pages")
    
    if not tc_text or len(tc_text) < 100:
        return {
            'url': verified_url,
            'error': "Terms & Conditions text too short or empty"
        }
    
    print(f"Extracted {len(tc_text)} characters of text")
    
    # Step 4: Analyze the text for risks
    print("Analyzing text for risky phrases...")
    analysis = textsifter(tc_text)
    
    # Step 5: Save results to database
    print("Saving results to database...")
    try:
        store_analysis_result(
            url=verified_url,
            tc_text=tc_text,
            analysis_result={
                'suspicious_clauses': str(analysis['suspicious_clauses']),
                'safety_rating': analysis['safety_rating'],
                'recommendation': analysis['recommendation'],
                'risk_categories': str(analysis['risks_found'])
            }
        )
        print("Results saved successfully!")
    except Exception as e:
        print(f"Warning: Could not save to database: {e}")
    
    # Step 6: Return final results
    return {
        'url': verified_url,
        'from_cache': False,
        'safety_rating': analysis['safety_rating'],
        'recommendation': analysis['recommendation'],
        'suspicious_clauses': analysis['suspicious_clauses'][:3],  # Show top 3
        'total_risks': analysis['risks_found']
    }

def print_results(result):
    """
    Prints the analysis results in a nice format for the user.
    """
    print("\n" + "="*60)
    print("TERMS & CONDITIONS ANALYSIS RESULTS")
    print("="*60)
    
    if 'error' in result:
        print(f"❌ ERROR: {result['error']}")
        return
    
    print(f"Website: {result['url']}")
    
    if result.get('from_cache'):
        print("📋 Source: Previous analysis (from database)")
    else:
        print("🔍 Source: Fresh analysis")
    
    print(f"\n🛡️  Safety Rating: {result['safety_rating']}")
    print(f"💡 Recommendation: {result['recommendation']}")
    
    if result.get('total_risks', 0) > 0:
        print(f"\n⚠️  Found {result['total_risks']} potential risk(s)")
        print("\nSuspicious clauses found:")
        for i, clause in enumerate(result.get('suspicious_clauses', []), 1):
            # Limit clause length for display
            display_clause = clause[:150] + "..." if len(clause) > 150 else clause
            print(f"{i}. {display_clause}")
    else:
        print("\n✅ No major risks detected in Terms & Conditions")
    
    print("\n" + "="*60)

def main():
    """
    Main program with disclaimer check.
    """
    # Show disclaimer first
    if not show_disclaimer():
        return  # Exit if user rejects
    
    print("This program analyzes website Terms & Conditions for safety.")
    print()
    
    while True:
        try:
            # Get URL from user
            url = input("Enter a website URL (or 'quit' to exit): ").strip()
            
            if url.lower() in ['quit', 'exit', 'q']:
                print("Thanks for using ReadBeforeDoom!")
                break
            
            if not url:
                print("Please enter a valid URL.")
                continue
            
            # Analyze the URL
            result = check_terms_and_conditions(url)
            
            # Show results
            print_results(result)
            
        except KeyboardInterrupt:
            print("\n\nExiting program...")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            print("Please try again with a different URL.")

# Test function for development
def test_program():
    """
    Test the program with a sample URL.
    """
    test_url = "https://www.google.com"
    print(f"Testing with URL: {test_url}")
    result = check_terms_and_conditions(test_url)
    print_results(result)

if __name__ == "__main__":
    # Uncomment the line below to run a test instead of interactive mode
    # test_program()
    
    # Run the main interactive program
    main()
