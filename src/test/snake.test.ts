import { describe, expect, it } from "vitest";
import { botDirection, changeDirection, createGame, randomFood, step, type GameState } from "@/lib/snake";

const base = (over: Partial<GameState> = {}): GameState => ({
  ...createGame("walls", 10, 10, () => 0),
  food: { x: 0, y: 0 },
  ...over,
});

describe("snake engine", () => {
  it("starts with length 3 moving right", () => {
    const g = createGame("walls", 10, 10);
    expect(g.snake).toHaveLength(3);
    expect(g.dir).toBe("right");
    expect(g.alive).toBe(true);
  });

  it("moves one cell per step", () => {
    const g = step(base());
    expect(g.snake[0]).toEqual({ x: 6, y: 5 });
    expect(g.snake).toHaveLength(3);
  });

  it("ignores reversing direction", () => {
    expect(changeDirection(base(), "left").pendingDir).toBe("right");
    expect(changeDirection(base(), "up").pendingDir).toBe("up");
  });

  it("eats food: grows and scores 10", () => {
    const g = step(base({ food: { x: 6, y: 5 } }), () => 0);
    expect(g.snake).toHaveLength(4);
    expect(g.score).toBe(10);
    expect(g.food).not.toEqual({ x: 6, y: 5 });
  });

  it("walls mode: dies hitting the edge", () => {
    const g = step(base({ snake: [{ x: 9, y: 5 }, { x: 8, y: 5 }] }));
    expect(g.alive).toBe(false);
  });

  it("pass-through mode: wraps to the other side", () => {
    const g = step(base({ mode: "pass-through", snake: [{ x: 9, y: 5 }, { x: 8, y: 5 }] }));
    expect(g.alive).toBe(true);
    expect(g.snake[0]).toEqual({ x: 0, y: 5 });
    const up = step(base({ mode: "pass-through", dir: "up", pendingDir: "up", snake: [{ x: 3, y: 0 }, { x: 3, y: 1 }] }));
    expect(up.snake[0]).toEqual({ x: 3, y: 9 });
  });

  it("dies on self collision", () => {
    const snake = [{ x: 5, y: 5 }, { x: 5, y: 6 }, { x: 4, y: 6 }, { x: 4, y: 5 }, { x: 4, y: 4 }];
    const g = step(base({ snake, dir: "up", pendingDir: "left" }));
    expect(g.alive).toBe(false);
  });

  it("can move into the cell the tail is leaving", () => {
    const snake = [{ x: 5, y: 5 }, { x: 5, y: 6 }, { x: 4, y: 6 }, { x: 4, y: 5 }];
    const g = step(base({ snake, dir: "up", pendingDir: "left" }));
    expect(g.alive).toBe(true);
  });

  it("dead game does not advance", () => {
    const dead = base({ alive: false });
    expect(step(dead)).toBe(dead);
  });

  it("food never spawns on the snake", () => {
    const snake = [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 0, y: 1 }];
    for (let i = 0; i < 20; i++) {
      const f = randomFood(snake, 2, 2, Math.random);
      expect(f).toEqual({ x: 1, y: 1 });
    }
    expect(randomFood([{ x: 0, y: 0 }, { x: 1, y: 0 }], 2, 1)).toEqual({ x: -1, y: -1 });
  });

  it("bot heads toward food and avoids walls", () => {
    expect(botDirection(base({ food: { x: 5, y: 0 } }))).toBe("up");
    const atEdge = base({ snake: [{ x: 9, y: 5 }, { x: 8, y: 5 }], food: { x: 9, y: 9 } });
    expect(botDirection(atEdge)).toBe("down");
  });

  it("bot survives many steps", () => {
    let g = createGame("walls", 15, 15);
    for (let i = 0; i < 200 && g.alive; i++) g = step(changeDirection(g, botDirection(g)));
    expect(g.score).toBeGreaterThan(0);
  });
});
