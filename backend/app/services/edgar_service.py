"""SEC EDGAR filing retrieval service."""

from app.config import settings


class EdgarService:
    """Downloads and parses SEC EDGAR filings (10-Q, 10-K)."""

    def __init__(self):
        self.user_agent = settings.EDGAR_USER_AGENT

    async def get_recent_filings(self, cik: str, filing_type: str = "10-Q") -> list[dict]:
        """Fetch list of recent filings for a company from EDGAR."""
        raise NotImplementedError("EDGAR filing retrieval not yet implemented")

    async def download_filing(self, accession_number: str) -> bytes:
        """Download the full filing document."""
        raise NotImplementedError("EDGAR filing download not yet implemented")

    async def parse_filing_html(self, content: bytes) -> str:
        """Extract text content from an EDGAR HTML filing."""
        raise NotImplementedError("EDGAR filing parsing not yet implemented")
