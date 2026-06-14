import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const location = useLocation();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };


  const navbarStyle = {
    backgroundColor: "#0f172a", 
    color: "#ffffff",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "0.75rem 1.5rem",
    boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
  };

  const linkStyle = (isActive: boolean) => ({
    textDecoration: "none",
    color: isActive ? "#93c5fd" : "#ffffff", 
    fontWeight: isActive ? "600" : "400",
    marginLeft: "1.25rem",
    transition: "color 0.2s ease"
  });

  const logoutBtnStyle = {
    backgroundColor: "#ffffff",
    color: "#0f172a",         
    border: "1px solid #cbd5e1",
    padding: "0.4rem 1rem",
    borderRadius: "6px",
    fontWeight: "500",
    cursor: "pointer",
    marginLeft: "1.25rem",
    transition: "background-color 0.2s ease"
  };

  return (
    <nav className="navbar" style={navbarStyle}>
      <div className="navbar-brand" style={{ fontWeight: "bold", fontSize: "1.2rem" }}>
        <Link to="/events" style={{ textDecoration: "none", color: "#ffffff" }}>
          PenguWave 🐧
        </Link>
      </div>
      <div className="navbar-links" style={{ display: "flex", alignItems: "center" }}>
        <Link
          to="/events"
          style={linkStyle(location.pathname.startsWith("/events"))}
          className={location.pathname.startsWith("/events") ? "active" : ""}
        >
          Events
        </Link>
        
        {user?.role === "admin" && (
          <Link
            to="/users"
            style={linkStyle(location.pathname === "/users")}
            className={location.pathname === "/users" ? "active" : ""}
          >
            Users
          </Link>
        )}
        
        <span className="navbar-user" style={{ marginLeft: "1.5rem", color: "#e2e8f0", fontSize: "0.9rem" }}>
          {user?.email}
        </span>
        
        <button 
          type="button" 
          onClick={handleLogout} 
          className="navbar-logout-btn"
          style={logoutBtnStyle}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#f1f5f9")}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#ffffff")}
        >
          Log Out
        </button>
      </div>
    </nav>
  );
}