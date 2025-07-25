import React from "react";

const Sidebar = ({ sidebar }) => {
  return (
    <>
      <div className="inner">
        <div className="content-item-content">
          <div className="rbt-default-sidebar-wrapper">
            <nav className="mainmenu-nav">
              <ul className="dashboard-mainmenu rbt-default-sidebar-list">
                {sidebar &&
                  sidebar.map((data, index) => (
                    <li className="has-submenu" key={index}>
                      <a
                        className={`collapse-btn ${
                          data.isShow ? "" : "collapsed"
                        }`}
                        data-bs-toggle="collapse"
                        href={`#${data.id}`}
                        role="button"
                        aria-expanded={data.isShow}
                        aria-controls={data.id}
                      >
                        <span>Başlarken</span>
                      </a>
                      <div
                        className={`${data.isShow ? "show" : "collapse"}`}
                        id={data.id}
                      >
                        <ul className="submenu rbt-default-sidebar-list">
                          {data.list.map((item, i) => (
                            <li key={i}>
                              <a href={`#${item.id}`}>
                                <span>{item.text}</span>
                              </a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </li>
                  ))}
                <li>
                  <a href="/roadmap">
                    <span>Yol Haritası</span>
                  </a>
                </li>
                <li>
                  <a href="/utilize">
                    <span>Geliştirilmiş Özellikler</span>
                  </a>
                </li>
                <li>
                  <a href="/contact">
                    <span>Destek AL</span>
                  </a>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
