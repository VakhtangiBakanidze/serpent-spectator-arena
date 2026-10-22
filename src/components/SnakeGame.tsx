import { useCallback, useEffect, useState } from "react";
import { Link } from "@tanstack/react-router";
import { Board } from "./Board";
import { changeDirection, createGame, KEY_TO_DIR, step, type Mode } from "@/lib/snake";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export function SnakeGame() {
  const { user } = useAuth();
  const [mode, setMode] = useState<Mode>("walls");
  const [state, setState] = useState(() => createGame("walls"));
  const [running, setRunning] = useState(false);
  const [saved, setSaved] = useState<string | null>(null);

  const restart = useCallback((m: Mode = mode) => {
    setState(createGame(m));
    setRunning(true);
    setSaved(null);
  }, [mode]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const dir = KEY_TO_DIR[e.key];
      if (dir) {
        e.preventDefault();
        setState((s) => changeDirection(s, dir));
      } else if (e.key === " ") {
        e.preventDefault();
        if (!state.alive) restart();
        else setRunning((r) => !r);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [state.alive, restart]);

  useEffect(() => {
    if (!running || !state.alive) return;
    const t = setInterval(() => setState((s) => step(s)), 120);
    return () => clearInterval(t);
  }, [running, state.alive]);

  useEffect(() => {
    if (!state.alive && state.score > 0 && user && saved === null) {
      setSaved("saving");
      api.submitScore(state.score, state.mode).then(() => setSaved("saved"));
    }
  }, [state.alive, state.score, state.mode, user, saved]);

  return (
    <div className="flex flex-col items-center gap-5">
      <div className="flex gap-2" role="group" aria-label="Game mode">
        {(["walls", "pass-through"] as Mode[]).map((m) => (
          <button
            key={m}
            aria-pressed={mode === m}
            className={mode === m ? "btn-primary" : "btn-ghost"}
            onClick={() => {
              setMode(m);
              setState(createGame(m));
              setRunning(false);
              setSaved(null);
            }}
          >
            {m === "walls" ? "Walls" : "Pass-through"}
          </button>
        ))}
      </div>
      <div className="flex items-center gap-6 font-display text-sm">
        <span>SCORE <span data-testid="score" className="text-primary">{state.score}</span></span>
        <span className="text-muted-foreground">{mode.toUpperCase()}</span>
      </div>
      <div className="relative">
        <Board state={state} />
        {(!running || !state.alive) && (
          <div className="overlay">
            {!state.alive ? (
              <>
                <p className="font-display text-2xl text-destructive glow">GAME OVER</p>
                <p className="text-sm">
                  {user
                    ? saved === "saved" ? "Score saved to leaderboard" : state.score > 0 ? "Saving…" : ""
                    : <><Link to="/login" className="underline">Log in</Link> to save scores</>}
                </p>
              </>
            ) : null}
            <button className="btn-primary" onClick={() => (state.alive && state.score === 0 && state.snake.length === 3 ? setRunning(true) : !state.alive ? restart() : setRunning(true))}>
              {!state.alive ? "Play again" : state.score === 0 ? "Start" : "Resume"}
            </button>
            <p className="text-xs text-muted-foreground">Arrows / WASD to move · Space to pause</p>
          </div>
        )}
      </div>
    </div>
  );
}
