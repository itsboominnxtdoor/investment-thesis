"""LLM service for thesis generation and analysis using Anthropic Claude."""

from app.config import settings


class LLMService:
    """Generates investment theses and analyses using Claude."""

    def __init__(self):
        self.model = settings.ANTHROPIC_MODEL
        self.api_key = settings.ANTHROPIC_API_KEY

    async def generate_business_profile(self, company_data: dict, filing_text: str) -> dict:
        """Generate a structured business profile from filing data.

        Returns dict with: description, business_model, competitive_position,
        key_products, geographic_mix, moat_assessment, moat_sources.
        """
        raise NotImplementedError("LLM business profile generation not yet implemented")

    async def generate_thesis(
        self,
        company_data: dict,
        financial_snapshot: dict,
        business_profile: dict,
        prior_thesis: dict | None = None,
    ) -> dict:
        """Generate a three-scenario investment thesis.

        IMPORTANT: Prompts explicitly prohibit buy/sell/hold recommendations.

        Returns dict with: bull_case, bull_target, base_case, base_target,
        bear_case, bear_target, key_drivers, key_risks, catalysts,
        thesis_integrity_score, integrity_rationale, drift_summary,
        conviction_direction.
        """
        raise NotImplementedError("LLM thesis generation not yet implemented")

    async def generate_quarterly_summary(
        self, filing_text: str, prior_snapshot: dict | None = None
    ) -> dict:
        """Generate executive summary and key changes from a quarterly filing.

        Returns dict with: executive_summary, key_changes, guidance_update,
        management_commentary.
        """
        raise NotImplementedError("LLM quarterly summary generation not yet implemented")
