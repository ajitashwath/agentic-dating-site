export default function ScoreRing({ value, label = "match" }: { value: number; label?: string }) {
  return (
    <div className="card-ember text-center">
      <div className="label">{label}</div>
      <div className="display-md mt-1" style={{ fontSize: 88 }}>{value}%</div>
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/30">
        <div className="h-full rounded-full bg-white" style={{ width: `${value}%`, transition: "width 1.2s ease-out" }} />
      </div>
    </div>
  );
}
