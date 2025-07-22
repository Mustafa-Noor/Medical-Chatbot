import { useState } from "react";
import API from "../services/api";
import { useNavigate } from "react-router-dom";
import "./LoginRegister.css"; // reuse styling

function ForgotPasswordForm() {
  const [username, setUsername] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await API.post("/auth/forgot-password", { username });
      navigate("/forgot-password/sent");
    } catch (err) {
      setError("User not found");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h2>Forgot Password</h2>
        <input
          type="text"
          placeholder="Enter your username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          disabled={loading}
        />
        {error && <p style={{ color: "red", fontSize: "14px" }}>{error}</p>}

        <button type="submit" disabled={loading}>
          {loading ? "Sending..." : "Send Reset Link"}
        </button>

        <p>
          <a href="/login">Back to Login</a>
        </p>
      </form>
    </div>
  );
}

export default ForgotPasswordForm;
