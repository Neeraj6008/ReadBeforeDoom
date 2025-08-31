"""
ReadBeforeDoom - Terms & Conditions Risk Analysis System

Main integration module that combines all components of the ReadBeforeDoom project
to provide comprehensive analysis of website Terms & Conditions for potential risks.

This module serves as the primary entry point and orchestrates the complete pipeline:
1. URL validation and sanitization (linkgate module)
2. Terms & Conditions text extraction (clausefetch module) 
3. Natural language processing and risk detection (textmine module)
4. Hash-based caching for performance optimization
5. Database storage and retrieval of analysis results
6. User-friendly risk scoring and recommendations

Components Integrated:
---------------------
- linkgate.py: URL validation and safety checks
- clausefetch.py: Web scraping and T&C text extraction  
- textmine.py: spaCy/regex-based risk pattern detection
- Database layer: SQLite storage with hash-based caching
- Risk scoring: 1-10 safety rating system
- Recommendation engine: Very basic, if-elif block, but good enough for now

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
    'recommendation': 'At this point ur just walking into a rattrap bruhh',
    'suspicious_clauses': ['We collect personal data...', 'Company not liable...'],
    'risks_found': 3
}

Author: Neeraj
Project: ReadBeforeDoom - CS Project
Timeline: Completed under pressure in final weeks before half-yearly exams (can you imagine what it was
like when I realized the time to complete this project went from 5 months to 1 month?!!?!!? )
"""

# Import all of the lego blocks (this is so satisfying)
from Linkgate import linkgate
from ClauseFetch import Clausefetch  
from textsifter import textsifter
from Database import sql_cache_check, store_analysis_result

def check_terms_and_conditions(url):

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
    Main program that asks user for URL and shows results.
    """
    print("Welcome to ReadBeforeDoom!")
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


if __name__ == "__main__":
    main()
