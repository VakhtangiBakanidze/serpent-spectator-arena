import { createFileRoute } from "@tanstack/react-router";
import { SnakeGame } from "@/components/SnakeGame";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Play Snake — Walls or Pass-through" },
      { name: "description", content: "Retro neon snake with walls and pass-through modes." },
      { property: "og:title", content: "Play Snake — Walls or Pass-through" },
      { property: "og:description", content: "Retro neon snake with walls and pass-through modes." },
    ],
  }),
  component: () => (
    <main className="px-4 py-10">
      <SnakeGame />
    </main>
  ),
});
