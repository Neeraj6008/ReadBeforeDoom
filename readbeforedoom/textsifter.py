import re
import json
import os


# Cleans and unclutters text for easier processing it using textsifter
def text_preprocessor(txt: str):
    """
    Split text into sentences using regex
    Fast, reliable, zero dependencies
    """
    # Split on periods, exclamation marks, question marks
    sentences = re.split(r'[.!?]+', txt)
    
    # Filter out short sentences (likely noise/fragments)
    cleaned_sent = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    return {"cleaned_stuff": cleaned_sent}



def load_risk_patterns(): # Gets the risk patterns from risk_patterns.json

    pattern_file = os.path.join(os.path.dirname(__file__), 'risk_patterns.json')
    
    try:
        with open(pattern_file, 'r') as f:
            data = json.load(f)
            # Extracting just the regex patterns for backward compatibility
            return {
                category: info['regex'] 
                for category, info in data['patterns'].items()
            }

    except FileNotFoundError:
        print("Warning: risk_patterns.json not found. Using default patterns (less accurate obv)")

        return {
            'data_collection': r'(collect|store|process|gather|track).*(personal|data|information)',
            'third_party_sharing': r'(share|disclose|transfer|provide).*(third.?party|partner|affiliate)',
        }

risk_patterns = load_risk_patterns()


# Risk checker:
def risk_analysis(risks_found_list: list):
    risk_count = len(risks_found_list)

    # Calculate safety score based on number of risks
    if risk_count >= 5:
        safety_score = 2
    elif risk_count >= 3:
        safety_score = 4
    elif risk_count >= 2:
        safety_score = 6
    elif risk_count >= 1:
        safety_score = 7
    else:
        safety_score = 9

    # Generate recommendation based on safety score
    if safety_score >= 8:
        recommendation = "The T&Cs look fine, you can continue..."
    elif safety_score >= 6:
        recommendation = "Proceed with caution"
    else:
        recommendation = "High risk - consider alternatives"

    return {
        "safety_score": f"{safety_score}/10",
        "recommendation": recommendation,
        "risk_count": risk_count
    }

def textsifter(txt: str):
    if not txt or len(txt.strip()) < 50:
        return {
            'suspicious_clauses': [],
            'safety_rating': "0/10",
            'recommendation': "No content to analyze",
            'risks_found': 0
        }

    # Preprocess the text
    processed_data = text_preprocessor(txt)
    cleantxt = processed_data["cleaned_stuff"]  # This is a List of sentences

    # The for Loop that checks for the risks starts from here:
    risks_found = []
    sus_clauses = []

    for sent in cleantxt:
        for risk_category, pattern in risk_patterns.items():
            match = re.search(pattern, sent, re.IGNORECASE)
            if match:
                risks_found.append(risk_category)
                sus_clauses.append(sent)
                break  # Only count one risk per sentence

    # Remove duplicates while preserving order
    unique_risks = []
    unique_clauses = []
    seen_risks = set()

    for i, risk in enumerate(risks_found):
        if risk not in seen_risks:
            unique_risks.append(risk)
            unique_clauses.append(sus_clauses[i])
            seen_risks.add(risk)

    # Calculate the safety score
    ra = risk_analysis(unique_risks)

    return {
        'suspicious_clauses': unique_clauses[:5],  # Limit to top 5
        'safety_rating': ra["safety_score"],
        'recommendation': ra["recommendation"],
        'risks_found': ra["risk_count"]
    }

if __name__ == "__main__":
    print("Enter Text below:")
    text = input()
    result = textsifter(text)
    print("\nAnalysis Result:")
    for key, value in result.items():
        print(f"{key}: {value}")
