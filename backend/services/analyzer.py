"""
Analyse la transcription pour en extraire la FORMULE (hook, structure narrative,
CTA, rythme des sous-titres) — sans jamais renvoyer le texte original tel quel
dans le produit final. C'est cette formule qui sera réappliquée à un autre sujet.
"""
import os
import json
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

ANALYSIS_PROMPT = """Tu es un expert en scripts viraux TikTok. Voici la transcription
horodatée d'une vidéo TikTok :

{transcript}

Analyse UNIQUEMENT la structure et la formule utilisée (pas le contenu factuel).
Réponds en JSON strict, sans texte autour, avec ce format exact :

{{
  "hook_type": "ex: question choc / statistique surprenante / affirmation contre-intuitive",
  "hook_duration_seconds": nombre,
  "structure": ["étape 1 du script", "étape 2", "..."],
  "pacing": "description du rythme (phrases courtes, pauses, répétitions...)",
  "cta_type": "ex: appel à commenter / à s'abonner / à partager",
  "cta_position": "début / milieu / fin",
  "tone": "ex: énergique, informatif, humoristique...",
  "subtitle_style": "description du style des sous-titres (mots clés en avant, rythme d'apparition...)"
}}
"""


def analyze_structure(transcript_segments: list[dict]) -> dict:
    transcript_text = "\n".join(
        f"[{seg['start']}s -> {seg['end']}s] {seg['text']}" for seg in transcript_segments
    )

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": ANALYSIS_PROMPT.format(transcript=transcript_text),
        }],
    )

    raw = message.content[0].text.strip()
    # Sécurité si le modèle ajoute des ```json autour
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)
