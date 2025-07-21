// src/pages/ResetPassword.jsx

import React, { useState } from "react";
import { useSearchParams } from "react-router-dom";
import axios from "axios";

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

      setMessage(response.data.message);
    } catch (error) {
      setMessage(error.response?.data?.detail || "Error resetting password");
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Reset Password</h2>
      <input
        type="password"
        placeholder="New password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      /><br />
      <input
        type="password"
        placeholder="Confirm password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
      /><br />
      <button onClick={handleReset}>Reset Password</button>
      <p>{message}</p>
    </div>
  );
};

export default ResetPassword;


