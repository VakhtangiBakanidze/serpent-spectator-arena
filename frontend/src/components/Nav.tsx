import { Link } from "@tanstack/react-router";
import { useAuth } from "@/lib/auth";

export function Nav() {
  const { user, logOut } = useAuth();
  return (
    <header className="flex flex-wrap items-center justify-between gap-4 border-b border-border px-6 py-4">
      <Link to="/" className="font-display text-xl text-primary glow">
        SNAKE//
      </Link>
      <nav className="flex items-center gap-5 text-sm">
        <Link to="/" className="nav-link" activeProps={{ className: "nav-link-active" }}>
          Play
        </Link>
        <Link to="/leaderboard" className="nav-link" activeProps={{ className: "nav-link-active" }}>
          Leaderboard
        </Link>
        <Link to="/watch" className="nav-link" activeProps={{ className: "nav-link-active" }}>
          Watch
        </Link>
        {user ? (
          <>
            <span data-testid="username" className="text-accent">
              @{user.username}
            </span>
            <button className="btn-ghost" onClick={() => logOut()}>
              Log out
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="nav-link">
              Log in
            </Link>
            <Link to="/signup" className="btn-primary">
              Sign up
            </Link>
          </>
        )}
      </nav>
    </header>
  );
}
