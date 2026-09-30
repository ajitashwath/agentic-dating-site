import Link from "next/link";
import { Person } from "@/lib/api";
import Avatar from "./Avatar";

export default function PersonCard({ person, index = 0 }: { person: Person; index?: number }) {
  return (
    <Link
      href={`/person/${person.id}`}
      className="rise group card flex flex-col items-center text-center transition-transform duration-300 hover:-translate-y-1.5 !p-6"
      style={{ animationDelay: `${Math.min(index, 12) * 40}ms` }}
    >
      <Avatar person={person} size={150} arch />
      <div className="h3 mt-5 !text-[34px]">{person.name}</div>
      <div className="mt-2 min-h-[2.6rem] text-sm leading-snug opacity-70">{person.role}</div>
      <p className="mt-2 text-sm leading-snug">{person.profile.summary}</p>
      <div className="mt-4">
        {person.profile.interests.slice(0, 3).map((t) => <span key={t} className="tag">{t}</span>)}
        {person.live && <span className="tag !bg-ember !text-white">live</span>}
      </div>
    </Link>
  );
}
