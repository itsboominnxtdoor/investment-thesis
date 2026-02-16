"""LLM service for thesis generation and analysis using Anthropic Claude."""

import json
import logging
from pathlib import Path

import anthropic

from app.config import settings

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text()


def _parse_json_response(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        # Remove markdown code fences
        lines = text.splitlines()
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)


class LLMService:
    """Generates investment theses and analyses using Claude."""

    def __init__(self):
        self.model = settings.ANTHROPIC_MODEL
        self.api_key = settings.ANTHROPIC_API_KEY
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)

    async def _call(self, system: str, user_prompt: str, temperature: float = 0.3) -> str:
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text

    async def generate_business_profile(self, company_data: dict, filing_text: str) -> dict:
        """Generate a structured business profile from filing data."""
        prompt_template = _load_prompt("business_profile.txt")
        prompt = prompt_template.format(
            company_name=company_data.get("name", ""),
            ticker=company_data.get("ticker", ""),
            exchange=company_data.get("exchange", ""),
            sector=company_data.get("sector", ""),
            industry=company_data.get("industry", ""),
            filing_text=filing_text[:60000],
        )

        response = await self._call(
            system="You are a senior equity research analyst. Respond only with valid JSON.",
            user_prompt=prompt,
            temperature=0.3,
        )
        result = _parse_json_response(response)

        # Ensure JSON array/object fields are stored as JSON strings
        if isinstance(result.get("key_products"), list):
            result["key_products"] = json.dumps(result["key_products"])
        if isinstance(result.get("geographic_mix"), dict):
            result["geographic_mix"] = json.dumps(result["geographic_mix"])
        if isinstance(result.get("moat_sources"), list):
            result["moat_sources"] = json.dumps(result["moat_sources"])

        return result

    async def generate_thesis(
        self,
        company_data: dict,
        financial_snapshot: dict,
        business_profile: dict,
        prior_thesis: dict | None = None,
    ) -> dict:
        """Generate a three-scenario investment thesis."""
        prompt_template = _load_prompt("thesis_generation.txt")

        # Build prior thesis section
        prior_thesis_section = ""
        drift_fields = ""
        if prior_thesis:
            prior_thesis_section = (
                f"PRIOR THESIS (v{prior_thesis.get('version', '?')}):\n"
                f"Bull: {prior_thesis.get('bull_case', 'N/A')[:500]}\n"
                f"Base: {prior_thesis.get('base_case', 'N/A')[:500]}\n"
                f"Bear: {prior_thesis.get('bear_case', 'N/A')[:500]}\n"
            )
            drift_fields = (
                '- "drift_summary": A paragraph comparing this thesis to the prior version.\n'
                '- "conviction_direction": One of "strengthened", "weakened", or "unchanged".'
            )

        # Format business profile for prompt
        bp_text = (
            f"Description: {business_profile.get('description', 'N/A')}\n"
            f"Business Model: {business_profile.get('business_model', 'N/A')}\n"
            f"Competitive Position: {business_profile.get('competitive_position', 'N/A')}\n"
            f"Moat: {business_profile.get('moat_assessment', 'N/A')}"
        )

        prompt = prompt_template.format(
            company_name=company_data.get("name", ""),
            ticker=company_data.get("ticker", ""),
            sector=company_data.get("sector", ""),
            industry=company_data.get("industry", ""),
            revenue=financial_snapshot.get("revenue", "N/A"),
            net_income=financial_snapshot.get("net_income", "N/A"),
            ebitda=financial_snapshot.get("ebitda", "N/A"),
            eps_diluted=financial_snapshot.get("eps_diluted", "N/A"),
            gross_margin=financial_snapshot.get("gross_margin", "N/A"),
            operating_margin=financial_snapshot.get("operating_margin", "N/A"),
            free_cash_flow=financial_snapshot.get("free_cash_flow", "N/A"),
            total_debt=financial_snapshot.get("total_debt", "N/A"),
            cash=financial_snapshot.get("cash_and_equivalents", "N/A"),
            debt_to_equity=financial_snapshot.get("debt_to_equity", "N/A"),
            business_profile=bp_text,
            prior_thesis_section=prior_thesis_section,
            drift_fields=drift_fields,
        )

        response = await self._call(
            system="You are a senior equity research analyst. Respond only with valid JSON. Do NOT provide buy/sell/hold recommendations.",
            user_prompt=prompt,
            temperature=0.3,
        )
        result = _parse_json_response(response)

        # Ensure JSON array fields are stored as JSON strings
        for field in ("key_drivers", "key_risks", "catalysts"):
            if isinstance(result.get(field), list):
                result[field] = json.dumps(result[field])

        return result

    async def generate_quarterly_summary(
        self, filing_text: str, prior_snapshot: dict | None = None
    ) -> dict:
        """Generate executive summary and key changes from a quarterly filing."""
        prompt_template = _load_prompt("quarterly_summary.txt")

        prior_snapshot_section = ""
        if prior_snapshot:
            prior_snapshot_section = (
                f"PRIOR QUARTER SNAPSHOT:\n"
                f"Revenue: {prior_snapshot.get('revenue', 'N/A')}\n"
                f"Net Income: {prior_snapshot.get('net_income', 'N/A')}\n"
                f"EPS: {prior_snapshot.get('eps_diluted', 'N/A')}\n"
            )

        prompt = prompt_template.format(
            filing_text=filing_text[:60000],
            prior_snapshot_section=prior_snapshot_section,
        )

        response = await self._call(
            system="You are a senior equity research analyst. Respond only with valid JSON.",
            user_prompt=prompt,
            temperature=0.3,
        )
        result = _parse_json_response(response)

        # Ensure key_changes is stored as JSON string
        if isinstance(result.get("key_changes"), list):
            result["key_changes"] = json.dumps(result["key_changes"])

        return result
