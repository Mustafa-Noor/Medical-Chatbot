// import "./LoginRegister.css"; // reuse the login/register styling

// function PasswordResetSent() {
//   return (
//     <div className="auth-container">
//       <div className="auth-form">
//         <h2>Check your email 📬</h2>
//         <p>If the username exists, a password reset link has been sent.</p>
//         <a href="/login" style={{ display: "inline-block", marginTop: "1.5rem", color: "#0096a0", fontWeight: "bold" }}>
//           Back to Login
//         </a>
//       </div>
//     </div>
//   );
// }

// export default PasswordResetSent;


import "./LoginRegister.css"; // use same style

function PasswordResetSent() {
  return (
    <div className="auth-container">
      <div className="auth-form">
        <h2>Check your email 📬</h2>
        <p>If the username exists, a password reset link has been sent.</p>
        <a
          href="/login"
          style={{
            display: "inline-block",
            marginTop: "1.5rem",
            padding: "10px 20px",
            backgroundColor: "#0096a0",
            color: "#fff",
            borderRadius: "8px",
            textDecoration: "none",
            fontWeight: "600",
          }}
        >
          Back to Login
        </a>
      </div>
    </div>
  );
}

export default PasswordResetSent;
