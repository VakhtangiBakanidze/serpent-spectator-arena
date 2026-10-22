/**
 * Single entry point for every backend call.
 *
 * In test environment (Vitest sets import.meta.env.MODE === "test") the
 * exported `api` resolves to the in-memory `mockApi` so existing tests keep
 * passing without any network access.  In all other environments `api`
 * resolves to `realApi` which talks to the FastAPI backend at
 * http://localhost:8000 using HTTP-only session cookies.
 */
import { createGame, type GameState, type Mode } from "./snake";

export type User = { username: string; email: string };
export type ScoreEntry = { username: string; score: number; mode: Mode; date: string };
export type LivePlayer = { id: string; username: string; mode: Mode; state: GameState };

// ---------------------------------------------------------------------------
// Mock (in-memory) implementation — kept intact so tests pass
// ---------------------------------------------------------------------------

type StoredUser = User & { password: string };

const delay = (ms = 150) => new Promise((r) => setTimeout(r, ms));

function seedScores(): ScoreEntry[] {
  return [
    { username: "neonviper", score: 420, mode: "walls", date: "2026-10-20" },
    { username: "pixelpython", score: 380, mode: "pass-through", date: "2026-10-19" },
    { username: "byte_boa", score: 310, mode: "walls", date: "2026-10-18" },
    { username: "loopcobra", score: 290, mode: "pass-through", date: "2026-10-21" },
    { username: "mamba8bit", score: 150, mode: "walls", date: "2026-10-17" },
  ];
}

let users: StoredUser[] = [];
let scores: ScoreEntry[] = [];
let currentUser: User | null = null;

export function resetMockDb() {
  users = [{ username: "demo", email: "demo@snake.dev", password: "demo123" }];
  scores = seedScores();
  currentUser = null;
}
resetMockDb();

const mockApi = {
  async signUp(username: string, email: string, password: string): Promise<User> {
    await delay();
    username = username.trim();
    email = email.trim().toLowerCase();
    if (username.length < 3) throw new Error("Username must be at least 3 characters");
    if (!/^\S+@\S+\.\S+$/.test(email)) throw new Error("Invalid email");
    if (password.length < 6) throw new Error("Password must be at least 6 characters");
    if (users.some((u) => u.username.toLowerCase() === username.toLowerCase()))
      throw new Error("Username already taken");
    if (users.some((u) => u.email === email)) throw new Error("Email already registered");
    users.push({ username, email, password });
    currentUser = { username, email };
    return currentUser;
  },

  async logIn(email: string, password: string): Promise<User> {
    await delay();
    const u = users.find((x) => x.email === email.trim().toLowerCase() && x.password === password);
    if (!u) throw new Error("Invalid email or password");
    currentUser = { username: u.username, email: u.email };
    return currentUser;
  },

  async logOut(): Promise<void> {
    await delay(50);
    currentUser = null;
  },

  async getCurrentUser(): Promise<User | null> {
    await delay(20);
    return currentUser;
  },

  async getLeaderboard(mode?: Mode): Promise<ScoreEntry[]> {
    await delay();
    return scores
      .filter((s) => !mode || s.mode === mode)
      .sort((a, b) => b.score - a.score)
      .slice(0, 10);
  },

  async submitScore(score: number, mode: Mode): Promise<ScoreEntry> {
    await delay();
    if (!currentUser) throw new Error("Must be logged in to submit a score");
    const entry = {
      username: currentUser.username,
      score,
      mode,
      date: new Date().toISOString().slice(0, 10),
    };
    scores.push(entry);
    return entry;
  },

  async getLivePlayers(): Promise<LivePlayer[]> {
    await delay();
    return [
      { id: "p1", username: "neonviper", mode: "walls" as Mode },
      { id: "p2", username: "pixelpython", mode: "pass-through" as Mode },
      { id: "p3", username: "loopcobra", mode: "pass-through" as Mode },
    ].map((p) => ({ ...p, state: createGame(p.mode) }));
  },
};

// ---------------------------------------------------------------------------
// Real HTTP implementation — talks to FastAPI at localhost:8000
// ---------------------------------------------------------------------------

const BASE = "http://localhost:8000";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...init.headers },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(body.message ?? res.statusText);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

const realApi = {
  async signUp(username: string, email: string, password: string): Promise<User> {
    return request("/auth/signup", { method: "POST", body: JSON.stringify({ username, email, password }) });
  },
  async logIn(email: string, password: string): Promise<User> {
    return request("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
  },
  async logOut(): Promise<void> {
    await request("/auth/logout", { method: "POST" });
  },
  async getCurrentUser(): Promise<User | null> {
    return request<User>("/auth/me").catch(() => null);
  },
  async getLeaderboard(mode?: Mode): Promise<ScoreEntry[]> {
    const qs = mode ? `?mode=${encodeURIComponent(mode)}` : "";
    return request(`/leaderboard${qs}`);
  },
  async submitScore(score: number, mode: Mode): Promise<ScoreEntry> {
    return request("/scores", { method: "POST", body: JSON.stringify({ score, mode }) });
  },
  async getLivePlayers(): Promise<LivePlayer[]> {
    return request("/live");
  },
};

// ---------------------------------------------------------------------------
// Export — use mock in Vitest, real otherwise
// ---------------------------------------------------------------------------

export { mockApi, realApi };
export const api = import.meta.env.MODE === "test" ? mockApi : realApi;
