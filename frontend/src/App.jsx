// App.jsx

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ResetPassword from "./pages/ResetPassword";
// import other pages like Home, Login, etc.

function App() {
  return (
    <Router>
      <Routes>
        {/* Example route */}
        {/* <Route path="/" element={<Home />} /> */}
        <Route path="/reset-password" element={<ResetPassword />} />
      </Routes>
    </Router>
  );
}

export default App;
