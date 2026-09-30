"use client";

import { useEffect, useRef, useState } from "react";
import { Message, Person } from "@/lib/api";
import Avatar from "./Avatar";

type Props = { messages: Message[]; a: Person; b: Person; onDone: () => void };

// Messages are already stored; this only reveals them one by one so the date feels live.
export default function AgentChat({ messages, a, b, onDone }: Props) {
  const [shown, setShown] = useState(0);
  const bottom = useRef<HTMLDivElement>(null);
  const done = shown >= messages.length;

  useEffect(() => {
    if (done) {
      onDone();
      return;
    }
    const timer = setTimeout(() => setShown((n) => n + 1), 1300);
    return () => clearTimeout(timer);
  }, [shown, done]);

  useEffect(() => {
    if (shown > 0) bottom.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [shown]);

  const typing = messages[shown];
  const bubble = (left: boolean) => `px-6 py-4 ${left ? "bg-limestone rounded-[28px] rounded-bl-md" : "bg-obsidian text-white rounded-[28px] rounded-br-md"}`;

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      {messages.slice(0, shown).map((m, i) => {
        const left = m.speaker === a.id;
        return (
          <div key={i} className={`rise flex items-end gap-3 ${left ? "" : "flex-row-reverse"}`}>
            <Avatar person={left ? a : b} size={44} />
            <div className={`max-w-[82%] ${bubble(left)}`}>
              <div className="label mb-1 opacity-60">{m.agent}</div>
              <p className="text-[17px] leading-relaxed">{m.text}</p>
            </div>
          </div>
        );
      })}
      {!done && typing && (
        <div className={`flex items-end gap-3 ${typing.speaker === a.id ? "" : "flex-row-reverse"}`}>
          <Avatar person={typing.speaker === a.id ? a : b} size={44} />
          <div className={`flex gap-1.5 !py-5 ${bubble(typing.speaker === a.id)}`}>
            {[0, 1, 2].map((d) => <span key={d} className="blink h-2 w-2 rounded-full bg-current" style={{ animationDelay: `${d * 0.2}s` }} />)}
          </div>
        </div>
      )}
      <div ref={bottom} />
      {!done && <div className="text-center"><button onClick={() => setShown(messages.length)} className="btn text-sm">Skip to the end</button></div>}
    </div>
  );
}
