import { Person } from "@/lib/api";

const sections: { key: Exclude<keyof Person["profile"], "summary">; title: string }[] = [
  { key: "needs", title: "Needs" },
  { key: "interests", title: "Interests" },
  { key: "hobbies", title: "Hobbies" },
  { key: "values", title: "Values" },
  { key: "personality", title: "Personality" },
  { key: "lifestyle", title: "Lifestyle" },
  { key: "communication_style", title: "Communication Style" },
  { key: "career_orientation", title: "Career Orientation" },
  { key: "dating_preferences", title: "Dating Preferences" },
];

function list(items: string[]) {
  if (items.length < 2) return items.join("");
  return items.slice(0, -1).join(", ") + " and " + items[items.length - 1];
}

// The agent's read is composed from the structured profile so it always matches the tags shown.
export function interpretation(person: Person) {
  const p = person.profile;
  const first = person.name.split(" ")[0];
  const needs = p.needs && p.needs.length ? `Needs: ${list(p.needs.slice(0, 3))}. ` : "";
  return `${needs}${first} reads as ${list(p.personality.slice(0, 3))}, drawn to ${list(p.interests.slice(0, 3))}. ` +
    `Values of ${list(p.values.slice(0, 3))} shape the choices, and free time goes to ${list(p.hobbies.slice(0, 3))}. ` +
    `In conversation ${first} is ${list(p.communication_style.slice(0, 2))}, and the day to day looks ${list(p.lifestyle.slice(0, 2))}. ` +
    `A partner who is ${list(p.dating_preferences.slice(0, 3))} would fit best.`;
}

export default function ProfileAnalysis({ person }: { person: Person }) {
  return (
    <div className="space-y-5">
      <div className="card-ember">
        <div className="label">Agent's read</div>
        <p className="mt-3 text-2xl leading-snug md:text-3xl">{person.profile.summary}</p>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        {sections.filter((s) => (person.profile[s.key] ?? []).length > 0).map((s) => (
          <div key={s.key} className="card-sm !p-6">
            <div className="h3 mb-3">{s.title}</div>
            <div>{(person.profile[s.key] ?? []).map((t) => <span key={t} className="tag">{t}</span>)}</div>
          </div>
        ))}
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        <div className="card-sm !p-6">
          <div className="h3 mb-3">LinkedIn signals</div>
          <ul className="space-y-2 text-[15px] leading-snug">
            {person.source_evidence.linkedin.map((e) => <li key={e} className="flex gap-2"><span className="text-ember">●</span>{e}</li>)}
          </ul>
        </div>
        <div className="card-sm !p-6">
          <div className="h3 mb-3">Instagram signals</div>
          <ul className="space-y-2 text-[15px] leading-snug">
            {person.source_evidence.instagram.map((e) => <li key={e} className="flex gap-2"><span className="text-ember">●</span>{e}</li>)}
          </ul>
        </div>
      </div>

      {person.verification && person.verification.length > 0 && (
        <div className="card-sm !p-6">
          <div className="h3 mb-3">Identity check</div>
          <p className="mb-2 text-sm opacity-70">Both links were scraped and cross-checked to confirm they belong to the same person.</p>
          <ul className="space-y-1.5 text-[15px] leading-snug">
            {person.verification.map((v) => <li key={v} className="flex gap-2"><span className="text-ember">✓</span>{v}</li>)}
          </ul>
        </div>
      )}

      <div className="card-dark">
        <div className="label opacity-70">Agent interpretation</div>
        <p className="mt-3 max-w-3xl text-xl leading-snug">{interpretation(person)}</p>
      </div>
    </div>
  );
}
