import { BrowserRouter, Routes, Route } from "react-router-dom";
import RegisterForm from "./components/RegisterForm";
import LoginForm from "./components/LoginForm";
import HomePage from "./components/HomePage";
import ResetPassword from "./components/ResetPassword";
import ForgotPasswordForm from "./components/ForgotPasswordForm";
import PasswordResetSent from "./components/PasswordResetSent";
import SelectTopic from "./components/SelectTopic"; // ✅ new
import ChatPage from "./components/ChatPage";       // ✅ new

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
        <Route path="/select-topic" element={<SelectTopic />} />      {/* ✅ new */}
        <Route path="/chat" element={<ChatPage />} />                 {/* ✅ new */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;
