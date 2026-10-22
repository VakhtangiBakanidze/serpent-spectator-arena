import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, type User } from "./api";

type AuthCtx = {
  user: User | null;
  logIn: (email: string, password: string) => Promise<void>;
  signUp: (username: string, email: string, password: string) => Promise<void>;
  logOut: () => Promise<void>;
};
const Ctx = createContext<AuthCtx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  useEffect(() => {
    api.getCurrentUser().then(setUser);
  }, []);
  return (
    <Ctx.Provider
      value={{
        user,
        logIn: async (e, p) => setUser(await api.logIn(e, p)),
        signUp: async (u, e, p) => setUser(await api.signUp(u, e, p)),
        logOut: async () => {
          await api.logOut();
          setUser(null);
        },
      }}
    >
      {children}
    </Ctx.Provider>
  );
}

export function useAuth() {
  const c = useContext(Ctx);
  if (!c) throw new Error("useAuth must be used inside AuthProvider");
  return c;
}
