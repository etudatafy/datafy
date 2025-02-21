"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/app/context/AuthContext"; // AuthContext'ten token al
import { useRouter } from "next/navigation";
import Context from "@/context/Context";

import HeaderTop from "@/components/Header/HeaderTop/HeaderTop";
import Header from "@/components/Header/Header";
import PopupMobileMenu from "@/components/Header/PopUpMobileMenu";
import Home from "@/components/Home/Home";
import Footer from "@/components/Footers/Footer";
import Copyright from "@/components/Footers/Copyright";

const HomePage = () => {
  const { token } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      // Token null ise localStorage kontrolü yapalım
      setTimeout(() => {
        if (!localStorage.getItem("authToken")) {
          router.push("/signin"); // Eğer token yoksa giriş sayfasına yönlendir
        }
      }, 500);
    } else {
      setLoading(false);
    }
  }, [token, router]);

  if (loading) return null; // Auth yüklenirken boş bir ekran göster

  return (
    <>
      <main className="page-wrapper">
        <Context>
          <Header
            headerTransparent="header-transparent"
            headerSticky="header-sticky"
            btnClass="rainbow-gradient-btn"
          />
          <PopupMobileMenu />

          <Home />
          <Footer />
          <Copyright />
        </Context>
      </main>
    </>
  );
};

export default HomePage;
