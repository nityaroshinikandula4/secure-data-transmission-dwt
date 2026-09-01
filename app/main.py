from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from .stego import decode, encode, sample_carrier

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
MAX_UPLOAD_BYTES = 20 * 1024 * 1024

app = FastAPI(
    title="WaveVault DWT Steganography API",
    version="1.0.0",
    description="Encrypted message hiding in reversible integer-wavelet coefficients for a portfolio demonstration.",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


async def read_upload(upload: UploadFile) -> bytes:
    data = await upload.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image exceeds the 20 MB upload limit.")
    return data


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "wavevault"}


@app.get("/api/sample-carrier")
def get_sample_carrier() -> Response:
    return Response(sample_carrier(), media_type="image/png", headers={"Content-Disposition": 'inline; filename="wavevault-sample.png"'})


@app.post("/api/encode")
async def encode_message(
    image: UploadFile = File(...),
    message: str = Form(..., min_length=1, max_length=16_384),
    password: str = Form(..., min_length=8, max_length=256),
) -> Response:
    try:
        result = encode(await read_upload(image), message, password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return Response(
        result.image_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": 'attachment; filename="wavevault-protected.png"',
            "X-WaveVault-Width": str(result.width),
            "X-WaveVault-Height": str(result.height),
            "X-WaveVault-Capacity": str(result.capacity_bytes),
            "X-WaveVault-Payload": str(result.payload_bytes),
        },
    )


@app.post("/api/decode")
async def decode_message(
    image: UploadFile = File(...),
    password: str = Form(..., min_length=8, max_length=256),
) -> JSONResponse:
    try:
        message = decode(await read_upload(image), password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return JSONResponse({"message": message})


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
