import os
import tempfile
import shutil

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.schemas import IngestResponse
from app.services.ingest import IngestService

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    bot_id: str = Form(...),
    namespace: str | None = Form(None),
):
    tmp_dir = tempfile.mkdtemp()
    try:
        file_path = os.path.join(tmp_dir, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        service = IngestService()
        result = await service.ingest_file(file_path, bot_id=bot_id, namespace=namespace)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
