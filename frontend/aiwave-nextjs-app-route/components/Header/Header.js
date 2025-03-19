"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";

import { useAppContext } from "@/context/Context";

import logo from "../../public/images/logo/logo.png";
import Nav from "./Nav";

const Header = ({ headerTransparent, headerSticky, btnClass }) => {
  const router = useRouter();
  const pathname = usePathname();
  const { activeMobileMenu, setActiveMobileMenu } = useAppContext();
  const [isSticky, setIsSticky] = useState(false);

  useEffect(() => {
    if (pathname === "/") {
      router.push("/home");
    }

    const handleScroll = () => {
      const scrolled = window.scrollY;
      if (scrolled > 200) {
        setIsSticky(true);
      } else {
        setIsSticky(false);
      }
    };

    window.addEventListener("scroll", handleScroll);

    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, [router, pathname]);
  return (
    <>
      <header
        className={`rainbow-header header-default ${headerTransparent} ${headerSticky} ${
          isSticky ? "sticky" : ""
        }`}
      >
        <div className="container position-relative">
          <div className="row align-items-center row--0">
            <div className="col-lg-2 col-md-6 col-6">
            <div className="logo">
                <Link href="/home">
                  <Image
                    className="logo-light"
                    src={logo}
                    width={4000}
                    height={1600}
                    alt="Destek AL AI Logo"
                    quality={100}
                    style={{
                      objectFit: "contain",
                      width: "400px",  // Sabit genişlik
                      height: "auto",
                      backgroundColor: "transparent"
                    }}
                    priority
                  />
                </Link>
              </div>
            </div>

            <div className="col-lg-8 d-none d-lg-block">
              <nav className="mainmenu-nav d-none d-lg-flex justify-content-center">
                <Nav />
              </nav>
            </div>

            <div className="col-lg-2 col-md-6 col-6 position-static">
              <div className="header-right">
                <div className="header-btn">
                  <Link className={`${btnClass}`} href="/text-generator">
                    <span>Başla</span>
                  </Link>
                </div>

                <div className="mobile-menu-bar ml--5 d-flex justify-content-end d-lg-none">
                  <div className="hamberger">
                    <button
                      className="hamberger-button"
                      onClick={() => setActiveMobileMenu(!activeMobileMenu)}
                    >
                      <i className="fa-sharp fa-regular fa-bars"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>
    </>
  );
};

export default Header;
