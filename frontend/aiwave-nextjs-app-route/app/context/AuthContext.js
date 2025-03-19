"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getAuthToken, setAuthToken, removeAuthToken } from "../utils/auth";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null); // Kullanıcı bilgilerini saklamak için
  const router = useRouter();

  useEffect(() => {
    const storedToken = getAuthToken();
    if (storedToken) {
      setToken(storedToken);
      fetchUserData(storedToken); // Kullanıcı bilgilerini çek
    }
  }, []);

  const fetchUserData = async (authToken) => {
    try {
      const response = await fetch("http://127.0.0.1:3000/api/auth/user", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authToken}`,
        },
      });

      if (!response.ok) throw new Error("Kullanıcı bilgileri alınamadı!");

      const userData = await response.json();
      setUser(userData); // Kullanıcı bilgilerini state'e kaydet
    } catch (error) {
      console.error("Kullanıcı bilgileri çekilirken hata oluştu:", error);
    }
  };

  const login = (newToken) => {
    setAuthToken(newToken);
    setToken(newToken);
    fetchUserData(newToken); // Login olunca kullanıcı bilgilerini al
    router.push("/");
  };

  const logout = () => {
    removeAuthToken();
    setToken(null);
    setUser(null); // Kullanıcı bilgisini sıfırla
    router.push("/signin");
  };

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
