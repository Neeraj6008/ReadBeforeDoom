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
def text_preprocessor(txt : str):

    # this is like a language processing machine for text, it loads the english model
    nlpobject = s.load('en_core_web_sm')

    # doc is a container that store the text from the T&Cs
    doc = nlpobject(txt)
    
    
    # Converts the text into sentences to make clause searching easier
    sentences = [sent.text.strip() for sent in doc.sents]

    #Time to clean the text sentence-by-sentence:
    # TODO: convert to lowercase, remove stopwords and punctutations
    
    cleaned_sent = []
    for snt in sentences:
        if snt.isalnum:
            cleaned_sent.append(snt.lower())
    
    return {"cleaned stuff" : cleaned_sent}

# Risk checker:
def risk_analysis(risklen : list):
    score_initial = 10
    risk_count = len(risklen)

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
    # omg I didn't expect long lines of if-elif blocks to only be used like one time?!?!?!


    if safety_score >= 8:
        recommendation = "The T&Cs look fine, you can continue..."
    
    elif 8 > safety_score >= 6:
        recommendation = "Proceed with caution"

    else:
        recommendation = "At this point ur just walking into a rattrap bruhh"

    return {
        "safety score" : f"{safety_score}/10",
        "recommendation" : recommendation,
        "risk count" : risk_count
    }


def textsifter(txt : str):

    cleantxt = text_preprocessor(txt)["cleaned stuff"]  # NOTE: This is a List of sentences


    # The for Loop that checks for the risks starts from here:
    risks_found = []
    sus_clauses = []
    
    for sent in cleantxt:
        for risk_category, pattern in risk_patterns.items():
            match = re.search(pattern, sent, re.IGNORECASE)
            if match:
                risks_found.append(risk_category)
                sus_clauses.append(sent)
                break
    

    # Calculates the safety score (from 1 to 10)
    ra = risk_analysis(risks_found)


    return {
            'suspicious_clauses': sus_clauses[:5],  # Limit to top 5
            'safety_rating': ra["safety score"],
            'recommendation': ra["recommendation"],
            'risks_found': ra["risk count"]
        }

if __name__ == "__main__":
    print("enter Text below:")
    text = input()
    print(textsifter(text))