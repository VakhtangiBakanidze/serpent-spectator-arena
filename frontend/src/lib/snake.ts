export type Mode = "walls" | "pass-through";
export type Dir = "up" | "down" | "left" | "right";
export type Point = { x: number; y: number };
export type GameState = {
  width: number;
  height: number;
  snake: Point[]; // head first
  dir: Dir;
  pendingDir: Dir;
  food: Point;
  score: number;
  alive: boolean;
  mode: Mode;
};

export const DELTA: Record<Dir, Point> = {
  up: { x: 0, y: -1 },
  down: { x: 0, y: 1 },
  left: { x: -1, y: 0 },
  right: { x: 1, y: 0 },
};
const OPPOSITE: Record<Dir, Dir> = { up: "down", down: "up", left: "right", right: "left" };

export const samePoint = (a: Point, b: Point) => a.x === b.x && a.y === b.y;

export function randomFood(
  snake: Point[],
  width: number,
  height: number,
  rand: () => number = Math.random,
): Point {
  const free: Point[] = [];
  for (let y = 0; y < height; y++)
    for (let x = 0; x < width; x++)
      if (!snake.some((s) => s.x === x && s.y === y)) free.push({ x, y });
  if (free.length === 0) return { x: -1, y: -1 };
  return free[Math.floor(rand() * free.length)]!;
}

export function createGame(
  mode: Mode,
  width = 20,
  height = 20,
  rand: () => number = Math.random,
): GameState {
  const cx = Math.floor(width / 2);
  const cy = Math.floor(height / 2);
  const snake = [
    { x: cx, y: cy },
    { x: cx - 1, y: cy },
    { x: cx - 2, y: cy },
  ];
  return {
    width,
    height,
    snake,
    dir: "right",
    pendingDir: "right",
    food: randomFood(snake, width, height, rand),
    score: 0,
    alive: true,
    mode,
  };
}

/** Queue a direction change; reversing into yourself is ignored. */
export function changeDirection(state: GameState, dir: Dir): GameState {
  if (OPPOSITE[state.dir] === dir) return state;
  return { ...state, pendingDir: dir };
}

export function step(state: GameState, rand: () => number = Math.random): GameState {
  if (!state.alive) return state;
  const dir = state.pendingDir;
  const d = DELTA[dir];
  const head = state.snake[0]!;
  let next = { x: head.x + d.x, y: head.y + d.y };

  const outside = next.x < 0 || next.y < 0 || next.x >= state.width || next.y >= state.height;
  if (outside) {
    if (state.mode === "walls") return { ...state, dir, alive: false };
    next = {
      x: (next.x + state.width) % state.width,
      y: (next.y + state.height) % state.height,
    };
  }

  const eats = samePoint(next, state.food);
  // When not eating, the tail moves away, so it's safe to move into it.
  const body = eats ? state.snake : state.snake.slice(0, -1);
  if (body.some((p) => samePoint(p, next))) return { ...state, dir, alive: false };

  const snake = [next, ...body];
  return {
    ...state,
    dir,
    snake,
    food: eats ? randomFood(snake, state.width, state.height, rand) : state.food,
    score: eats ? state.score + 10 : state.score,
  };
}

/** Simple bot used to simulate other players: heads toward food, avoids death. */
export function botDirection(state: GameState): Dir {
  const head = state.snake[0]!;
  const dirs: Dir[] = ["up", "down", "left", "right"];
  const safe = dirs.filter((d) => {
    if (OPPOSITE[state.dir] === d) return false;
    const sim = step({ ...state, pendingDir: d }, () => 0);
    return sim.alive;
  });
  if (safe.length === 0) return state.dir;
  const dist = (d: Dir) => {
    let x = head.x + DELTA[d].x;
    let y = head.y + DELTA[d].y;
    if (state.mode === "pass-through") {
      x = (x + state.width) % state.width;
      y = (y + state.height) % state.height;
    }
    return Math.abs(x - state.food.x) + Math.abs(y - state.food.y);
  };
  return safe.sort((a, b) => dist(a) - dist(b))[0] ?? state.dir;
}

export const KEY_TO_DIR: Record<string, Dir> = {
  ArrowUp: "up",
  ArrowDown: "down",
  ArrowLeft: "left",
  ArrowRight: "right",
  w: "up",
  s: "down",
  a: "left",
  d: "right",
};
