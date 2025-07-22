import { BrowserRouter, Routes, Route } from "react-router-dom";
import RegisterForm from "./components/RegisterForm";
import LoginForm from "./components/LoginForm";
import HomePage from "./components/HomePage"; // <-- import
import ResetPassword from "./pages/ResetPassword";
import ForgotPasswordForm from "./components/ForgotPasswordForm";
import PasswordResetSent from "./components/PasswordResetSent";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/register" element={<RegisterForm />} />
        <Route path="/login" element={<LoginForm />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/forgot-password" element={<ForgotPasswordForm />} />
        <Route path="/forgot-password/sent" element={<PasswordResetSent />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
