"""Quarterly ingestion pipeline — 7-step process for each company filing.

Steps:
1. Download filing from EDGAR/SEDAR+
2. Upload raw document to S3
3. Pull structured financial data from API
4. Create financial snapshot
5. Generate/update business profile via LLM
6. Generate new thesis version via LLM
7. Create quarterly update record
"""

import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.quarterly_ingestion.check_for_new_filings")
def check_for_new_filings():
    """Hourly beat task: check all active companies for new filings.

    For each company with a new filing detected, dispatches
    process_company_filing as a separate task.
    """
    logger.info("Checking for new filings across all active companies")
    # TODO: Implementation
    # 1. Query all active companies
    # 2. For each, check EDGAR (US) or SEDAR+ (CA) for new filings
    # 3. For each new filing found, dispatch process_company_filing.delay(company_id, filing_info)
    raise NotImplementedError("Filing check not yet implemented")


@celery_app.task(
    name="app.tasks.quarterly_ingestion.process_company_filing",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
)
def process_company_filing(self, company_id: str, filing_info: dict):
    """Process a single company's new filing through the 7-step pipeline.

    Args:
        company_id: UUID of the company
        filing_info: Dict with filing metadata (type, url, date, etc.)
    """
    logger.info("Processing filing for company %s: %s", company_id, filing_info.get("type"))

    try:
        # Step 1: Download filing
        _step_download_filing(company_id, filing_info)

        # Step 2: Upload to S3
        _step_upload_to_s3(company_id, filing_info)

        # Step 3: Pull structured financial data
        _step_pull_financial_data(company_id, filing_info)

        # Step 4: Create financial snapshot
        _step_create_snapshot(company_id, filing_info)

        # Step 5: Generate business profile
        _step_generate_profile(company_id, filing_info)

        # Step 6: Generate thesis version
        _step_generate_thesis(company_id, filing_info)

        # Step 7: Create quarterly update
        _step_create_quarterly_update(company_id, filing_info)

        logger.info("Successfully processed filing for company %s", company_id)

    except NotImplementedError:
        raise
    except Exception as exc:
        logger.exception("Failed to process filing for company %s", company_id)
        raise self.retry(exc=exc)


def _step_download_filing(company_id: str, filing_info: dict):
    """Step 1: Download the filing from EDGAR or SEDAR+."""
    raise NotImplementedError("Step 1: Download filing not yet implemented")


def _step_upload_to_s3(company_id: str, filing_info: dict):
    """Step 2: Upload the raw filing document to S3."""
    raise NotImplementedError("Step 2: Upload to S3 not yet implemented")


def _step_pull_financial_data(company_id: str, filing_info: dict):
    """Step 3: Pull structured financial data from external API."""
    raise NotImplementedError("Step 3: Pull financial data not yet implemented")


def _step_create_snapshot(company_id: str, filing_info: dict):
    """Step 4: Create an immutable financial snapshot record."""
    raise NotImplementedError("Step 4: Create snapshot not yet implemented")


def _step_generate_profile(company_id: str, filing_info: dict):
    """Step 5: Generate/update business profile via LLM."""
    raise NotImplementedError("Step 5: Generate profile not yet implemented")


def _step_generate_thesis(company_id: str, filing_info: dict):
    """Step 6: Generate new thesis version via LLM."""
    raise NotImplementedError("Step 6: Generate thesis not yet implemented")


def _step_create_quarterly_update(company_id: str, filing_info: dict):
    """Step 7: Create quarterly update record tying everything together."""
    raise NotImplementedError("Step 7: Create quarterly update not yet implemented")
