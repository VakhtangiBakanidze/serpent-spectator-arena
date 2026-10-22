import { act, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { AuthProvider, useAuth } from "@/lib/auth";
import { resetMockDb } from "@/lib/api";

function Probe() {
  const { user, logIn, logOut, signUp } = useAuth();
  return (
    <div>
      <span data-testid="u">{user?.username ?? "anon"}</span>
      <button onClick={() => logIn("demo@snake.dev", "demo123")}>in</button>
      <button onClick={() => signUp("bob", "bob@x.com", "secret1")}>up</button>
      <button onClick={() => logOut()}>out</button>
    </div>
  );
}

beforeEach(() => resetMockDb());

describe("AuthProvider", () => {
  it("logs in, shows username, logs out", async () => {
    render(<AuthProvider><Probe /></AuthProvider>);
    expect(screen.getByTestId("u")).toHaveTextContent("anon");
    await act(async () => { screen.getByText("in").click(); await new Promise((r) => setTimeout(r, 250)); });
    expect(screen.getByTestId("u")).toHaveTextContent("demo");
    await act(async () => { screen.getByText("out").click(); await new Promise((r) => setTimeout(r, 100)); });
    expect(screen.getByTestId("u")).toHaveTextContent("anon");
  });

  it("signs up and shows the new username", async () => {
    render(<AuthProvider><Probe /></AuthProvider>);
    await act(async () => { screen.getByText("up").click(); await new Promise((r) => setTimeout(r, 250)); });
    expect(screen.getByTestId("u")).toHaveTextContent("bob");
  });
});
