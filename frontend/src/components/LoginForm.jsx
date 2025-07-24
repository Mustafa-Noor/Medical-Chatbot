import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import "./LoginRegister.css";

function LoginForm() {
  const [form, setForm] = useState({ username: "", password: "" });
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    console.log("Base URL:", import.meta.env.VITE_API_URL);

    try {
      // ✅ Send as JSON — no need for formData or headers
      const res = await API.post("/auth/login", {
        username: form.username,
        password: form.password,
      });

      // Save token and user_id
      localStorage.setItem("token", res.data.access_token);
      if (res.data.user_id) {
        localStorage.setItem("user_id", res.data.user_id);
      }

      navigate("/select-topic");
    } catch (err) {
      alert("Login failed. Please check your credentials.");
      console.error("Login error:", err.response?.data || err.message);
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
          Don't have an account? <a href="/register">Register here</a>
        </p>
        <p>
          <a href="/forgot-password">Forgot your password?</a>
        </p>
      </form>
    </div>
  );
}

export default LoginForm;
