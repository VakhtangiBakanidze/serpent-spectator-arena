import { useEffect, useRef, useState } from "react";
import type { LivePlayer } from "./api";

function getWebSocketUrl(): string {
  if (import.meta.env.VITE_WS_URL) {
    return import.meta.env.VITE_WS_URL;
  }
  if (typeof window !== "undefined" && window.location.port !== "5173" && import.meta.env.MODE !== "test") {
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${proto}//${window.location.host}/ws/live`;
  }
  return "ws://localhost:8000/ws/live";
}

const WS_URL = getWebSocketUrl();

export function useWebSocketLivePlayers() {
  const [players, setPlayers] = useState<LivePlayer[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let destroyed = false;

    function connect() {
      if (destroyed) return;
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data);
          if (msg.type === "snapshot" || msg.type === "tick") {
            setPlayers(msg.players);
          } else if (msg.type === "player_joined") {
            setPlayers((ps) => [...ps.filter((p) => p.id !== msg.player.id), msg.player]);
          } else if (msg.type === "player_left") {
            setPlayers((ps) => ps.filter((p) => p.id !== msg.playerId));
          }
        } catch {
          // ignore malformed messages
        }
      };

      ws.onclose = () => {
        if (!destroyed) {
          reconnectTimer.current = setTimeout(connect, 2000);
        }
      };

      ws.onerror = () => ws.close();
    }

    connect();

    return () => {
      destroyed = true;
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, []);

  return players;
}
