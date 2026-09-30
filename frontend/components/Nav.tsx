"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import Heart from "./Heart";

const links = [
  { href: "/people", label: "People" },
  { href: "/dating", label: "Dating" },
  { href: "/rankings", label: "Rankings" },
];

export default function Nav() {
  const path = usePathname();
  return (
    <header className="mx-auto max-w-[1280px] px-4 pt-4 md:px-6">
      <div className="flex items-center justify-between gap-1 rounded-full bg-limestone py-2 pl-4 pr-2 sm:pl-5">
        <Link href="/" className="flex items-center gap-2">
          <Heart size={24} />
          <span className="h3 hidden !text-[28px] sm:inline">agentdate</span>
        </Link>
        <nav className="flex items-center gap-1">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={`rounded-full px-2 py-2 text-sm transition hover:bg-pumice sm:px-3 md:px-4 md:text-base ${path.startsWith(l.href) ? "bg-pumice" : ""}`}
            >
              {l.label}
            </Link>
          ))}
        </nav>
        <Link href="/create" className="btn btn-solid !px-4 !py-2.5 text-sm md:text-base"><span className="sm:hidden">Create</span><span className="hidden sm:inline">Create Person</span></Link>
      </div>
    </header>
  );
}
