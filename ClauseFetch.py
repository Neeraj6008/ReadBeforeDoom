# ClauseFetch.py — static-only T&C/Privacy extractor (finalized)

import requests as r
from bs4 import BeautifulSoup as b
import re
import urllib.parse as up
from typing import List, Dict, Any, Optional


# Legal keyword fragments used for detection (disclaimer: very big)
terms_fragments = [
    "terms of service", "terms and conditions", "user agreement", "service agreement",
    "by using", "by accessing", "by visiting", "you agree", "you accept", "you acknowledge",
    "agreement", "accept", "acceptance", "binding", "bound", "constitute",
    "liability", "limitation of liability", "disclaimer", "warranty", "warranties",
    "damages", "indemnify", "indemnification", "hold harmless", "at your own risk",
    "disclaim", "exclude", "limit", "maximum extent", "fullest extent",
    "rights", "reserve the right", "intellectual property", "proprietary", "copyright",
    "trademark", "license", "permitted", "prohibited", "restricted", "violation",
    "infringement", "unauthorized", "modify", "distribute", "reproduce",
    "service", "services", "website", "platform", "content", "materials",
    "user", "users", "account", "registration", "access", "available",
    "suspend", "terminate", "termination", "discontinue", "modify",
    "privacy", "privacy policy", "personal information", "data", "collect",
    "information", "cookies", "tracking", "third party", "share", "disclose",
    "payment", "fees", "charges", "billing", "subscription", "refund",
    "purchase", "transaction", "price", "cost", "currency",
    "governing law", "jurisdiction", "dispute", "arbitration", "court",
    "legal", "laws", "regulations", "compliance", "enforce", "enforcement",
    "changes", "modifications", "updates", "revisions", "notice", "notification",
    "effective date", "last updated", "from time to time", "sole discretion",
    "as is", "as available", "without warranty", "may not", "shall not",
    "responsible", "responsibility", "obligation", "requirements", "conditions",
    "subject to", "in accordance with", "breach", "violation", "compliance",
]


def normalized_html(resp: r.Response) -> str:
    # Standardize text decoding; avoid ISO-8859-1 pitfalls common in requests
    enc = (resp.encoding or "").lower()
    if not enc or enc == "iso-8859-1":
        resp.encoding = "utf-8"
    return resp.text


def clean_text_from_html(soup: b) -> str:
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    return soup.get_text(separator="\n", strip=True)


def tac_in_page(tac: str, soup: Optional[b] = None) -> Dict[str, Any]:
    MIN_LENGTH_HINT = 600  # helps avoid tiny/irrelevant matches
    # Quick guard for clearly empty or trivial pages
    if not tac or len(tac) < MIN_LENGTH_HINT:
        return {"success": False, "content": None}

    relevant_sections: List[str] = []
    context_window = 5
    lines = [line.strip() for line in tac.splitlines() if line.strip()]

    for idx, line in enumerate(lines):
        low = line.lower()
        if any(fragment in low for fragment in terms_fragments):
            start = max(0, idx - context_window)
            end = min(len(lines), idx + context_window + 1)
            content = "\n".join(lines[start:end])

            # If we have structured HTML, prefer the immediate parent block’s text
            if soup:
                try:
                    found = soup.find(string=re.compile(re.escape(line), re.IGNORECASE))
                    if found and found.parent:
                        content = found.parent.get_text(separator="\n", strip=True)
                except Exception:
                    pass

            relevant_sections.append(content)

    if relevant_sections:
        combined = "\n\n".join(relevant_sections)
        return {"success": True, "content": combined}

    # Also try headings/title hints when body scan misses but soup exists
    if soup:
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'title'])
        for h in headings:
            txt = h.get_text().lower()
            if any(k in txt for k in ["terms", "conditions", "privacy", "policy", "legal", "agreement", "service"]):
                return {"success": True, "content": tac}

    return {"success": False, "content": None}


def find_legal_links(soup: b, base_url: str) -> List[str]:
    LEGAL_LINK_KEYWORDS = ["terms", "privacy", "policy", "disclaimer", "legal"]
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip() # type: ignore
        text = a.get_text(strip=True).lower()
        href_lower = href.lower()

        candidate = any(k in href_lower for k in LEGAL_LINK_KEYWORDS) or any(
            k in text for k in LEGAL_LINK_KEYWORDS
        )
        if not candidate:
            continue

        try:
            full = up.urljoin(base_url, href)
            parsed = up.urlparse(full)
            if parsed.scheme in ("http", "https"):
                links.add(full)
        except Exception:
            continue

    return list(links)


def guess_legal_paths(base_url: str) -> List[str]:
    # Fallback probes when the homepage shows no visible legal links
    common_paths = [
        "/privacy", "/privacy-policy", "/policies",
        "/terms", "/terms-of-service", "/terms-and-conditions",
        "/legal",
    ]
    origin = up.urlunparse(up.urlparse(base_url)._replace(path="/", params="", query="", fragment=""))
    return [up.urljoin(origin, p) for p in common_paths]

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
}

def Clausefetch(url: str) -> Dict[str, Any]:
    if not url.startswith(("http://", "https://")):
        return {
            "success": False, "found_in_page": False, "found_in_links": False,
            "content": None, "links": None, "error": "Invalid URL format"
        }

    # Fetch homepage
    try:
        resp = r.get(url, headers=header, timeout=10)
        resp.raise_for_status()
    except r.exceptions.RequestException as e:
        return {
            "success": False, "found_in_page": False, "found_in_links": False,
            "content": None, "links": None, "error": f"Connection error: {e}"
        }

    html = normalized_html(resp)
    soup = b(html, "lxml")
    page_text = clean_text_from_html(soup)

    # 1) Try to detect in-page
    in_page = tac_in_page(page_text, soup)
    if in_page["success"]:
        return {
            "success": True, "found_in_page": True, "found_in_links": False,
            "content": in_page["content"], "links": None, "error": None
        }

    # 2) Look for legal links (cross-domain allowed), else probe common paths
    candidates = find_legal_links(soup, url)
    if not candidates:
        candidates = guess_legal_paths(url)

    found_docs: List[Dict[str, str]] = []
    for link in candidates[:8]:
        try:
            r2 = r.get(link, headers=header, timeout=7)
            r2.raise_for_status()
        except r.exceptions.RequestException:
            continue

        html2 = normalized_html(r2)
        soup2 = b(html2, "lxml")
        sub_text = clean_text_from_html(soup2)
        sub_check = tac_in_page(sub_text, soup2)
        if sub_check["success"]:
            found_docs.append({"url": link, "content": sub_check["content"]})

    if found_docs:
        return {
            "success": True, "found_in_page": False, "found_in_links": True,
            "content": found_docs, "links": candidates, "error": None
        }

    return {
        "success": False, "found_in_page": False, "found_in_links": False,
        "content": None, "links": None, "error": None
    }


if __name__ == "__main__":
    test_url = input("Enter a URL: ").strip()
    result = Clausefetch(test_url)

    if result.get("success"):
        if result.get("found_in_page"):
            print("T&C content found in page.\n")
            content = result.get("content")
            print(str(content)[:1200])
        elif result.get("found_in_links"):
            print("T&C content found in linked pages.\n")
            content = result.get("content")
            if isinstance(content, list) and content:
                first = content[0]
                print(f"Source: {first.get('url', 'unknown')}\n")
                print(first.get("content", "")[:1200])
            else:
                print(str(content)[:1200])
        else:
            print("Success but no flags set; inspect content:\n")
            print(str(result.get("content"))[:800])
    else:
        print("No T&C content found or error:", result.get("error"))