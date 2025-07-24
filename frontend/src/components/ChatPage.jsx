import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./ChatPage.css";

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [topic, setTopic] = useState("");
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
      const user_id = localStorage.getItem("user_id");
      const response = await axios.post("http://localhost:8000/chat", {
        user_id,
        topic,
        query: input, // make sure this matches backend (`query`, not `question`)
      });

      const { answer, source } = response.data;

      const botMessage = {
        sender: "bot",
        text: answer,
        source: source || "unknown",
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Sorry, something went wrong.", source: "error" },
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
      {/* Sidebar */}
      <div className="sidebar">
        <h2>Chat History</h2>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Topic Bar */}
        <div className="topic-bar-wrapper">
          <div className="topic-bar-inner">
            <button onClick={goBack} className="back-btn">← Back</button>
            <div className="topic-title">
              Topic: {topic.replace(/__/g, ": ").replace(/_/g, " ")}
            </div>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="chat-box">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-bubble ${msg.sender}`}>
              <p>{msg.text}</p>
              {msg.sender === "bot" && msg.source && (
                <small className="source-tag">source: {msg.source}</small>
              )}
            </div>
          ))}
        </div>

        {/* Chat Input */}
        <div className="chat-input-wrapper">
          <input
            type="text"
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type your question..."
          />
          <button className="send-btn" onClick={handleSend}>Send</button>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
