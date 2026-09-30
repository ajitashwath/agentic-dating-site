"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, Person, Ranking } from "@/lib/api";
import Avatar from "@/components/Avatar";
import { useNarrow } from "@/lib/useNarrow";
import ProfileAnalysis from "@/components/ProfileAnalysis";

export default function PersonPage({ params }: { params: { id: string } }) {
  const [person, setPerson] = useState<Person | null>(null);
  const [people, setPeople] = useState<Person[]>([]);
  const [top, setTop] = useState<Ranking[]>([]);
  const [error, setError] = useState("");
  const narrow = useNarrow();

  useEffect(() => {
    api<Person>(`/api/people/${params.id}`).then(setPerson).catch((e) => setError(e.message));
    api<Person[]>("/api/people").then(setPeople);
    api<Ranking[]>(`/api/rankings/${params.id}`).then((r) => setTop(r.slice(0, 5)));
  }, [params.id]);

  if (error) return <p className="pt-10 text-center">{error}</p>;
  if (!person) return <p className="pt-10 text-center">Loading profile...</p>;

  return (
    <div className="rise">
      <Link href="/people" className="btn !px-4 !py-2 text-sm">← All people</Link>

      <div className="halftone mt-5 flex flex-col items-center px-4 py-10 text-center">
        <Avatar person={person} size={narrow ? 120 : 170} arch />
        <h1 className="display-md mt-5">{person.name}</h1>
        <p className="mt-2 text-xl">{person.role}</p>
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          {person.linkedin && <a href={person.linkedin} target="_blank" rel="noreferrer" className="btn !border-white text-white hover:!bg-white hover:!text-obsidian">LinkedIn ↗</a>}
          {person.instagram && <a href={person.instagram} target="_blank" rel="noreferrer" className="btn !border-white text-white hover:!bg-white hover:!text-obsidian">Instagram ↗</a>}
          {top.find((r) => r.date_id) && <Link href={`/dating?id=${top.find((r) => r.date_id)!.date_id}`} className="btn btn-solid !bg-limestone !border-limestone">Watch a date</Link>}
          <Link href={`/rankings?p=${person.id}`} className="btn !border-white text-white hover:!bg-white hover:!text-obsidian">All rankings</Link>
        </div>
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-[1fr_340px]">
        <ProfileAnalysis person={person} />
        <aside className="card-sm h-fit !p-6 lg:sticky lg:top-6">
          <div className="h3 mb-3">Top matches</div>
          {top.map((r) => {
            const other = people.find((p) => p.id === r.person_id);
            if (!other) return null;
            return (
              <Link key={r.person_id} href={`/rankings?p=${person.id}&m=${r.person_id}`} className="group flex items-center gap-3 border-t border-dotted border-obsidian py-3">
                <Avatar person={other} size={40} />
                <span className="flex-1 truncate group-hover:underline decoration-ember decoration-2 underline-offset-4">{other.name}</span>
                <span className="tag !m-0 !bg-ember !text-white">{r.score}%</span>
              </Link>
            );
          })}
        </aside>
      </div>
    </div>
  );
}
