import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select

from app.dependencies import DBSession
from app.models.document import Document
from app.schemas.document import DocumentList, DocumentRead
from app.services.company_service import CompanyService
from app.services.edgar_service import EdgarService
from app.services.sedar_service import SedarService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/companies/{company_id}/documents", tags=["documents"])


@router.get("", response_model=DocumentList)
async def list_documents(
    db: DBSession,
    company_id: UUID,
    doc_type: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
):
    conditions = [Document.company_id == company_id]
    if doc_type:
        conditions.append(Document.doc_type == doc_type)

    count_q = select(func.count()).where(*conditions)
    total = (await db.execute(count_q)).scalar_one()

    q = (
        select(Document)
        .where(*conditions)
        .order_by(Document.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(q)
    items = list(result.scalars().all())
    return DocumentList(items=items, total=total, page=page, per_page=per_page)


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(db: DBSession, company_id: UUID, document_id: UUID):
    q = select(Document).where(Document.id == document_id, Document.company_id == company_id)
    result = await db.execute(q)
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/ingest", response_model=DocumentList)
async def ingest_documents(db: DBSession, company_id: UUID):
    """Ingest recent filings from EDGAR (US) or SEDAR+ (Canada) for a company."""
    from sqlalchemy import func

    company_svc = CompanyService(db)
    company = await company_svc.get_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    documents = []

    # Ingest from EDGAR if US company
    if company.cik:
        edgar = EdgarService()
        try:
            for filing_type in ["10-K", "10-Q"]:
                filings = await edgar.get_recent_filings(company.cik, filing_type)
                for filing in filings:
                    # Check if document already exists
                    existing = await db.execute(
                        select(Document).where(
                            Document.company_id == company_id,
                            Document.source_url == filing["primary_document_url"],
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue

                    doc = Document(
                        company_id=company_id,
                        doc_type=filing["form_type"],
                        source="edgar",
                        source_url=filing["primary_document_url"],
                        filing_date=filing["filing_date"],
                    )
                    db.add(doc)
                    documents.append(doc)
        except Exception as e:
            logger.warning("EDGAR ingest failed for company %s: %s", company_id, e)

    # Ingest from SEDAR+ if Canadian company (TSX)
    if company.exchange == "TSX":
        sedar = SedarService()
        try:
            filings = await sedar.get_recent_filings(company.name)
            for filing in filings:
                existing = await db.execute(
                    select(Document).where(
                        Document.company_id == company_id,
                        Document.source_url == filing.get("url", ""),
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                doc = Document(
                    company_id=company_id,
                    doc_type=filing.get("type", "Unknown"),
                    source="sedar",
                    source_url=filing.get("url", ""),
                    filing_date=filing.get("filing_date"),
                )
                db.add(doc)
                documents.append(doc)
        except Exception as e:
            logger.warning("SEDAR+ ingest failed for company %s: %s", company_id, e)

    if not documents:
        # Return empty list if no documents found
        return DocumentList(items=[], total=0, page=1, per_page=50)

    await db.commit()

    # Refresh to get full objects with IDs
    for doc in documents:
        await db.refresh(doc)

    return DocumentList(
        items=documents,
        total=len(documents),
        page=1,
        per_page=50,
    )
