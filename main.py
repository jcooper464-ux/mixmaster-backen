from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
import whisper

app = FastAPI()

# Allow Framer → FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Make temp folder (Render-safe)
os.makedirs("/tmp", exist_ok=True)

# ============================================================
# LOAD WHISPER MODEL
# ============================================================
print("Loading Whisper model...")
whisper_model = whisper.load_model("tiny")
print("Whisper loaded.")

# ============================================================
# SIMPLE PLACEHOLDER CLEAN FUNCTION
# ============================================================
def simple_clean(audio_path):
    return audio_path

# ============================================================
# SIMPLE PLACEHOLDER MIXMASTER FUNCTION
# ============================================================
def simple_mixmaster(audio_path, style):
    return audio_path

# ============================================================
# HOMEPAGE ROUTE
# ============================================================
@app.get("/")
def home():
    return {"status": "MixMaster backend running"}

# ============================================================
# /clean-vocals ENDPOINT
# ============================================================
@app.post("/clean-vocals")
async def clean_vocals(audio: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    input_path = f"/tmp/{file_id}_{audio.filename}"

    with open(input_path, "wb") as f:
        f.write(await audio.read())

    cleaned_path = simple_clean(input_path)

    return {
        "cleaned_audio_url": f"https://mixmaster-backen.onrender.com/download/{os.path.basename(cleaned_path)}"
    }

# ============================================================
# /mix-master ENDPOINT
# ============================================================
@app.post("/mix-master")
async def mix_master(audio: UploadFile = File(...), style: str = Form("pop")):
    file_id = str(uuid.uuid4())
    input_path = f"/tmp/{file_id}_{audio.filename}"

    with open(input_path, "wb") as f:
        f.write(await audio.read())

    mastered_path = simple_mixmaster(input_path, style)

    return {
        "mastered_audio_url": f"https://mixmaster-backen.onrender.com/download/{os.path.basename(mastered_path)}"
    }

# ============================================================
# /transcribe ENDPOINT (WHISPER)
# ============================================================
@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    input_path = f"/tmp/{file_id}_{audio.filename}"

    # Save file
    with open(input_path, "wb") as f:
        f.write(await audio.read())

    # Run Whisper transcription
    result = whisper_model.transcribe(input_path)

    return {
        "text": result["text"],
        "segments": result["segments"],
        "language": result.get("language", "unknown")
    }

# ============================================================
# DOWNLOAD ROUTE
# ============================================================
@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"/tmp/{filename}"

    if not os.path.exists(file_path):
        return JSONResponse({"error": "File not found"}, status_code=404)

    return FileResponse(
        file_path,
        media_type="audio/wav",
        filename=filename
    )
