"""SEC EDGAR filing retrieval service."""

import logging
import re

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

EDGAR_SUBMISSIONS_URL = "https://data.sec.gov/submissions"
EDGAR_ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data"
MAX_FILING_TEXT_CHARS = 80_000


class EdgarService:
    """Downloads and parses SEC EDGAR filings (10-Q, 10-K)."""

    def __init__(self):
        self.user_agent = settings.EDGAR_USER_AGENT

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": self.user_agent, "Accept-Encoding": "gzip, deflate"},
        )

    async def get_recent_filings(self, cik: str, filing_type: str = "10-Q") -> list[dict]:
        """Fetch list of recent filings for a company from EDGAR."""
        cik_padded = cik.lstrip("0").zfill(10)
        url = f"{EDGAR_SUBMISSIONS_URL}/CIK{cik_padded}.json"

        async with self._client() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        recent = data.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        accession_numbers = recent.get("accessionNumber", [])
        filing_dates = recent.get("filingDate", [])
        primary_docs = recent.get("primaryDocument", [])

        filings = []
        for i, form in enumerate(forms):
            if form != filing_type:
                continue
            accession = accession_numbers[i]
            accession_no_dash = accession.replace("-", "")
            cik_num = cik.lstrip("0")
            doc_url = (
                f"{EDGAR_ARCHIVES_URL}/{cik_num}/{accession_no_dash}/{primary_docs[i]}"
            )
            filings.append({
                "accession_number": accession,
                "filing_date": filing_dates[i],
                "form_type": form,
                "primary_document_url": doc_url,
            })
            if len(filings) >= 5:
                break

        return filings

    async def download_filing(self, url: str) -> bytes:
        """Download a filing document by its full URL."""
        async with self._client() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content

    def parse_filing_html(self, content: bytes) -> str:
        """Extract text content from an EDGAR HTML filing.

        Uses regex-based tag stripping for lightweight parsing.
        Falls back gracefully if beautifulsoup4 is available.
        """
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(content, "lxml")
            # Remove script and style elements
            for tag in soup(["script", "style"]):
                tag.decompose()
            text = soup.get_text(separator="\n")
        except ImportError:
            # Fallback: simple regex tag stripping
            text_str = content.decode("utf-8", errors="replace")
            text = re.sub(r"<[^>]+>", " ", text_str)

        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines()]
        text = "\n".join(line for line in lines if line)

        # Truncate to fit LLM context
        if len(text) > MAX_FILING_TEXT_CHARS:
            text = text[:MAX_FILING_TEXT_CHARS]

        return text
