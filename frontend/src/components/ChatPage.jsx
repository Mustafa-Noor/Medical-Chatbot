import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import "./ChatPage.css";

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [topic, setTopic] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const navigate = useNavigate();
  const chatEndRef = useRef(null); // ✅ Step 1: Create ref

  useEffect(() => {
    const storedTopic = localStorage.getItem("selected_topic");
    setTopic(storedTopic || "");
  }, []);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        if (topic) {
          const res = await API.get(`/chat/sessions?topic=${encodeURIComponent(topic)}`);
          setSessions(res.data);
        }
      } catch (err) {
        console.error("Error fetching sessions", err);
      }
    };
    fetchSessions();
  }, [topic]);

  const handleSessionClick = async (id) => {
    try {
      const res = await API.get(`/chat/messages?session_id=${id}`);
      const msgs = res.data.map((msg) => ({
        sender: msg.sender === "user" ? "user" : "bot",
        text: msg.message || msg.reply,
      }));
      setMessages(msgs);
      setSessionId(id);
    } catch (err) {
      console.error("Failed to load session messages", err);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await API.post("/chat/send-message", {
        session_id: sessionId,
        topic,
        message: input,
      });

      const newSessionId = response.data.session_id;
      if (!sessionId && newSessionId) {
        setSessionId(newSessionId);
        const updatedSessions = await API.get(`/chat/sessions?topic=${encodeURIComponent(topic)}`);
        setSessions(updatedSessions.data);
      }

      const botMessage = {
        sender: "bot",
        text: response.data.reply,
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

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom(); // ✅ Step 3: Scroll on new messages
  }, [messages]);

  return (
    <div className="chat-wrapper">
      <div className="sidebar">
        <h2>Chat Sessions</h2>
        <div className="session-list">
          {sessions.map((s) => (
            <button
              key={s.id}
              className={`session-btn ${s.id === sessionId ? "active" : ""}`}
              onClick={() => handleSessionClick(s.id)}
            >
              {s.title || `Session #${s.id}`}
            </button>
          ))}
        </div>
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </div>

      <div className="main-content">
        <div className="topic-bar-wrapper">
          <div className="topic-bar-inner">
            <button onClick={goBack} className="back-btn">← Back</button>
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
          <div ref={chatEndRef} /> {/* ✅ Step 4: Scroll anchor */}
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
