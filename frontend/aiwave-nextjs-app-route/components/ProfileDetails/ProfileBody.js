"use client";

import React, { useState } from "react";

const ProfileBody = ({ user }) => {
  // Kullanıcı bilgilerini prop olarak al
  const [bio, setBio] = useState(
    user.bio || "Profil bilgilerinizi güncelleyin."
  );

  const handleChange = (event) => {
    setBio(event.target.value);
  };

  return (
    <>
      <div className="single-settings-box profile-details-box overflow-hidden">
        <div className="profile-details-tab">
          <div className="advance-tab-button mb--30">
            <ul
              className="nav nav-tabs tab-button-style-2 justify-content-start"
              id="settinsTab-4"
              role="tablist"
            >
              <li role="presentation">
                <a
                  href="#"
                  className="tab-button active"
                  id="profile-tab"
                  data-bs-toggle="tab"
                  data-bs-target="#profile"
                  role="tab"
                  aria-controls="profile"
                  aria-selected="true"
                >
                  <span className="title">Profile</span>
                </a>
              </li>
              <li role="presentation">
                <a
                  href="#"
                  className="tab-button"
                  id="password-tab"
                  data-bs-toggle="tab"
                  data-bs-target="#password"
                  role="tab"
                  aria-controls="password"
                  aria-selected="false"
                >
                  <span className="title">Password</span>
                </a>
              </li>
            </ul>
          </div>

          <div className="tab-content">
            <div
              className="tab-pane fade active show"
              id="profile"
              role="tabpanel"
              aria-labelledby="profile-tab"
            >
              <form className="rbt-profile-row rbt-default-form row row--15">
                <div className="col-lg-6 col-md-6 col-sm-6 col-12">
                  <div className="form-group">
                    <label htmlFor="firstname">First Name</label>
                    <input
                      id="firstname"
                      type="text"
                      value={user.username}
                      readOnly
                    />
                  </div>
                </div>
                <div className="col-lg-6 col-md-6 col-sm-6 col-12">
                  <div className="form-group">
                    <label htmlFor="email">Email</label>
                    <input id="email" type="text" value={user.email} readOnly />
                  </div>
                </div>
                <div className="col-12">
                  <div className="form-group">
                    <label htmlFor="bio">Bio</label>
                    <textarea
                      id="bio"
                      cols="20"
                      rows="5"
                      value={bio}
                      onChange={handleChange}
                    />
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ProfileBody;
