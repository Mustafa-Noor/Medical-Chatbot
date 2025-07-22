// src/components/HomePage.jsx
import { Link } from "react-router-dom";
import "./HomePage.css";
import bgImage from "../assets/medical-bg.jpg";

function HomePage() {
  return (
    <div
      className="home-container"
      style={{
        backgroundImage: `url(${bgImage})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "'Segoe UI', sans-serif",
      }}
    >
      <div className="home-card">
        <h1>Welcome to <span>Medical-ChatBot</span></h1>
        <p>Your trusted AI companion for medical information.</p>
        <div className="home-buttons">
          <Link to="/login" className="home-btn">Login</Link>
          <Link to="/register" className="home-btn outline">Register</Link>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
