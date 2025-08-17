import pytest
from Linkgate import linkgate  # replace with your actual import

test_cases = [
    # ✅ Should pass (valid, resolvable URLs)
    ("https://www.google.com", True),
    ("http://example.com", True),
    ("https://github.com", True),
    ("https://www.python.org", True),
    ("https://www.wikipedia.org", True),
    
    # ❌ Should fail (invalid or non-existent domains)
    ("https://thisdomaindoesnotexist123456.org", False),
    ("https://sub.example.org", False),  # subdomain that doesn't exist
    ("http://256.256.256.256", False),  # invalid IP
    ("ftp://example.com", False),        # unsupported scheme
    ("https://private.local", False),    # private/reserved domain
]

@pytest.mark.parametrize("url, should_pass", test_cases)
def test_linkgate(url, should_pass):
    import sys
    from contextlib import nullcontext
    
    # Expect SystemExit for failing cases
    context = pytest.raises(SystemExit) if not should_pass else nullcontext()
    
    with context:
        result = linkgate(url)
        if should_pass:
            assert result is not None
            assert isinstance(result, str)
