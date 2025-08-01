// src/components/ChatSidebar.jsx
import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import API from "../services/api";
import "./ChatSidebar.css";

const ChatSidebar = ({ onSessionSelect, currentSessionId, onClose }) => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();



  const handleSessionClick = (session) => {
  navigate(`/chat?sessionId=${session.id}&topic=${encodeURIComponent(session.topic)}`);
};

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) {
        setError("Not authenticated");
        return;
      }

      const response = await API.get("/chat/sessions/all");
      setSessions(response.data);
      setError(null);
    } catch (err) {
      console.error("Failed to fetch sessions:", err);
      setError("Failed to load sessions");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return "Today";
    if (diffDays === 2) return "Yesterday";
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    return date.toLocaleDateString();
  };

  const truncate = (str, n = 30) => (str.length > n ? str.slice(0, n) + "..." : str);
  const getSessionPreview = (session) => {
    const title = truncate(session.title || "Untitled");
    return `${title}`;
    };

  if (loading) {
  return (
    <div className="chat-sidebar">
      <div className="sidebar-header">
        <h3>Chat History</h3>
        <button className="toggle-sidebar-btn" onClick={onClose}>
          ⨯
        </button>
      </div>
      <div className="loading-sessions">
        <div className="loading-spinner"></div>
        <p>Loading sessions...</p>
      </div>
    </div>
  );
}

  return (
    <div className="chat-sidebar">
      <div className="sidebar-header-top">
        <h3 className="sidebar-title">Chat History</h3>
        <button className="toggle-sidebar-btn" onClick={onClose}>⨯</button>
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={fetchSessions} className="retry-btn">
            Retry
          </button>
        </div>
      )}

      <div className="sessions-list">
        {sessions.length === 0 ? (
          <div className="no-sessions">
            <p>No chat sessions yet</p>
            <p className="no-sessions-subtitle">Start a new conversation!</p>
          </div>
        ) : (
          sessions.map((session) => (
  <div
    key={session.id}
    className={`session-item ${currentSessionId === session.id ? "active" : ""}`}
    onClick={() => handleSessionClick(session)}
  >
    <div className="session-content">
      <div className="session-topic font-semibold text-sm">
        {session.topic.replace(/_/g, " ")}
      </div>
      <div className="session-title text-xs text-gray-600">
        {getSessionPreview(session)}
      </div>
      <div className="session-date text-[10px] text-gray-400 mt-1">
        {formatDate(session.created_at)}
      </div>
    </div>
    <div className="session-indicator">
      {currentSessionId === session.id && (
        <div className="active-indicator"></div>
      )}
    </div>
  </div>
))
        )}
      </div>

      <div className="sidebar-footer">
        <button onClick={fetchSessions} className="refresh-btn">
          ↻ Refresh
        </button>
      </div>
    </div>
  );
};

export default ChatSidebar;