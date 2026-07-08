"""
Récupère des clips vidéo de b-roll (libres de droits) en lien avec le nouveau
sujet, via l'API gratuite Pexels.
"""
import os
import requests

PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]
PEXELS_URL = "https://api.pexels.com/videos/search"


def fetch_broll_clips(query: str, count: int, storage_dir: str) -> list[str]:
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": count, "orientation": "portrait"}

    resp = requests.get(PEXELS_URL, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    clip_paths = []
    for i, video in enumerate(data.get("videos", [])[:count]):
        # On prend le fichier HD le plus proche du format vertical
        files = sorted(video["video_files"], key=lambda f: f.get("width", 0))
        best = next((f for f in files if f.get("width", 0) <= 1080), files[-1])

        video_data = requests.get(best["link"], timeout=30).content
        path = os.path.join(storage_dir, f"broll_{i}.mp4")
        with open(path, "wb") as f:
            f.write(video_data)
        clip_paths.append(path)

    return clip_paths
