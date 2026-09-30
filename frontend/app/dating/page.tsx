"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { api, DateResult, DateSummary, Person } from "@/lib/api";
import AgentChat from "@/components/AgentChat";
import Avatar from "@/components/Avatar";
import Heart from "@/components/Heart";
import ScoreRing from "@/components/ScoreRing";
import { useNarrow } from "@/lib/useNarrow";

export default function DatingPage() {
  const [people, setPeople] = useState<Person[]>([]);
  const [date, setDate] = useState<DateResult | null>(null);
  const [finished, setFinished] = useState(false);
  const [error, setError] = useState("");
  const narrow = useNarrow();
  const summaries = useRef<DateSummary[]>([]);
  const seen = useRef<string[]>([]);

  function open(id: string) {
    setFinished(false);
    setDate(null);
    seen.current.push(id);
    api<DateResult>(`/api/dates/${id}`).then(setDate).catch((e) => setError(e.message));
  }

  useEffect(() => {
    api<Person[]>("/api/people").then(setPeople).catch((e) => setError(e.message));
    api<DateSummary[]>("/api/dates").then((list) => {
      summaries.current = list;
      const wanted = new URLSearchParams(window.location.search).get("id");
      open(wanted || list[Math.floor(Math.random() * list.length)].id);
    }).catch((e) => setError(e.message));
  }, []);

  function nextDate() {
    // Never repeat a date until all 300 have been watched.
    const fresh = summaries.current.filter((d) => !seen.current.includes(d.id));
    const pool = fresh.length ? fresh : summaries.current;
    open(pool[Math.floor(Math.random() * pool.length)].id);
  }

  if (error) return <p className="pt-10 text-center">{error}</p>;

  const a = date && people.find((p) => p.id === date.person_a);
  const b = date && people.find((p) => p.id === date.person_b);

  return (
    <div>
      <div className="text-center">
        <h1 className="display-md">Watch agents date</h1>
        <p className="mx-auto mt-3 max-w-xl text-lg leading-snug">Each date is a stored conversation between two agents, written from both real profiles.</p>
        <button onClick={nextDate} className="btn btn-solid mt-5">NEXT DATE →</button>
      </div>

      {!(date && a && b) ? (
        <p className="mt-12 text-center">Setting up the table...</p>
      ) : (
        <div key={date.id} className="mt-8">
          <div className="halftone flex items-end justify-center gap-4 px-4 py-10 text-center md:gap-14">
            <Link href={`/person/${a.id}`} className="flex flex-col items-center">
              <Avatar person={a} size={narrow ? 92 : 150} arch />
              <div className="h3 mt-3 !text-[26px] sm:!text-[34px]">{a.name}</div>
              <div className="max-w-[130px] text-xs leading-tight opacity-90 sm:max-w-[220px] sm:text-sm">{a.role}</div>
            </Link>
            <div className="mb-12 flex flex-col items-center sm:mb-16">
              <Heart size={narrow ? 30 : 52} color="#ffffff" />
              <div className="label mt-2">first date</div>
            </div>
            <Link href={`/person/${b.id}`} className="flex flex-col items-center">
              <Avatar person={b} size={narrow ? 92 : 150} arch />
              <div className="h3 mt-3 !text-[26px] sm:!text-[34px]">{b.name}</div>
              <div className="max-w-[130px] text-xs leading-tight opacity-90 sm:max-w-[220px] sm:text-sm">{b.role}</div>
            </Link>
          </div>

          {date.generated_by === "template" && (
            <p className="card-sm mt-5 text-center text-sm">
              Scripted preview. This pair has not been dated by Gemini agents yet, the conversation is assembled from both real profiles.
            </p>
          )}

          <div className="mt-8">
            <AgentChat messages={date.messages} a={a} b={b} onDone={() => setFinished(true)} />
          </div>

          {finished && (
            <div className="rise mt-8">
              <div className="grid gap-5 md:grid-cols-3">
                <div>
                  <ScoreRing value={date.compatibility} label="compatible" />
                  <p className="mt-3 text-center text-sm">
                    {a.name.split(" ")[0]} to {b.name.split(" ")[0]}: {date.a_to_b}%<br />
                    {b.name.split(" ")[0]} to {a.name.split(" ")[0]}: {date.b_to_a}%
                  </p>
                </div>
                <div className="card !p-6">
                  <div className="h3 mb-3">Shared interests</div>
                  <div>
                    {date.shared_interests.length
                      ? date.shared_interests.map((t) => <span key={t} className="tag">{t}</span>)
                      : <span>None. An opposites-attract date.</span>}
                  </div>
                  <div className="h3 mb-3 mt-5">Strengths</div>
                  <ul className="space-y-1.5 text-[15px] leading-snug">{date.strengths.map((s) => <li key={s}>+ {s}</li>)}</ul>
                </div>
                <div className="card !p-6">
                  <div className="h3 mb-3">Potential friction</div>
                  <ul className="space-y-1.5 text-[15px] leading-snug">{date.friction.map((s) => <li key={s}>! {s}</li>)}</ul>
                  <div className="h3 mb-3 mt-5">Agent verdict</div>
                  <p className="leading-snug">{date.verdict}</p>
                </div>
              </div>
              <div className="mt-6 flex flex-wrap justify-center gap-3">
                <Link href={`/rankings?p=${a.id}&m=${b.id}`} className="btn">{a.name.split(" ")[0]}'s ranking of {b.name.split(" ")[0]}</Link>
                <Link href={`/rankings?p=${b.id}&m=${a.id}`} className="btn">{b.name.split(" ")[0]}'s ranking of {a.name.split(" ")[0]}</Link>
                <button onClick={nextDate} className="btn btn-solid">NEXT DATE →</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
