"""SEDAR+ filing retrieval service for TSX-listed companies."""


class SedarService:
    """Downloads and parses SEDAR+ filings for Canadian companies."""

    async def get_recent_filings(self, sedar_id: str, filing_type: str = "annual") -> list[dict]:
        """Fetch list of recent filings from SEDAR+."""
        raise NotImplementedError("SEDAR+ filing retrieval not yet implemented")

    async def download_filing(self, document_id: str) -> bytes:
        """Download a filing document from SEDAR+."""
        raise NotImplementedError("SEDAR+ filing download not yet implemented")
