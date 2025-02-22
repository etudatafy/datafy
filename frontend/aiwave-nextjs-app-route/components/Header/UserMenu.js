"use client";

import Image from "next/image";
import Link from "next/link";
import { useAuth } from "@/app/context/AuthContext"; // Kullanıcı bilgilerini almak için
import defaultAvatar from "../../public/images/team/team-01sm.jpg";
import UserMenuItems from "./HeaderProps/UserMenuItem";

const UserMenu = () => {
  const { user, logout } = useAuth(); // Kullanıcı bilgilerini çek

  return (
    <>
      <div className="inner">
        <div className="rbt-admin-profile">
          <div className="admin-thumbnail">
            <Image
              src={user?.avatar || defaultAvatar} // Kullanıcının avatarı varsa göster, yoksa varsayılan avatar
              width={31}
              height={31}
              alt="User Image"
            />
          </div>
          <div className="admin-info">
            <span className="name">
              {user?.username || "Misafir Kullanıcı"}
            </span>
            <Link
              className="rbt-btn-link color-primary"
              href="/profile-details"
            >
              View Profile
            </Link>
          </div>
        </div>

        <UserMenuItems parentClass="user-list-wrapper user-nav" />

        <hr className="mt--10 mb--10" />

        <ul className="user-list-wrapper user-nav">
          <li>
            <Link href="/privacy-policy">
              <i className="fa-solid fa-comments-question"></i>
              <span>Help Center</span>
            </Link>
          </li>
          <li>
            <Link href="/profile-details">
              <i className="fa-sharp fa-solid fa-gears"></i>
              <span>Settings</span>
            </Link>
          </li>
        </ul>

        <hr className="mt--10 mb--10" />

        <ul className="user-list-wrapper">
          <li>
            <button onClick={logout} className="logout-button">
              <i className="fa-sharp fa-solid fa-right-to-bracket"></i>
              <span>Logout</span>
            </button>
          </li>
        </ul>
      </div>
    </>
  );
};

export default UserMenu;
