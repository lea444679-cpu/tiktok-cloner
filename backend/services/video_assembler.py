"""
Assemble la vidéo finale : b-roll en boucle, voix off, sous-titres dynamiques
incrustés (style TikTok, mot par mot ou par courte phrase), coupée exactement
à la durée cible choisie par l'utilisateur.
"""
import os
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip,
    concatenate_videoclips, CompositeAudioClip,
)

W, H = 1080, 1920  # format vertical TikTok


def _make_subtitle_clips(segments: list[dict]):
    clips = []
    for seg in segments:
        txt = TextClip(
            seg["text"],
            fontsize=70,
            font="DejaVu-Sans-Bold",
            color="white",
            stroke_color="black",
            stroke_width=3,
            method="caption",
            size=(W - 100, None),
        ).set_start(seg["start"]).set_end(seg["end"])
        txt = txt.set_position(("center", H * 0.72))
        clips.append(txt)
    return clips


def _prepare_broll_track(broll_paths: list[str], target_duration: float) -> VideoFileClip:
    clips = []
    total = 0.0
    i = 0
    while total < target_duration:
        path = broll_paths[i % len(broll_paths)]
        clip = VideoFileClip(path).without_audio()
        # recadrage/resize simple pour coller au format vertical
        clip = clip.resize(height=H)
        if clip.w > W:
            x_center = clip.w / 2
            clip = clip.crop(x_center=x_center, width=W)
        clips.append(clip)
        total += clip.duration
        i += 1

    full = concatenate_videoclips(clips, method="compose")
    return full.subclip(0, target_duration)


def assemble_video(
    broll_paths: list[str],
    voiceover_path: str,
    subtitle_segments: list[dict],
    target_duration: float,
    output_path: str,
) -> str:
    voice_audio = AudioFileClip(voiceover_path)
    actual_duration = min(target_duration, voice_audio.duration)

    background = _prepare_broll_track(broll_paths, actual_duration)
    subtitles = _make_subtitle_clips(subtitle_segments)

    final = CompositeVideoClip([background, *subtitles], size=(W, H))
    final = final.set_audio(voice_audio.subclip(0, actual_duration))
    final = final.set_duration(actual_duration)

    final.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
    )
    return output_path
