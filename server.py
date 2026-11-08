"""NeVedis web server.  Run:  .venv/bin/python server.py   then open http://127.0.0.1:8501"""
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import analyzer
import scams

HERE = Path(__file__).parent
MAX_BYTES = 15 * 1024 * 1024
PORT = 8501

app = FastAPI(title="NeVedis", docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")


def sniff(head: bytes) -> tuple[str, str] | None:
    """Identify a file by its first bytes (never trust the file name). Returns (kind, extension)."""
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image", "png"
    if head.startswith(b"\xff\xd8\xff"):
        return "image", "jpg"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image", "webp"
    if head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        return "audio", "wav"
    if head.startswith(b"ID3") or (len(head) > 1 and head[0] == 0xFF and head[1] & 0xE0 == 0xE0):
        return "audio", "mp3"
    if head[4:8] == b"ftyp" and head[8:12] in (b"M4A ", b"mp42", b"isom", b"M4B ", b"dash"):
        return "audio", "m4a"
    return None


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(HERE / "static" / "index.html", headers={"Cache-Control": "no-store"})


@app.get("/api/library")
def library():
    return scams.library()


@app.post("/api/check")
def check(text: str = Form(""), files: list[UploadFile] = File(default=[])):
    text = text[:20000]
    image = audio = None
    for f in files[:4]:
        data = f.file.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise HTTPException(413, f"{f.filename} is bigger than 15 MB.")
        kind = sniff(data[:16])
        if not kind:
            raise HTTPException(415, f"{f.filename}: NeVedis reads screenshots (PNG, JPG, WEBP) and recordings (MP3, WAV, M4A).")
        if kind[0] == "image" and not image:
            image = (data, kind[1])
        elif kind[0] == "audio" and not audio:
            audio = (data, kind[1])
    if not text.strip() and not image and not audio:
        raise HTTPException(400, "Paste a message, or add a screenshot or a recording.")
    return analyzer.analyze(text, "Unknown", image, audio)


if __name__ == "__main__":
    print(f"\n  NeVedis is running at  http://127.0.0.1:{PORT}\n  Press Ctrl+C to stop.\n")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
