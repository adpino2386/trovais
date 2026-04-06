from fastapi import APIRouter, HTTPException
from api.models import IngestRequest, IngestResponse
from ingestion.embedder import ingest_file

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
def ingest_endpoint(request: IngestRequest):
    try:
        ingest_file(request.filepath)
        return IngestResponse(
            success=True,
            filename=request.filepath.split("\\")[-1],
            chunks_ingested=0,
            message="File ingested successfully"
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {request.filepath}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))