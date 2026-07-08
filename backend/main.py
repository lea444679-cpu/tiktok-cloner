import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

from services.downloader import download_tiktok
from services.transcriber import transcribe
from services.analyzer import analyze_structure
from services.script_generator import generate_new_script
from services.tts import generate_voiceover
from services.broll import fetch_broll_clips
from services.video_assembler import assemble_video

load_dotenv()

STORAGE_DIR = os.environ.get("STORAGE_DIR", "./storage")
os.makedirs(STORAGE_DIR, exist_ok=True)

app = FastAPI(title="TikTok Structure Cloner")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre à ton domaine frontend en prod
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/files", StaticFiles(directory=STORAGE_DIR), name="files")


class AnalyzeRequest(BaseModel):
    tiktok_url: str


class GenerateRequest(BaseModel):
    tiktok_url: str
    new_topic: str
    target_duration: int  # secondes, entre 10 et 90


@app.post("/analyze")
def analyze_endpoint(req: AnalyzeRequest):
    """
    Étape 1 : télécharge la vidéo TikTok, la transcrit, et renvoie la formule
    détectée (hook, structure, CTA, rythme) à l'utilisateur pour vérification.
    """
    try:
        video_info = download_tiktok(req.tiktok_url, STORAGE_DIR)
        segments = transcribe(video_info["video_path"])
        structure = analyze_structure(segments)
        # Nettoyage du fichier vidéo source, on n'en a plus besoin
        if os.path.exists(video_info["video_path"]):
            os.remove(video_info["video_path"])
        return {"structure": structure, "source_duration": video_info["duration"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/generate")
async def generate_endpoint(req: GenerateRequest):
    """
    Étape 2 : à partir de la formule détectée + un nouveau sujet + une durée
    cible, génère une vidéo entièrement nouvelle (script, voix, b-roll, sous-titres).
    """
    if not (10 <= req.target_duration <= 90):
        raise HTTPException(status_code=400, detail="La durée doit être entre 10 et 90 secondes.")

    try:
        video_info = download_tiktok(req.tiktok_url, STORAGE_DIR)
        segments = transcribe(video_info["video_path"])
        structure = analyze_structure(segments)
        if os.path.exists(video_info["video_path"]):
            os.remove(video_info["video_path"])

        new_script = generate_new_script(structure, req.new_topic, req.target_duration)

        full_text = " ".join(s["text"] for s in new_script["segments"])
        job_id = os.urandom(6).hex()
        voiceover_path = os.path.join(STORAGE_DIR, f"{job_id}_voice.mp3")
        await generate_voiceover(
            full_text, voiceover_path, new_script.get("voiceover_style", "default")
        )

        broll_paths = fetch_broll_clips(req.new_topic, count=4, storage_dir=STORAGE_DIR)

        output_path = os.path.join(STORAGE_DIR, f"{job_id}_final.mp4")
        assemble_video(
            broll_paths=broll_paths,
            voiceover_path=voiceover_path,
            subtitle_segments=new_script["segments"],
            target_duration=req.target_duration,
            output_path=output_path,
        )

        return {
            "video_url": f"/files/{job_id}_final.mp4",
            "structure_used": structure,
            "script": new_script,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}
