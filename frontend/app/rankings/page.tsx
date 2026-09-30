"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, firstName, Person, Ranking } from "@/lib/api";
import Avatar from "@/components/Avatar";

export default function RankingsPage() {
  const [people, setPeople] = useState<Person[]>([]);
  const [personId, setPersonId] = useState("");
  const [rankings, setRankings] = useState<Ranking[]>([]);
  const [matchId, setMatchId] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    api<Person[]>("/api/people").then((list) => {
      setPeople(list);
      setPersonId(params.get("p") || list[0].id);
      setMatchId(params.get("m") || "");
    }).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    if (!personId) return;
    api<Ranking[]>(`/api/rankings/${personId}`).then((r) => {
      setRankings(r);
      setMatchId((current) => (r.some((x) => x.person_id === current) ? current : r[0].person_id));
    }).catch((e) => setError(e.message));
  }, [personId]);

  if (error) return <p className="pt-10 text-center">{error}</p>;

  const person = people.find((p) => p.id === personId);
  const selected = rankings.find((r) => r.person_id === matchId);
  const other = people.find((p) => p.id === matchId);

  return (
    <div>
      <div className="text-center">
        <h1 className="display-md">Ranked matches</h1>
        <p className="mx-auto mt-3 max-w-xl text-lg leading-snug">Rankings are directional. Who they rank first does not have to rank them first.</p>
        <div className="mt-5 flex flex-wrap items-center justify-center gap-3">
          <span className="label">Rankings for</span>
          <select value={personId} onChange={(e) => setPersonId(e.target.value)} className="pill-input !w-auto !py-3 !text-base">
            {people.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          {person && <Link href={`/person/${person.id}`} className="btn !py-3 text-sm">Open profile</Link>}
        </div>
      </div>

      <div className="mt-10 grid gap-5 lg:grid-cols-[1fr_1.1fr]">
        <div className="card !p-4 md:!p-5">
          {rankings.map((r) => {
            const p = people.find((x) => x.id === r.person_id);
            if (!p) return null;
            const active = r.person_id === matchId;
            return (
              <button
                key={r.person_id}
                onClick={() => setMatchId(r.person_id)}
                className={`mb-1.5 flex w-full items-center gap-3 rounded-full py-2 pl-3 pr-5 text-left transition ${active ? "bg-obsidian text-white" : "hover:bg-pumice"}`}
              >
                <span className="h3 w-8 text-center !text-[26px]">{r.rank}</span>
                <Avatar person={p} size={40} />
                <div className="min-w-0 flex-1">
                  <div className="truncate">{p.name}</div>
                  <div className={`mt-1 h-1.5 overflow-hidden rounded-full ${active ? "bg-white/25" : "bg-pumice"}`}>
                    <div className="h-full rounded-full bg-ember" style={{ width: `${r.score}%` }} />
                  </div>
                </div>
                <span className="h3 !text-[28px]">{r.score}%</span>
              </button>
            );
          })}
        </div>

        {selected && other && person && (
          <div key={matchId} className="rise h-fit lg:sticky lg:top-6">
            <div className="halftone flex flex-col items-center px-4 py-8 text-center">
              <Avatar person={other} size={120} arch />
              <div className="label mt-4 opacity-90">#{selected.rank} for {firstName(person)}</div>
              <div className="display-md">{other.name}</div>
              <div className="text-sm">{other.role}</div>
            </div>
            <div className="mt-5 grid grid-cols-2 gap-5">
              <div className="card-ember text-center !p-6">
                <div className="display-md" style={{ fontSize: 72 }}>{selected.score}%</div>
                <div className="label">{firstName(person)}'s score</div>
              </div>
              <div className="card text-center !p-6">
                <div className="display-md" style={{ fontSize: 72 }}>{selected.mutual}%</div>
                <div className="label">Mutual</div>
              </div>
            </div>
            <div className="card mt-5 !p-6">
              <div className="h3 mb-2">Why they match</div>
              <p className="text-lg leading-snug">{selected.why}</p>
              <div className="mt-5 flex flex-wrap gap-3">
                {selected.date_id ? (
                  <Link href={`/dating?id=${selected.date_id}`} className="btn btn-solid">View date →</Link>
                ) : (
                  <span className="btn cursor-default opacity-60">Not dated yet</span>
                )}
                <Link href={`/person/${other.id}`} className="btn">Profile</Link>
                <Link href={`/rankings?p=${other.id}&m=${person.id}`} className="btn">{firstName(other)}'s view</Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
