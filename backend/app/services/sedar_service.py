"""SEDAR+ filing retrieval service for TSX-listed companies."""

import logging
import re

import httpx

logger = logging.getLogger(__name__)

# SEDAR+ API endpoints
SEDAR_SEARCH_URL = "https://www.sedarplus.ca/csesvc/en/filing.do"
SEDAR_BASE_URL = "https://www.sedarplus.ca"

# Filing type mappings (SEDAR uses different terminology)
FILING_TYPE_MAP = {
    "10-K": ["AIF", "Annual Financial Statements"],
    "10-Q": ["Interim Financial Statements", "MD&A"],
    "AIF": ["AIF"],
    "MD&A": ["MD&A"],
}

MAX_FILING_TEXT_CHARS = 80_000


class SedarService:
    """Downloads and parses SEDAR+ filings for Canadian companies.
    
    Note: SEDAR+ does not have a public API. This service uses web scraping
    as a fallback. For production use, consider a paid data provider like
    SEDAR+ Direct API or a third-party service (e.g., Calcbench, Intrinio).
    """

    def __init__(self):
        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )

    async def close(self):
        await self.session.aclose()

    async def get_recent_filings(
        self, company_name: str, filing_type: str = "10-K"
    ) -> list[dict]:
        """Fetch list of recent filings from SEDAR+ by company name search.

        Currently a stub — SEDAR+ has no public API and requires JS rendering.
        TSX financial data is available via FMP (FinancialDataService) for the MVP.

        To enable full SEDAR+ integration, implement one of:
        1. Intrinio API (https://intrinio.com/) — has Canadian filings
        2. SEDAR+ Direct API — official, requires paid subscription
        3. Calcbench — institutional-grade filing access

        Args:
            company_name: Name of the company to search for
            filing_type: Type of filing (10-K, 10-Q, AIF, MD&A)

        Returns:
            Empty list (stub). Future: list of filing dicts with metadata.
        """
        sedar_types = FILING_TYPE_MAP.get(filing_type, [filing_type])

        logger.info(
            "SEDAR+ stub called for '%s' (types=%s). "
            "TSX financials are served via FMP. To add SEDAR+ filing retrieval, "
            "integrate a paid provider (Intrinio, Calcbench, or SEDAR+ Direct).",
            company_name,
            sedar_types,
        )

        return []

    async def download_filing(self, url: str) -> bytes:
        """Download a filing document from SEDAR+.
        
        Args:
            url: Full URL to the filing document
            
        Returns:
            Raw bytes of the filing document
        """
        try:
            resp = await self.session.get(url)
            resp.raise_for_status()
            return resp.content
        except httpx.HTTPError as e:
            logger.error("Failed to download SEDAR+ filing: %s", e)
            raise

    def parse_filing_html(self, content: bytes) -> str:
        """Extract text content from a SEDAR+ HTML filing.
        
        Uses regex-based tag stripping for lightweight parsing.
        Falls back gracefully if beautifulsoup4 is available.
        
        Args:
            content: Raw HTML bytes
            
        Returns:
            Extracted text content
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
