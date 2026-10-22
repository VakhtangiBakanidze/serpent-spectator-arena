import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { api, type ScoreEntry } from "@/lib/api";
import type { Mode } from "@/lib/snake";

export const Route = createFileRoute("/leaderboard")({
  head: () => ({
    meta: [
      { title: "Leaderboard — Snake" },
      { name: "description", content: "Top snake scores in walls and pass-through modes." },
      { property: "og:title", content: "Leaderboard — Snake" },
      { property: "og:description", content: "Top snake scores in walls and pass-through modes." },
    ],
  }),
  component: Leaderboard,
});

function Leaderboard() {
  const [mode, setMode] = useState<Mode | undefined>();
  const [rows, setRows] = useState<ScoreEntry[] | null>(null);
  useEffect(() => {
    setRows(null);
    api.getLeaderboard(mode).then(setRows);
  }, [mode]);

  return (
    <main className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="mb-6 font-display text-2xl text-primary glow">LEADERBOARD</h1>
      <div className="mb-4 flex gap-2">
        {([undefined, "walls", "pass-through"] as const).map((m) => (
          <button key={m ?? "all"} className={mode === m ? "btn-primary" : "btn-ghost"} onClick={() => setMode(m)}>
            {m ?? "All"}
          </button>
        ))}
      </div>
      <div className="panel">
        {!rows ? (
          <p className="text-muted-foreground">Loading…</p>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="text-muted-foreground">
              <tr><th className="py-2">#</th><th>Player</th><th>Mode</th><th className="text-right">Score</th></tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i} className="border-t border-border">
                  <td className="py-2 font-display text-accent">{i + 1}</td>
                  <td>{r.username}</td>
                  <td className="text-muted-foreground">{r.mode}</td>
                  <td className="text-right font-display text-primary">{r.score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </main>
  );
}
