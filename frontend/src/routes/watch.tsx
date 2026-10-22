import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { useWebSocketLivePlayers } from "@/lib/websocket";
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
  const players = useWebSocketLivePlayers();
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const selected = players.find((p) => p.id === (selectedId ?? players[0]?.id));

  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-6 px-4 py-10 md:flex-row">
      <aside className="panel md:w-60">
        <h2 className="mb-3 font-display text-sm text-accent">LIVE NOW</h2>
        {players.length === 0 ? (
          <p className="text-sm text-muted-foreground">Connecting…</p>
        ) : (
          <ul className="flex flex-col gap-2">
            {players.map((p) => (
              <li key={p.id}>
                <button
                  onClick={() => setSelectedId(p.id)}
                  className={`w-full text-left ${p.id === selected?.id ? "btn-primary" : "btn-ghost"}`}
                >
                  <span className="live-dot" /> {p.username} · {p.state.score}
                </button>
              </li>
            ))}
          </ul>
        )}
      </aside>
      {selected && (
        <section className="flex flex-col items-center gap-3">
          <p className="font-display text-sm">
            WATCHING <span className="text-primary">{selected.username}</span> · {selected.mode} · SCORE{" "}
            <span className="text-primary">{selected.state.score}</span>
          </p>
          <Board state={selected.state} />
        </section>
      )}
    </main>
  );
}
