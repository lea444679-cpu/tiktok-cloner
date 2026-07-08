"""
Génère la voix off à partir du script, avec edge-tts (gratuit, voix Microsoft).
"""
import edge_tts

# Voix françaises disponibles (tu peux en tester d'autres avec `edge-tts --list-voices`)
VOICE_MAP = {
    "energique": "fr-FR-HenriNeural",
    "calme": "fr-FR-DeniseNeural",
    "default": "fr-FR-HenriNeural",
}


async def generate_voiceover(full_text: str, output_path: str, style: str = "default") -> str:
    voice = VOICE_MAP.get(style, VOICE_MAP["default"])
    communicate = edge_tts.Communicate(full_text, voice, rate="+5%")
    await communicate.save(output_path)
    return output_path
