# TikTok Structure Cloner

Site qui analyse la structure d'une vidéo TikTok (hook, rythme, CTA, sous-titres)
et génère une **vidéo entièrement nouvelle** sur un autre sujet, en gardant la
même formule qui fonctionne. Durée réglable de 10 à 90 secondes.

## ⚠️ À lire avant de déployer

1. **Le fichier vidéo/audio original n'est jamais réutilisé.** Le pipeline
   télécharge la vidéo source uniquement pour la transcrire, puis la supprime.
   La vidéo finale est composée à 100% de nouveaux médias (nouvelle voix off
   générée, nouveau b-roll libre de droits, nouveau texte). C'est ce qui fait
   que ce n'est pas "une copie" mais un clone de structure narrative.
2. **yt-dlp** (téléchargement TikTok) fonctionne très bien aujourd'hui, mais
   TikTok change régulièrement ses protections. Il peut nécessiter des mises à
   jour fréquentes (`pip install -U yt-dlp`). Ce n'est pas une API officielle.
3. **Coûts réels** : hébergement quasi gratuit sauf calcul vidéo (ffmpeg/Whisper
   consomment du CPU) → prévoir un petit serveur (~5-10$/mois, ex: Render,
   Railway, Hetzner). Les appels Claude (analyse + script) coûtent quelques
   centimes par vidéo générée. Pexels et edge-tts sont gratuits.
4. Respecte les CGU de TikTok et les droits d'auteur : n'utilise ce site que
   pour t'inspirer de formats/structures, pas pour republier du contenu d'autrui.

## Structure du projet

```
tiktok-cloner/
├── backend/          # API FastAPI (Python)
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── services/
│       ├── downloader.py      # téléchargement TikTok (yt-dlp)
│       ├── transcriber.py     # transcription + timing (faster-whisper)
│       ├── analyzer.py        # extraction de la formule (Claude)
│       ├── script_generator.py# nouveau script même formule (Claude)
│       ├── tts.py              # voix off (edge-tts, gratuit)
│       ├── broll.py            # b-roll libre de droits (Pexels, gratuit)
│       └── video_assembler.py  # montage final (moviepy/ffmpeg)
└── frontend/          # Next.js
    └── app/
        ├── page.tsx
        ├── layout.tsx
        └── globals.css
```

## Installation en local

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

# ffmpeg doit être installé sur le système
# Mac: brew install ffmpeg | Ubuntu: sudo apt install ffmpeg

cp .env.example .env
# remplis ANTHROPIC_API_KEY et PEXELS_API_KEY dans .env

uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

Ouvre `http://localhost:3000`.

## Déploiement en production

- **Frontend** : Vercel (gratuit) — connecte le repo GitHub, ajoute la variable
  d'environnement `NEXT_PUBLIC_API_URL` pointant vers ton backend.
- **Backend** : Render ou Railway (plan payant nécessaire à cause du CPU pour
  Whisper/ffmpeg — le plan gratuit timeout trop vite). Alternative : un VPS
  Hetzner/OVH à ~5€/mois avec Docker.
- Pense à sécuriser `/generate` (rate limiting, auth basique) pour éviter les
  abus, vu que chaque appel a un coût.

## Où obtenir les clés API gratuites/pas chères

- **Anthropic (Claude)** : https://console.anthropic.com — facturation à l'usage,
  quelques centimes par vidéo avec `claude-haiku-4-5` / `claude-sonnet-5`.
- **Pexels** : https://www.pexels.com/api/ — inscription gratuite, quota large.

## Prochaines améliorations possibles

- Ajouter une preview du script généré avant de lancer le montage (validation
  humaine du texte avant de payer le rendu vidéo).
- Cache des analyses de structure pour ne pas re-télécharger deux fois la même
  vidéo source.
- File d'attente (Celery/Redis) pour gérer plusieurs générations en parallèle
  sans bloquer le serveur.
- Choix de plusieurs voix / styles de sous-titres dans l'interface.
