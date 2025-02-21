"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getAuthToken, setAuthToken, removeAuthToken } from "../utils/auth";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);
  const router = useRouter();

  useEffect(() => {
    const storedToken = getAuthToken();
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  const login = (newToken) => {
    setAuthToken(newToken);
    setToken(newToken);
    router.push("/"); // Başarılı login sonrası anasayfaya yönlendir
  };

  const logout = () => {
    removeAuthToken();
    setToken(null);
    router.push("/signin"); // Çıkış yapınca login sayfasına yönlendir
  };

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
