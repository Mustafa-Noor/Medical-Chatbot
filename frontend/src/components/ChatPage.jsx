import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import "./ChatPage.css";

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [topic, setTopic] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const storedTopic = localStorage.getItem("selected_topic");
    setTopic(storedTopic || "");
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await API.post("/chat/send-message", {
        session_id: sessionId, // Can be null on first send
        topic,
        message: input,
      });

      const newSessionId = response.data.session_id;
      if (!sessionId && newSessionId) {
        setSessionId(newSessionId); // Save session ID for future use
      }

      const botMessage = {
        sender: "bot",
        text: response.data.reply, // ✅ correct key based on backend
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Sorry, something went wrong." },
      ]);
      console.error("Chat error:", err);
    }

    setInput("");
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") handleSend();
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate("/login");
  };

  const goBack = () => {
    navigate("/select-topic");
  };

  return (
    <div className="chat-wrapper">
      <div className="sidebar">
        <h2>Chat History</h2>
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </div>

      <div className="main-content">
        <div className="topic-bar-wrapper">
          <div className="topic-bar-inner">
            <button onClick={goBack} className="back-btn">
              ← Back
            </button>
            <div className="topic-title">
              Topic: {topic.replace(/__/g, ": ").replace(/_/g, " ")}
            </div>
          </div>
        </div>

        <div className="chat-box">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`chat-bubble ${msg.sender === "user" ? "user" : "bot"}`}
            >
              {msg.text}
            </div>
          ))}
        </div>

        <div className="chat-input-wrapper">
          <input
            type="text"
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type your question..."
          />
          <button className="send-btn" onClick={handleSend}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
