import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import "./ChatPage.css";
import ReactMarkdown from "react-markdown";

const ChatPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [topic, setTopic] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const navigate = useNavigate();
  const chatBoxRef = useRef(null);

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
    setInput("");
    setIsLoading(true);

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

      setIsLoading(false); // 🟢 FIXED: move this before setting message

      const botMessage = {
        sender: "bot",
        text: response.data.reply,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setIsLoading(false); // Ensure it turns off on error too
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Sorry, something went wrong." },
      ]);
      console.error("Chat error:", err);
    }
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
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className={`chat-wrapper ${sidebarOpen ? "sidebar-open" : "sidebar-closed"}`}>
      {/* Floating ☰ toggle button (when sidebar is closed) */}
      {!sidebarOpen && (
        <button className="toggle-sidebar-btn-floating" onClick={toggleSidebar}>
          ☰
        </button>
      )}

      {/* Sidebar */}
      {sidebarOpen && (
        <div className="sidebar">
          <div className="sidebar-header">
            <div className="sidebar-header-top">
              <button onClick={goBack} className="back-btn">← Back</button>
              <button className="toggle-sidebar-btn" onClick={toggleSidebar}>⨯</button>
            </div>
            <h2>Chat Sessions</h2>
          </div>

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

          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      )}

      {/* Main Content */}
      <div className="main-content">
        {/* Topic Title Bar */}
        <div className="topic-bar-wrapper">
          <div className="topic-title">
            Topic: {topic.replace(/__/g, ": ").replace(/_/g, " ")}
          </div>
        </div>

        {/* Chat Area */}
        <div className="chat-box" ref={chatBoxRef}>
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-bubble ${msg.sender}`}>
              {msg.sender === "bot" ? (
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              ) : (
                msg.text
              )}
            </div>
          ))}

          {isLoading && (
            <div className="chat-bubble bot loading">
              Typing<span className="dot">.</span><span className="dot">.</span><span className="dot">.</span>
            </div>
          )}
        </div>

        {/* Input Bar */}
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
