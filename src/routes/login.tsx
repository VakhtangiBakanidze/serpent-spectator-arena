import { createFileRoute } from "@tanstack/react-router";
import { AuthForm } from "@/components/AuthForm";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: "Log in — Snake" },
      { name: "description", content: "Log in to save your snake scores." },
      { property: "og:title", content: "Log in — Snake" },
      { property: "og:description", content: "Log in to save your snake scores." },
    ],
  }),
  component: () => <main className="px-4 py-16"><AuthForm kind="login" /></main>,
});
