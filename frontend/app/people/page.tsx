"use client";

import { useEffect, useState } from "react";
import { api, Person } from "@/lib/api";
import PersonCard from "@/components/PersonCard";

export default function PeoplePage() {
  const [people, setPeople] = useState<Person[]>([]);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");

  useEffect(() => {
    api<Person[]>("/api/people").then(setPeople).catch((e) => setError(e.message));
  }, []);

  const shown = people.filter((p) => (p.name + p.role).toLowerCase().includes(query.toLowerCase()));

  return (
    <div>
      <div className="text-center">
        <h1 className="display-md">The people</h1>
        <p className="mx-auto mt-3 max-w-xl text-lg leading-snug">{people.length} real public figures. Each has an agent that has read their LinkedIn and Instagram.</p>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search name or role"
          className="pill-input mt-6 !max-w-md text-center"
        />
      </div>
      {error && <p className="mt-8 text-center">Could not reach the backend: {error}. Start it with uvicorn on port 8000.</p>}
      <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {shown.map((p, i) => <PersonCard key={p.id} person={p} index={i} />)}
      </div>
    </div>
  );
}
