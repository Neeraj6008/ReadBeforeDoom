import spacy as s
import re

# The following is the list of risk patterns that I will search in the text (and hopefully succeed)
risk_patterns = {
    'data_collection': r'(collect|store|process|gather|track).*(personal|data|information)',
    'third_party_sharing': r'(share|disclose|transfer|provide).*(third.?party|partner|affiliate)',
    'liability_disclaimer': r'(not liable|disclaim|exclude|limit liability|no responsibility)',
    'unilateral_changes': r'(modify|change|alter|update).*(without notice|at any time|sole discretion)',
    'broad_permissions': r'(any purpose|unlimited|perpetual|irrevocable)',
    'content_rights': r'(license|grant|assign).*(content|material|intellectual property)'
}

# Cleans and unclutters text for easier processing it using textsifter.
def text_preprocessor(txt: str):
    try:
        # Load the English model
        nlpobject = s.load('en_core_web_sm')

        # Process the text
        doc = nlpobject(txt)

        # Convert the text into sentences to make clause searching easier
        sentences = [sent.text.strip() for sent in doc.sents]

        # Clean the text sentence-by-sentence
        cleaned_sent = []
        for snt in sentences:
            # Fixed: Proper condition check - keep sentences longer than 10 characters
            if len(snt.strip()) > 10 and snt.strip():
                cleaned_sent.append(snt.strip())  # Keep original case for better matching

        return {"cleaned_stuff": cleaned_sent}

    except OSError:
        print("Warning: spaCy model not found. Using basic sentence splitting.")
        # Fallback to simple sentence splitting
        sentences = re.split(r'[.!?]+', txt)
        cleaned_sent = [s.strip() for s in sentences if len(s.strip()) > 10]
        return {"cleaned_stuff": cleaned_sent}

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
