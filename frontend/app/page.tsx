"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, DateResult, DateSummary, Person } from "@/lib/api";
import Avatar from "@/components/Avatar";
import Heart from "@/components/Heart";
import { useNarrow } from "@/lib/useNarrow";

export default function Home() {
  const narrow = useNarrow();
  const [people, setPeople] = useState<Person[]>([]);
  const [dates, setDates] = useState<DateSummary[]>([]);
  const [best, setBest] = useState<DateResult | null>(null);

  useEffect(() => {
    api<Person[]>("/api/people").then(setPeople).catch(() => {});
    api<DateSummary[]>("/api/dates").then((list) => {
      setDates(list);
      const top = [...list].sort((x, y) => y.compatibility - x.compatibility)[0];
      if (top) api<DateResult>(`/api/dates/${top.id}`).then(setBest);
    }).catch(() => {});
  }, []);

  const a = best && people.find((p) => p.id === best.person_a);
  const b = best && people.find((p) => p.id === best.person_b);
  const stats = [
    { n: people.length || "-", label: "people" },
    { n: people.length || "-", label: "agents" },
    { n: dates.length || "-", label: "dates" },
  ];

  return (
    <div>
      <section className="text-center">
        <span className="tag !mb-5">LinkedIn + Instagram in. Matches out.</span>
        <h1 className="display">AGENTS DATE.<br />HUMANS DON'T.</h1>
        <p className="mx-auto mt-6 max-w-2xl text-xl leading-snug">
          Every person has an AI agent. It reads their public profiles, goes on dates with every other agent, and comes back with a ranked list of who to meet.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Link href="/people" className="btn btn-solid">Explore People</Link>
          <Link href={best ? `/dating?id=${best.id}` : "/dating"} className="btn">Watch Agents Date</Link>
          <Link href="/create" className="btn">Create Person</Link>
        </div>
      </section>

      <section className="halftone mt-14 px-4 py-10 text-center md:py-14">
        {best && a && b ? (
          <>
            <div className="label opacity-90">Best date so far</div>
            <div className="mt-6 flex items-end justify-center gap-4 md:gap-14">
              <Link href={`/person/${a.id}`} className="flex flex-col items-center">
                <Avatar person={a} size={narrow ? 96 : 170} arch />
                <div className="h3 mt-3 !text-[24px] sm:!text-[34px]">{a.name}</div>
              </Link>
              <div className="mb-10 flex flex-col items-center rounded-[28px] bg-limestone px-3 py-3 text-obsidian sm:mb-14 sm:rounded-[40px] sm:px-6 sm:py-4">
                <Heart size={narrow ? 26 : 40} />
                <div className="display-md" style={{ fontSize: narrow ? 40 : 64 }}>{best.compatibility}%</div>
                <div className="label">match</div>
              </div>
              <Link href={`/person/${b.id}`} className="flex flex-col items-center">
                <Avatar person={b} size={narrow ? 96 : 170} arch />
                <div className="h3 mt-3 !text-[24px] sm:!text-[34px]">{b.name}</div>
              </Link>
            </div>
            <p className="mx-auto mt-8 max-w-2xl text-xl leading-snug">"{(best.messages[2] ?? best.messages[0]).text}"</p>
            <div className="label mt-3 opacity-80">{(best.messages[2] ?? best.messages[0]).agent}</div>
            <Link href={`/dating?id=${best.id}`} className="btn mt-6 !border-white text-white hover:!bg-white hover:!text-obsidian">Watch the full date</Link>
          </>
        ) : (
          <div className="h-[380px]" />
        )}
      </section>

      <section className="mt-5 grid gap-5 sm:grid-cols-3">
        {stats.map((s) => (
          <div key={s.label} className="card-ember text-center">
            <div className="label">{s.label}</div>
            <div className="display-md mt-1" style={{ fontSize: 96 }}>{s.n}</div>
          </div>
        ))}
      </section>

      <section className="card mt-5 text-center">
        <h2 className="display-sm">Meet the agents</h2>
        <div className="mt-8 grid grid-cols-2 gap-x-6 gap-y-8 sm:grid-cols-4">
          {people.slice(0, 8).map((p) => (
            <Link key={p.id} href={`/person/${p.id}`} className="group flex flex-col items-center">
              <div className="transition-transform duration-300 group-hover:-translate-y-2"><Avatar person={p} size={110} arch /></div>
              <div className="mt-3 group-hover:underline decoration-ember decoration-2 underline-offset-4">{p.name}</div>
              <div className="text-sm opacity-60">{p.role.split(",")[0]}</div>
            </Link>
          ))}
        </div>
        <Link href="/people" className="btn mt-8">See all {people.length} people</Link>
      </section>

      <section className="mt-5 grid gap-5 md:grid-cols-3">
        {[
          ["01", "Read", "The agent reads exactly two public sources: LinkedIn and Instagram."],
          ["02", "Date", "Agents hold real conversations about interests, values and lifestyle."],
          ["03", "Rank", "Deterministic scoring ranks every other person, with a reason for each match."],
        ].map(([n, title, text]) => (
          <div key={title} className="card text-center">
            <span className="tag">{n}</span>
            <div className="display-sm mt-2">{title}</div>
            <p className="mt-2 leading-snug">{text}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
