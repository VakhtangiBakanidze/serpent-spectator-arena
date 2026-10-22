import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { realApi } from "@/lib/api";
import { useWebSocketLivePlayers } from "@/lib/websocket";

describe("realApi HTTP client", () => {
  const originalFetch = globalThis.fetch;

  afterEach(() => {
    globalThis.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  it("calls /auth/signup with credentials: include and JSON body", async () => {
    const mockUser = { username: "tester", email: "tester@snake.dev" };
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => mockUser,
    });

    const res = await realApi.signUp("tester", "tester@snake.dev", "password123");
    expect(res).toEqual(mockUser);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/auth/signup",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        body: JSON.stringify({ username: "tester", email: "tester@snake.dev", password: "password123" }),
      }),
    );
  });

  it("calls /auth/login with credentials: include", async () => {
    const mockUser = { username: "tester", email: "tester@snake.dev" };
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockUser,
    });

    const res = await realApi.logIn("tester@snake.dev", "password123");
    expect(res).toEqual(mockUser);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/auth/login",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        body: JSON.stringify({ email: "tester@snake.dev", password: "password123" }),
      }),
    );
  });

  it("handles logout returning 204", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 204,
    });

    await expect(realApi.logOut()).resolves.toBeUndefined();
    expect(globalThis.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/auth/logout",
      expect.objectContaining({ method: "POST", credentials: "include" }),
    );
  });

  it("getCurrentUser returns null when not authenticated (e.g. 401)", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ message: "Not authenticated" }),
    });

    const user = await realApi.getCurrentUser();
    expect(user).toBeNull();
  });

  it("getLeaderboard passes query params", async () => {
    const mockScores = [{ username: "bob", score: 100, mode: "walls", date: "2026-10-22" }];
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockScores,
    });

    const res = await realApi.getLeaderboard("walls");
    expect(res).toEqual(mockScores);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/leaderboard?mode=walls",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("submitScore sends score and mode", async () => {
    const scoreEntry = { username: "bob", score: 250, mode: "pass-through", date: "2026-10-22" };
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => scoreEntry,
    });

    const res = await realApi.submitScore(250, "pass-through");
    expect(res).toEqual(scoreEntry);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/scores",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        body: JSON.stringify({ score: 250, mode: "pass-through" }),
      }),
    );
  });
});

describe("useWebSocketLivePlayers hook", () => {
  let mockWsInstance: any;

  beforeEach(() => {
    class MockWebSocket {
      onmessage: ((ev: any) => void) | null = null;
      onclose: ((ev: any) => void) | null = null;
      onerror: ((ev: any) => void) | null = null;
      close = vi.fn();
      constructor(public url: string) {
        mockWsInstance = this;
      }
    }

    vi.stubGlobal("WebSocket", MockWebSocket);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("connects to ws://localhost:8000/ws/live and updates players on snapshot/tick", () => {
    const { result, unmount } = renderHook(() => useWebSocketLivePlayers());

    expect(result.current).toEqual([]);
    expect(mockWsInstance.url).toBe("ws://localhost:8000/ws/live");

    const fakePlayers = [
      {
        id: "p1",
        username: "neonviper",
        mode: "walls" as const,
        state: {
          width: 20,
          height: 20,
          snake: [{ x: 5, y: 5 }],
          dir: "right" as const,
          pendingDir: "right" as const,
          food: { x: 10, y: 10 },
          score: 100,
          alive: true,
          mode: "walls" as const,
        },
      },
    ];

    // Simulate server sending snapshot
    act(() => {
      mockWsInstance.onmessage?.({
        data: JSON.stringify({ type: "snapshot", players: fakePlayers }),
      });
    });

    expect(result.current).toEqual(fakePlayers);

    // Simulate player_joined
    const newPlayer = {
      id: "p2",
      username: "cobraclaw",
      mode: "pass-through" as const,
      state: {
        width: 20,
        height: 20,
        snake: [{ x: 8, y: 8 }],
        dir: "down" as const,
        pendingDir: "down" as const,
        food: { x: 3, y: 3 },
        score: 50,
        alive: true,
        mode: "pass-through" as const,
      },
    };

    act(() => {
      mockWsInstance.onmessage?.({
        data: JSON.stringify({ type: "player_joined", player: newPlayer }),
      });
    });

    expect(result.current.length).toBe(2);
    expect(result.current.find((p) => p.id === "p2")).toEqual(newPlayer);

    // Simulate player_left
    act(() => {
      mockWsInstance.onmessage?.({
        data: JSON.stringify({ type: "player_left", playerId: "p1" }),
      });
    });

    expect(result.current.length).toBe(1);
    expect(result.current[0].id).toBe("p2");

    unmount();
    expect(mockWsInstance.close).toHaveBeenCalled();
  });
});
