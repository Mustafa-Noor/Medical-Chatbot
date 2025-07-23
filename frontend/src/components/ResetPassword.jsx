// src/pages/ResetPassword.jsx

import React, { useState } from "react";
import { useSearchParams } from "react-router-dom";
import axios from "axios";
import "./ResetPassword.css"; // custom CSS for this page

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleReset = async () => {
    if (password !== confirmPassword) {
      setMessage("Passwords do not match");
      return;
    }

    try {
      const response = await axios.post("http://localhost:8000/auth/reset-password", {
        token,
        new_password: password,
      });

      setMessage(response.data.message || "Password reset successfully.");
    } catch (error) {
      setMessage(error.response?.data?.detail || "Error resetting password");
    }
  };

  return (
    <div className="reset-container">
      <div className="reset-card">
        <h2>Reset Password</h2>
        <input
          type="password"
          placeholder="New password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Confirm password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />
        <button onClick={handleReset}>Reset Password</button>

        {message && (
          <p
            className={`reset-message ${message.toLowerCase().includes("success") ? "success" : "error"}`}
          >
            {message}
          </p>
        )}
      </div>
    </div>
  );
};

export default ResetPassword;
