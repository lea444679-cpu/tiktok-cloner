"""
Génère un script 100% nouveau (nouveau sujet, nouveaux mots) qui suit exactement
la même formule (hook, structure, CTA, rythme) que celle détectée, adapté à la
durée cible choisie par l'utilisateur (10s à 90s).
"""
import os
import json
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

GENERATION_PROMPT = """Tu es un scénariste expert en vidéos TikTok virales.

Voici la FORMULE (structure narrative) extraite d'une vidéo qui a bien fonctionné :
{structure_json}

Écris un script ENTIÈREMENT ORIGINAL sur le sujet suivant : "{new_topic}"
Ce script doit suivre exactement la même formule (même type de hook, même
structure, même position du CTA, même ton, même rythme), mais avec un contenu
100% nouveau et différent (aucune phrase ne doit ressembler à l'originale).

Durée cible de la vidéo : {target_duration} secondes.
Découpe le script en segments courts adaptés à des sous-titres dynamiques
(3 à 8 mots par segment), avec un timing cohérent qui remplit toute la durée cible.

Réponds en JSON strict, sans texte autour, avec ce format exact :

{{
  "segments": [
    {{"start": 0.0, "end": 1.8, "text": "..."}},
    {{"start": 1.8, "end": 3.5, "text": "..."}}
  ],
  "cta_text": "le texte exact du CTA final",
  "voiceover_style": "ton à utiliser pour la voix off (énergique/calme/etc.)"
}}
"""


def generate_new_script(structure: dict, new_topic: str, target_duration: int) -> dict:
    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": GENERATION_PROMPT.format(
                structure_json=json.dumps(structure, ensure_ascii=False),
                new_topic=new_topic,
                target_duration=target_duration,
            ),
        }],
    )

    raw = message.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)
