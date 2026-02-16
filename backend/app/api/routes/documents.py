from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import DBSession
from app.schemas.document import DocumentList, DocumentRead

router = APIRouter(prefix="/companies/{company_id}/documents", tags=["documents"])


@router.get("", response_model=DocumentList)
async def list_documents(
    db: DBSession,
    company_id: UUID,
    doc_type: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
):
    from sqlalchemy import func, select

    from app.models.document import Document

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
    from sqlalchemy import select

    from app.models.document import Document

    q = select(Document).where(Document.id == document_id, Document.company_id == company_id)
    result = await db.execute(q)
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
