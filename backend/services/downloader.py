"""
Téléchargement d'une vidéo TikTok à partir de son URL, via yt-dlp.
On ne garde la vidéo que temporairement, le temps d'en extraire l'audio
pour la transcription. On ne réutilise jamais ce fichier dans la vidéo finale.
"""
import os
import uuid
import yt_dlp


def download_tiktok(url: str, storage_dir: str) -> dict:
    """
    Télécharge la vidéo TikTok et retourne le chemin du fichier + métadonnées.
    """
    os.makedirs(storage_dir, exist_ok=True)
    file_id = str(uuid.uuid4())
    output_path = os.path.join(storage_dir, f"{file_id}_source.%(ext)s")

    ydl_opts = {
        "outtmpl": output_path,
        "format": "mp4/best",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        final_path = ydl.prepare_filename(info)

    return {
        "file_id": file_id,
        "video_path": final_path,
        "duration": info.get("duration", 0),
        "title": info.get("title", ""),
        "original_caption": info.get("description", ""),
    }
