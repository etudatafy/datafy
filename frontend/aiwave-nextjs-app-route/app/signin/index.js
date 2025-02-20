"use client";
import { useState } from "react";
import { loginUser } from "../api";
import Image from "next/image";
import Link from "next/link";

import logo from "../../public/images/logo/logo.png";
import google from "../../public/images/sign-up/google.png";
import facebook from "../../public/images/sign-up/facebook.png";

const SigninPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const data = await loginUser(email, password);
      localStorage.setItem("token", data.token); // Token'ı sakla
      alert("Giriş başarılı!");
      window.location.href = "/home"; // Kullanıcıyı yönlendir
    } catch (err) {
      setError(err.response?.data?.message || "Giriş yapılamadı.");
    }
  };

  return (
    <>
      <main className="page-wrapper">
        <div className="signup-area">
          <div className="wrapper">
            <div className="row">
              <div className="col-lg-6 bg-color-blackest left-wrapper">
                <div className="sign-up-box">
                  <div className="signup-box-top">
                    <Image
                      src={logo}
                      width={193}
                      height={50}
                      alt="sign-up logo"
                    />
                  </div>
                  <div className="signup-box-bottom">
                    <div className="signup-box-content">
                      <form onSubmit={handleLogin}>
                        <div className="input-section mail-section">
                          <input
                            type="email"
                            placeholder="Enter email address"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                          />
                        </div>
                        <div className="input-section password-section">
                          <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                          />
                        </div>
                        {error && <p className="error-message">{error}</p>}
                        <button type="submit" className="btn-default">
                          Sign In
                        </button>
                      </form>
                    </div>
                  </div>
                </div>
              </div>
              <div className="col-lg-6 right-wrapper">
                <div className="client-feedback-area">
                  <p>AI destekli eğitim sistemimize hoş geldiniz!</p>
                </div>
              </div>
            </div>
          </div>
          <Link className="close-button" href="/">
            <i className="fa-sharp fa-regular fa-x"></i>
          </Link>
        </div>
      </main>
    </>
  );
};

export default SigninPage;
