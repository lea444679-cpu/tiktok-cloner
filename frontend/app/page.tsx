"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Structure = {
  hook_type: string;
  hook_duration_seconds: number;
  structure: string[];
  pacing: string;
  cta_type: string;
  cta_position: string;
  tone: string;
  subtitle_style: string;
};

export default function Home() {
  const [tiktokUrl, setTiktokUrl] = useState("");
  const [newTopic, setNewTopic] = useState("");
  const [duration, setDuration] = useState(30);

  const [structure, setStructure] = useState<Structure | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [step, setStep] = useState<"idle" | "analyzing" | "analyzed" | "generating" | "done" | "error">("idle");
  const [error, setError] = useState("");

  async function handleAnalyze() {
    setStep("analyzing");
    setError("");
    try {
      const res = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tiktok_url: tiktokUrl }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Erreur d'analyse");
      const data = await res.json();
      setStructure(data.structure);
      setStep("analyzed");
    } catch (e: any) {
      setError(e.message);
      setStep("error");
    }
  }

  async function handleGenerate() {
    setStep("generating");
    setError("");
    try {
      const res = await fetch(`${API_URL}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tiktok_url: tiktokUrl,
          new_topic: newTopic,
          target_duration: duration,
        }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Erreur de génération");
      const data = await res.json();
      setVideoUrl(`${API_URL}${data.video_url}`);
      setStep("done");
    } catch (e: any) {
      setError(e.message);
      setStep("error");
    }
  }

  return (
    <main className="max-w-2xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold mb-2">Clone de structure TikTok</h1>
      <p className="text-neutral-400 mb-8">
        Colle un lien TikTok, choisis un nouveau sujet et une durée. On garde le hook,
        le rythme et le CTA qui marchent — le contenu, lui, est entièrement nouveau.
      </p>

      <div className="space-y-4 bg-neutral-900 p-6 rounded-2xl">
        <div>
          <label className="block text-sm mb-1 text-neutral-300">Lien TikTok</label>
          <input
            value={tiktokUrl}
            onChange={(e) => setTiktokUrl(e.target.value)}
            placeholder="https://www.tiktok.com/@user/video/..."
            className="w-full bg-neutral-800 rounded-lg px-3 py-2 outline-none focus:ring-2 ring-pink-500"
          />
        </div>

        <button
          onClick={handleAnalyze}
          disabled={!tiktokUrl || step === "analyzing"}
          className="bg-pink-600 hover:bg-pink-500 disabled:opacity-40 px-4 py-2 rounded-lg font-medium"
        >
          {step === "analyzing" ? "Analyse en cours..." : "1. Analyser la vidéo"}
        </button>

        {structure && (
          <div className="bg-neutral-800 rounded-lg p-4 text-sm space-y-1">
            <p><span className="text-neutral-400">Hook détecté :</span> {structure.hook_type}</p>
            <p><span className="text-neutral-400">Ton :</span> {structure.tone}</p>
            <p><span className="text-neutral-400">CTA :</span> {structure.cta_type} ({structure.cta_position})</p>
            <p><span className="text-neutral-400">Rythme :</span> {structure.pacing}</p>
          </div>
        )}

        {structure && (
          <>
            <div>
              <label className="block text-sm mb-1 text-neutral-300">Nouveau sujet</label>
              <input
                value={newTopic}
                onChange={(e) => setNewTopic(e.target.value)}
                placeholder="ex: les avantages du café le matin"
                className="w-full bg-neutral-800 rounded-lg px-3 py-2 outline-none focus:ring-2 ring-pink-500"
              />
            </div>

            <div>
              <label className="block text-sm mb-1 text-neutral-300">
                Durée cible : {duration}s
              </label>
              <input
                type="range"
                min={10}
                max={90}
                value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value))}
                className="w-full"
              />
            </div>

            <button
              onClick={handleGenerate}
              disabled={!newTopic || step === "generating"}
              className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 px-4 py-2 rounded-lg font-medium"
            >
              {step === "generating" ? "Génération en cours (peut prendre 1-2 min)..." : "2. Générer la vidéo"}
            </button>
          </>
        )}

        {error && <p className="text-red-400 text-sm">{error}</p>}

        {videoUrl && (
          <video src={videoUrl} controls className="w-full rounded-lg mt-4" />
        )}
      </div>
    </main>
  );
}
