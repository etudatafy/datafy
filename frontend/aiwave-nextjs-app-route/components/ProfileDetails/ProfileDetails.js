import React from "react";
import { useAuth } from "@/app/context/AuthContext"; // Kullanıcı bilgilerini çekmek için
import ProfileBody from "./ProfileBody";
import UserNav from "../Common/UserNav";

const ProfileDetails = () => {
  const { user } = useAuth(); // Kullanıcı bilgilerini AuthContext'ten al

  return (
    <>
      <div className="rbt-main-content mb--0">
        <div className="rbt-daynamic-page-content center-width">
          <div className="rbt-dashboard-content">
            <UserNav title="Profile Details" />

            <div className="content-page pb--50">
              <div className="chat-box-list">
                {user ? (
                  <ProfileBody user={user} />
                ) : (
                  <p>
                    User Bilgisi Bulunmamaktadır, Lütfen Tekrar Giriş Yapınız.
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ProfileDetails;
