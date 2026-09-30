"use client";

import Link from "next/link";
import { useState } from "react";
import { api, Person } from "@/lib/api";
import ProfileAnalysis from "@/components/ProfileAnalysis";
import Avatar from "@/components/Avatar";

const linkedinRe = /^https?:\/\/([a-z]{2,3}\.)?linkedin\.com\/in\/[\w\-%]+\/?(\?.*)?$/i;
const instagramRe = /^https?:\/\/(www\.)?instagram\.com\/[\w.]+\/?(\?.*)?$/i;

const steps = ["Collecting LinkedIn data", "Collecting Instagram data", "Verifying identity and analyzing", "Building agent", "Done"];

export default function CreatePage() {
  const [linkedin, setLinkedin] = useState("");
  const [instagram, setInstagram] = useState("");
  const [step, setStep] = useState(-1);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState<Person | null>(null);

  const linkedinOk = linkedinRe.test(linkedin.trim());
  const instagramOk = instagramRe.test(instagram.trim());
  const running = step >= 0 && step < 4 && !error;

  // Editing a field clears the last error and progress, unless a run is in flight.
  function reset() {
    if (running) return;
    setError("");
    setStep(-1);
    setSaved(null);
  }

  async function analyze() {
    setError("");
    setSaved(null);
    if (!linkedinOk) return setError("Enter a LinkedIn profile URL like https://www.linkedin.com/in/username");
    if (!instagramOk) return setError("Enter an Instagram profile URL like https://www.instagram.com/username");
    try {
      setStep(0);
      const li = await api<Record<string, unknown>>("/api/scrape", { source: "linkedin", url: linkedin.trim() });
      setStep(1);
      const ig = await api<Record<string, unknown>>("/api/scrape", { source: "instagram", url: instagram.trim() });
      setStep(2);
      const draft = await api<Person>("/api/analyze", { linkedin: li, instagram: ig });
      setStep(3);
      const person = await api<Person>("/api/people", draft);
      setSaved(person);
      setStep(4);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div>
      <div className="text-center">
        <h1 className="display-md">Create your agent</h1>
        <p className="mx-auto mt-3 max-w-xl text-lg leading-snug">Paste a public LinkedIn and a public Instagram profile. Apify fetches them and Gemini builds the profile.</p>
      </div>

      <div className="card-dark mx-auto mt-8 max-w-3xl space-y-6">
        <div>
          <label className="label opacity-70">LinkedIn URL</label>
          <input value={linkedin} onChange={(e) => { setLinkedin(e.target.value); reset(); }} placeholder="https://www.linkedin.com/in/username"
            className="mt-2 w-full rounded-full border-[1.5px] border-white bg-transparent px-8 py-5 text-lg text-white outline-none placeholder:text-white/40 focus:border-ember" />
          {linkedin && !linkedinOk && <div className="mt-2 pl-4 text-sm text-ember">Not a valid LinkedIn profile URL.</div>}
        </div>
        <div>
          <label className="label opacity-70">Instagram URL</label>
          <input value={instagram} onChange={(e) => { setInstagram(e.target.value); reset(); }} placeholder="https://www.instagram.com/username"
            className="mt-2 w-full rounded-full border-[1.5px] border-white bg-transparent px-8 py-5 text-lg text-white outline-none placeholder:text-white/40 focus:border-ember" />
          {instagram && !instagramOk && <div className="mt-2 pl-4 text-sm text-ember">Not a valid Instagram profile URL.</div>}
        </div>
        <button onClick={analyze} disabled={running} className="btn btn-solid w-full !py-4">{running ? "ANALYZING..." : "ANALYZE PERSON"}</button>
      </div>

      {step >= 0 && (
        <div className="card-sm mx-auto mt-5 max-w-3xl !p-6">
          {steps.map((label, i) => {
            const failed = error && i === step;
            const complete = i < step || step === 4;
            const active = i === step && !error && step < 4;
            return (
              <div key={label} className={`flex items-center gap-4 py-2 ${complete || active || failed ? "" : "opacity-35"}`}>
                <span className={`flex h-8 w-8 items-center justify-center rounded-full text-sm ${failed ? "bg-ember text-white" : complete ? "bg-obsidian text-white" : active ? "animate-pulse bg-sulfur" : "bg-pumice"}`}>
                  {failed ? "!" : complete ? "✓" : i + 1}
                </span>
                <span className="text-lg">{label}</span>
              </div>
            );
          })}
        </div>
      )}

      {error && (
        <div className="card-ember mx-auto mt-5 max-w-3xl !p-6">
          <div className="h3">Live analysis failed</div>
          <p className="mt-2 text-lg leading-snug">{error}</p>
          <p className="mt-2 text-sm opacity-80">The demo people are unaffected and still work.</p>
        </div>
      )}

      {saved && (
        <div className="mt-10">
          <div className="halftone flex flex-col items-center px-4 py-8 text-center">
            <Avatar person={saved} size={120} arch />
            <div className="display-md mt-4">{saved.name}</div>
            <div>{saved.role}</div>
            <div className="mt-5 flex gap-3">
              <Link href={`/person/${saved.id}`} className="btn !border-white text-white hover:!bg-white hover:!text-obsidian">Open profile</Link>
              <Link href={`/rankings?p=${saved.id}`} className="btn btn-solid !bg-limestone !border-limestone">See matches</Link>
            </div>
          </div>
          <div className="mt-5"><ProfileAnalysis person={saved} /></div>
        </div>
      )}
    </div>
  );
}
