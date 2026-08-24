from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from record_catalog.database import get_db
from record_catalog.models import Record
from record_catalog.schemas import (
    RecordCreate,
    RecordListResponse,
    RecordResponse,
)

router = APIRouter()


@router.post("/records", status_code=status.HTTP_201_CREATED, response_model=RecordResponse)
async def create_record(payload: RecordCreate, db: AsyncSession = Depends(get_db)) -> Record:
    record = Record(**payload.model_dump())
    db.add(record)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate artist/album")
    await db.refresh(record)
    return record


@router.get("/records/{record_id}", response_model=RecordResponse)
async def get_record(record_id: int, db: AsyncSession = Depends(get_db)) -> Record:
    record = await db.get(Record, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


@router.put("/records/{record_id}", response_model=RecordResponse)
async def update_record(
    record_id: int, payload: RecordCreate, db: AsyncSession = Depends(get_db)
) -> Record:
    record = await db.get(Record, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    for key, value in payload.model_dump().items():
        setattr(record, key, value)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate artist/album")
    await db.refresh(record)
    return record


@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(record_id: int, db: AsyncSession = Depends(get_db)) -> None:
    record = await db.get(Record, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    await db.delete(record)
    await db.flush()


@router.get("/records", response_model=RecordListResponse)
async def list_records(
    limit: int = Query(default=50, ge=1),
    offset: int = Query(default=0, ge=0),
    artist: str | None = Query(default=None),
    album: str | None = Query(default=None),
    genre: str | None = Query(default=None),
    year: int | None = Query(default=None),
    condition: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> RecordListResponse:
    limit = min(limit, 100)

    query = select(Record)
    count_query = select(func.count(Record.id))

    if artist:
        query = query.where(Record.artist.ilike(f"%{artist}%"))
        count_query = count_query.where(Record.artist.ilike(f"%{artist}%"))
    if album:
        query = query.where(Record.album.ilike(f"%{album}%"))
        count_query = count_query.where(Record.album.ilike(f"%{album}%"))
    if genre:
        query = query.where(Record.genre.ilike(genre))
        count_query = count_query.where(Record.genre.ilike(genre))
    if year is not None:
        query = query.where(Record.year == year)
        count_query = count_query.where(Record.year == year)
    if condition:
        query = query.where(Record.condition.ilike(condition))
        count_query = count_query.where(Record.condition.ilike(condition))

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    records = list(result.scalars().all())

    return RecordListResponse(
        items=[RecordResponse.model_validate(r) for r in records],
        total=total,
        limit=limit,
        offset=offset,
    )
