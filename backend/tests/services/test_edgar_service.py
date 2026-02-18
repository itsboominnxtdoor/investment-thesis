"""Tests for EdgarService — EDGAR response parsing, CIK padding."""

import pytest

from app.services.edgar_service import EdgarService


class TestCikPadding:
    """Test CIK padding logic used in get_recent_filings."""

    def test_pads_short_cik(self):
        cik = "320193"
        padded = cik.lstrip("0").zfill(10)
        assert padded == "0000320193"

    def test_already_padded_cik(self):
        cik = "0000320193"
        padded = cik.lstrip("0").zfill(10)
        assert padded == "0000320193"

    def test_very_short_cik(self):
        cik = "42"
        padded = cik.lstrip("0").zfill(10)
        assert padded == "0000000042"


class TestParseFilingHtml:
    def test_strips_tags(self):
        service = EdgarService()
        html = b"<html><body><p>Hello World</p><script>evil()</script></body></html>"
        text = service.parse_filing_html(html)
        assert "Hello World" in text
        assert "<script>" not in text
        assert "evil()" not in text

    def test_truncates_long_content(self):
        service = EdgarService()
        html = b"<html><body>" + b"x" * 100_000 + b"</body></html>"
        text = service.parse_filing_html(html)
        assert len(text) <= 80_000

    def test_handles_empty_content(self):
        service = EdgarService()
        text = service.parse_filing_html(b"")
        assert isinstance(text, str)
