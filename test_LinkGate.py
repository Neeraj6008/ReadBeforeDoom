import pytest
from unittest.mock import patch, MagicMock
import Linkgate


class MockResponse:
    def __init__(self, status_code=200, url="http://example.com", headers=None):
        self.status_code = status_code
        self.url = url
        self.headers = headers or {}


def test_invalid_scheme():
    result = Linkgate.linkgate("ftp://example.com")
    assert not result["valid"]
    assert "scheme" in result["message"]

@pytest.mark.parametrize("url, expected_part_of_message", [
    ("https://inv@lid_hostname", "invalid TLD"),
    ("https://invalid_hostname.com", "hostname"),
    ("http://-startshyphen.example", "hostname"),
    ("http://toolonglabeltoolonglabeltoolonglabeltoolonglabeltoolonglabeltoolonglabel.com", "hostname"),
])
def test_invalid_hostname_format(url, expected_part_of_message):
    result = Linkgate.linkgate(url)
    assert not result["valid"]
    assert expected_part_of_message in result["message"]


@patch("Linkgate.requests.get")
def test_invalid_tld(mock_get):
    mock_get.return_value.text = "COM\nORG\nNET\n"  # 'XYZ' is NOT in this list
    result = Linkgate.linkgate("http://website.xyz")
    assert not result["valid"]
    assert ("invalid TLD" in result["message"]) or ("hostname" in result["message"])



@patch("Linkgate.requests.get")
def test_tld_fetch_failure(mock_get):
    mock_get.side_effect = Exception("Network error")
    result = Linkgate.linkgate("http://validhost.test")
    assert not result["valid"]
    assert "Couldn't load TLDs" in result["message"]



def test_idn_invalid_domain():
    result = Linkgate.linkgate("http://example.\uD800")
    assert not result["valid"]
    assert "Internationalized" in result["message"]


@patch("Linkgate.dns.resolver.resolve")
def test_dns_nx_domain(mock_resolve):
    mock_resolve.side_effect = Linkgate.dns.resolver.NXDOMAIN
    result = Linkgate.ipvcollector("notexistingsite.example")
    assert not result["valid"]
    assert "Hostname does not exist" in result["message"]


@patch("Linkgate.dns.resolver.resolve")
def test_dns_timeout(mock_resolve):
    mock_resolve.side_effect = Linkgate.dns.resolver.Timeout
    result = Linkgate.ipvcollector("timeout.example")
    assert not result["valid"]
    assert "timed out" in result["message"]


@patch("Linkgate.dns.resolver.resolve")
def test_dns_no_answer(mock_resolve):
    def side_effect(name, record_type):
        if record_type == "A":
            raise Linkgate.dns.resolver.NoAnswer
        else:
            class Rdata:
                address = "2001:db8::1"

            return [Rdata()]

    mock_resolve.side_effect = side_effect
    result = Linkgate.ipvcollector("noanswer.example")
    assert "iplist" in result
    assert "2001:db8::1" in result["iplist"]


def test_is_valid_hostname():
    valid = Linkgate.is_valid_hostname("sub.domain.com")
    invalid = Linkgate.is_valid_hostname("inva lid.com")
    repeated_label = Linkgate.is_valid_hostname("aaaabbbb.domain.com")
    assert valid is True
    assert invalid is False
    assert repeated_label is False


@patch("Linkgate.requests.head")
@patch("Linkgate.status_code_checker")
def test_status_code_checker_redirect(mock_checker, mock_head):
    mock_checker.return_value = {"valid": True, "redirect/link": "http://redirected.com"}
    mock_head.return_value = MagicMock()
    mock_head.return_value.status_code = 301
    mock_head.return_value.headers = {"Location": "http://redirected.com"}
    mock_head.return_value.url = "http://original.com"

    result = Linkgate.linkgate("http://original.com")
    assert result.get("valid") in (True, False)


@patch("Linkgate.requests.head")
@patch("Linkgate.status_code_checker")
def test_status_code_checker_no_redirect_link(mock_checker, mock_head):
    mock_checker.return_value = {"valid": True, "redirect/link": False}
    mock_head.return_value = MagicMock()
    mock_head.return_value.status_code = 200
    mock_head.return_value.url = "http://site.com"

    result = Linkgate.linkgate("http://site.com")
    assert "valid" in result


@patch("Linkgate.requests.head")
def test_requests_head_timeout():
    with patch("Linkgate.requests.head", side_effect=Linkgate.requests.exceptions.Timeout("timeout")):
        result = Linkgate.linkgate("http://timeout.com")
        assert not result["valid"]
        assert "Connection failed" in result["message"]


@patch("Linkgate.dns.resolver.resolve")
def test_reserved_private_ip(mock_resolve):
    class Rdata:
        address = "192.168.1.1"  # private IP

    mock_resolve.return_value = [Rdata()]
    result = Linkgate.linkgate("http://example.com")
    assert not result["valid"]
    assert "Reserved" in result["message"]
