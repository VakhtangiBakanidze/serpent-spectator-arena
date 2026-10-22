import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { api, type LivePlayer } from "@/lib/api";
import { botDirection, changeDirection, createGame, step } from "@/lib/snake";
import { Board } from "@/components/Board";

export const Route = createFileRoute("/watch")({
  head: () => ({
    meta: [
      { title: "Watch live — Snake" },
      { name: "description", content: "Follow other snake players in real time." },
      { property: "og:title", content: "Watch live — Snake" },
      { property: "og:description", content: "Follow other snake players in real time." },
    ],
  }),
  component: Watch,
});

function Watch() {
  const [players, setPlayers] = useState<LivePlayer[]>([]);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    api.getLivePlayers().then((p) => {
      setPlayers(p);
      setSelected(p[0]?.id ?? null);
    });
  }, []);

  // Simulate every live player with the bot.
  useEffect(() => {
    const t = setInterval(() => {
      setPlayers((ps) =>
        ps.map((p) => {
          const s = p.state.alive ? step(changeDirection(p.state, botDirection(p.state))) : createGame(p.mode);
          return { ...p, state: s };
        }),
      );
    }, 140);
    return () => clearInterval(t);
  }, []);

  const current = players.find((p) => p.id === selected);

  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-6 px-4 py-10 md:flex-row">
      <aside className="panel md:w-60">
        <h2 className="mb-3 font-display text-sm text-accent">LIVE NOW</h2>
        <ul className="flex flex-col gap-2">
          {players.map((p) => (
            <li key={p.id}>
              <button
                onClick={() => setSelected(p.id)}
                className={`w-full text-left ${p.id === selected ? "btn-primary" : "btn-ghost"}`}
              >
                <span className="live-dot" /> {p.username} · {p.state.score}
              </button>
            </li>
          ))}
        </ul>
      </aside>
      {current && (
        <section className="flex flex-col items-center gap-3">
          <p className="font-display text-sm">
            WATCHING <span className="text-primary">{current.username}</span> · {current.mode} · SCORE{" "}
            <span className="text-primary">{current.state.score}</span>
          </p>
          <Board state={current.state} />
        </section>
      )}
    </main>
  );
}
