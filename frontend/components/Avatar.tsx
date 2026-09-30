import { Person } from "@/lib/api";

const fills = [
  { bg: "#fc5000", fg: "#ffffff" },
  { bg: "#f7f6f2", fg: "#070607" },
  { bg: "#f5f28e", fg: "#070607" },
  { bg: "#070607", fg: "#ffffff" },
  { bg: "#e2e2df", fg: "#070607" },
];

function fillFor(id: string) {
  let sum = 0;
  for (const ch of id) sum += ch.charCodeAt(0);
  return fills[sum % fills.length];
}

// No real photos are hotlinked, so each person gets a monogram portrait. `arch` gives the tall arched frame.
export default function Avatar({ person, size = 48, arch = false }: { person: Person; size?: number; arch?: boolean }) {
  const initials = person.name.split(" ").map((w) => w[0]).slice(0, 2).join("");
  const fill = fillFor(person.id);
  return (
    <div
      className="flex shrink-0 items-center justify-center"
      style={{
        width: size,
        height: arch ? size * 1.3 : size,
        fontSize: size * (arch ? 0.42 : 0.42),
        fontFamily: '"Bebas Neue", Impact, sans-serif',
        letterSpacing: "0.02em",
        background: fill.bg,
        color: fill.fg,
        borderRadius: arch ? "800px 800px 28px 28px" : 800,
      }}
    >
      {initials}
    </div>
  );
}
