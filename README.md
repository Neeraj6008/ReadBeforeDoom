# ReadBeforeDoom

*Don't get trapped by Terms & Conditions. Analyze before you agree.*

## Overview

**ReadBeforeDoom** is a Python-based tool that automatically extracts and analyzes Terms & Conditions from websites using Natural Language Processing (NLP) and Machine Learning. Instead of manually reading lengthy T&C documents, ReadBeforeDoom flags potentially problematic clauses, helping users make informed decisions about which services to trust.

## The Problem

We all know that _almost_ no one reads those kilometers long lines of Terms and Conditions because:
- **They're too long (which I think was intentional)**: Average T&C is 2,000-3,000 words
- **They're complex**: Written in legal jargon
- **They're constantly changing**: Updates go unnoticed

Yet buried in these documents are clauses about data usage, automatic charges, liability waivers, and privacy violations that directly affect you.

## The Solution

ReadBeforeDoom automates this process. It:
- **Extracts T&C text** from websites (both static and dynamic pages)
- **Analyzes each clause** using NLP/ML to identify suspicious language
- **Flags risks** with severity ratings (Low/Medium/High/Critical)
- **Caches results** so you only analyze each site once
- **Runs locally** - no cloud storage, no tracking

## Key Features

- **Dynamic Page Support**: Uses browser automation for JavaScript-heavy sites (most modern websites)
- **Smart Caching**: SQLite database stores analyzed results with URL hashing for fast lookups
- **ML-Powered Detection**: Identifies problematic clauses beyond simple keyword matching
- **Clause Classification**: Categorizes risks (payment terms, data usage, dispute resolution, liability)
- **User-Friendly Output**: Clear, color-coded results showing exactly what to worry about

## Tech Stack

- **Backend**: Python 3.14+
- **NLP**: Hugging Face Transformers (spaCy → Transformers migration for Python 3.14 compatibility)
- **Web Scraping**: Selenium (for dynamic content), BeautifulSoup (for parsing)
- **Database**: SQLite (portable, no external dependencies)
- **Architecture**: Modular design with OOP principles (TextSifter, ClauseFetch, Linkgate, Database modules)

## Installation

### Prerequisites
- Python 3.14+
- pip (Python package manager)

### Setup
- Clone the repository: `git clone https://github.com/Neeraj6008/ReadBeforeDoom.git`
  
- move to the directory: `cd ReadBeforeDoom`
  
- Install dependencies: `pip install -r requirements.txt`
  
- Run the application: `python main.py`
