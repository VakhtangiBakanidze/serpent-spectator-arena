import type { GameState } from "@/lib/snake";

export function Board({ state, size = 20 }: { state: GameState; size?: number }) {
  const cells = [];
  for (let y = 0; y < state.height; y++)
    for (let x = 0; x < state.width; x++) {
      const idx = state.snake.findIndex((p) => p.x === x && p.y === y);
      const food = state.food.x === x && state.food.y === y;
      cells.push(
        <div
          key={`${x}-${y}`}
          className={idx === 0 ? "cell-head" : idx > 0 ? "cell-snake" : food ? "cell-food" : ""}
        />,
      );
    }
  return (
    <div
      data-testid="board"
      className={`board ${state.mode === "walls" ? "board-walls" : "board-pass"}`}
      style={{
        gridTemplateColumns: `repeat(${state.width}, ${size}px)`,
        gridTemplateRows: `repeat(${state.height}, ${size}px)`,
      }}
    >
      {cells}
    </div>
  );
}
