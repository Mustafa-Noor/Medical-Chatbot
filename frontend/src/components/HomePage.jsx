// src/components/HomePage.jsx
import { Link } from "react-router-dom";
import "./HomePage.css";

function HomePage() {
  return (
    <div className="home-container">
      <div className="home-card">
        <h1>Welcome to Medical-ChatBot</h1>
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
