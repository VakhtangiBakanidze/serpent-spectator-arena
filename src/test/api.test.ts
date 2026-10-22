import { beforeEach, describe, expect, it } from "vitest";
import { api, resetMockDb } from "@/lib/api";

beforeEach(() => resetMockDb());

describe("mock api", () => {
  it("signs up and becomes current user", async () => {
    const u = await api.signUp("alice", "Alice@x.com", "secret1");
    expect(u).toEqual({ username: "alice", email: "alice@x.com" });
    expect(await api.getCurrentUser()).toEqual(u);
  });

  it("validates signup", async () => {
    await expect(api.signUp("al", "a@x.com", "secret1")).rejects.toThrow(/3 characters/);
    await expect(api.signUp("alice", "bad", "secret1")).rejects.toThrow(/email/);
    await expect(api.signUp("alice", "a@x.com", "123")).rejects.toThrow(/6 characters/);
    await expect(api.signUp("Demo", "n@x.com", "secret1")).rejects.toThrow(/taken/);
    await expect(api.signUp("newbie", "demo@snake.dev", "secret1")).rejects.toThrow(/registered/);
  });

  it("logs in, rejects bad password, logs out", async () => {
    await expect(api.logIn("demo@snake.dev", "nope")).rejects.toThrow();
    const u = await api.logIn("demo@snake.dev", "demo123");
    expect(u.username).toBe("demo");
    await api.logOut();
    expect(await api.getCurrentUser()).toBeNull();
  });

  it("leaderboard sorted desc and filtered by mode", async () => {
    const all = await api.getLeaderboard();
    expect(all.map((s) => s.score)).toEqual([...all.map((s) => s.score)].sort((a, b) => b - a));
    const walls = await api.getLeaderboard("walls");
    expect(walls.every((s) => s.mode === "walls")).toBe(true);
  });

  it("submitScore requires login and appears on leaderboard", async () => {
    await expect(api.submitScore(999, "walls")).rejects.toThrow(/logged in/);
    await api.logIn("demo@snake.dev", "demo123");
    await api.submitScore(999, "walls");
    expect((await api.getLeaderboard())[0]).toMatchObject({ username: "demo", score: 999 });
  });

  it("returns live players with game states", async () => {
    const p = await api.getLivePlayers();
    expect(p.length).toBeGreaterThan(0);
    expect(p[0].state.alive).toBe(true);
  });
});
