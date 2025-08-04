import { useState } from "react";
import { useNavigate } from "react-router-dom"; // ✅ ADD THIS
import API from "../services/api";
import "./LoginRegister.css";
import { Link } from "react-router-dom";

function LoginForm() {
  const [form, setForm] = useState({ username: "", password: "" });
  const navigate = useNavigate(); // ✅ ADD THIS

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await API.post("/auth/login", new URLSearchParams(form));
      console.log(res)

      // ✅ Save token and user_id if available
      localStorage.setItem("token", res.data.access_token);
  
      if (res.data.user_id) {
        localStorage.setItem("user_id", res.data.user_id);
      }

      navigate("/select-topic"); // ✅ REDIRECT TO TOPIC SELECTION
    } catch (err) {
  if (err.response && err.response.data && err.response.data.detail) {
    alert(`Login failed: ${err.response.data.detail}`);
  } else {
    alert("Login failed. Please try again later.");
  }
}
  };

  return (
    <div className="auth-container">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h2>Login</h2>
        <input
          type="text"
          placeholder="Username"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          required
        />
        <button type="submit">Login</button>
        <p>
          Don't have an account? <Link to="/register">Register here</Link>
        </p>
        <p>
          <Link to="/forgot-password">Forgot your password?</Link>
        </p>
      </form>
    </div>
  );
}

export default LoginForm;
