"""
Analyze Terms & Conditions text to detect potential risks and provide safety scoring.

Goals:
- Use spaCy to preprocess input text by splitting it into sentences and filtering out
  stop words and punctuation for clean pattern matching.
- Detect risky legal clauses by applying regex patterns to the cleaned text.
- Map detected risks back to their original sentences for meaningful context.
- Calculate an overall safety rating (1-10) based on severity and number of risks found.
- Generate a human-readable recommendation (ex: accept, proceed with caution, reject).
- Return structured results including suspicious clauses, safety rating, and recommendation
  for integration with the caching and storage layers of the ReadBeforeDoom project.

  A very rough pseudo code for what im doing here:

  function textsifter(tctxt):
 Step 1: Use spaCy to split text into sentences
    sentences = spacy_split_into_sentences(text)
    
 Step 2: Clean and preprocess text     
    cleaned_text = preprocess_text(text)  # lowercase, remove stop words/punctuation
    
 Step 3: Define risk patterns (regex) for detection
    risk_patterns = {
        "data_collection": "regex_pattern_1",
        "liability_clause": "regex_pattern_2",
        "change_clause": "regex_pattern_3",
         ... more patterns ...
    }

    risks_found = {}
    
 Step 4: Search cleaned_text for each pattern
    for category, pattern in risk_patterns:
        if match found:
            risks_found[category] = matched phrases / sentences
    
 Step 5: Map each found risk to the sentence(s) containing it
    suspicious_clauses = []
    for sentence in sentences:
        for risk in risks_found:
            if sentence contains that risk pattern:
                suspicious_clauses.append(sentence)
    
 Step 6: Calculate safety score from risks_found
    safety_score = calculate_score(risks_found)
    
 Step 7: Generate recommendation based on score
    recommendation = generate_recommendation(safety_score)
    
 Step 8: Return final analysis dictionary
    return {
        'suspicious_clauses': suspicious_clauses,
        'safety_rating': safety_score,
        'recommendation': recommendation,
    }

"""

import spacy as s


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


def textsifter(txt : str):
    cleantxt = text_preprocessor(txt)
    
    




if __name__ == "__main__":
    from ClauseFetch import Clausefetch as cf
    text = cf("https://en.wikipedia.org/wiki/William_C._Brennan") 
    print(text_preprocessor(text["content"]))