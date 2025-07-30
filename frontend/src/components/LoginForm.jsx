import { useState } from "react";
import { useNavigate } from "react-router-dom"; // ✅ ADD THIS
import API from "../services/api";
import "./LoginRegister.css";

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
      alert("Login failed. Please check your credentials.");
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
