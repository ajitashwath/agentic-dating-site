// Empty means same origin: on Vercel the /api/* rewrite routes to the backend service.
// Locally frontend/.env.local points this at the uvicorn server.
export const API = process.env.NEXT_PUBLIC_API_URL ?? "";

export type Profile = {
  summary: string;
  needs?: string[];
  interests: string[];
  hobbies: string[];
  values: string[];
  personality: string[];
  lifestyle: string[];
  communication_style: string[];
  career_orientation: string[];
  dating_preferences: string[];
};

export type Person = {
  id: string;
  name: string;
  role: string;
  linkedin: string;
  instagram: string;
  profile: Profile;
  source_evidence: { linkedin: string[]; instagram: string[] };
  verification?: string[];
  live?: boolean;
};

export type Message = { speaker: string; agent: string; text: string };

export type DateSummary = { id: string; person_a: string; person_b: string; compatibility: number };

export type DateResult = DateSummary & {
  messages: Message[];
  a_to_b: number;
  b_to_a: number;
  shared_interests: string[];
  shared: Record<string, string[]>;
  strengths: string[];
  friction: string[];
  verdict: string;
  generated_by?: "gemini" | "template";
};

export type Ranking = {
  rank: number;
  person_id: string;
  score: number;
  mutual: number;
  date_id: string | null;
  why: string;
};

export async function api<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(API + path, body === undefined ? undefined : {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
  return data as T;
}

export function firstName(person: Person) {
  return person.name.split(" ")[0];
}

const gradients = [
  "from-violet-500 to-fuchsia-500",
  "from-cyan-400 to-blue-500",
  "from-pink-500 to-orange-400",
  "from-emerald-400 to-cyan-500",
  "from-amber-400 to-rose-500",
  "from-indigo-500 to-sky-400",
  "from-fuchsia-500 to-purple-600",
  "from-lime-400 to-emerald-500",
];

export function gradientFor(id: string) {
  let sum = 0;
  for (const ch of id) sum += ch.charCodeAt(0);
  return gradients[sum % gradients.length];
}
