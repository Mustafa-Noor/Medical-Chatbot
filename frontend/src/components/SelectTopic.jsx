// src/components/SelectTopic.jsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import ChatSidebar from "./ChatSidebar";
import "./SelectTopics.css";

const SelectTopic = () => {
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState("");
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      console.warn("No token found. Not fetching topics.");
      return;
    }
    
    API.get("/topics")
      .then((res) => {
        console.log("Fetched topics:", res.data);
        setTopics(res.data);
      })
      .catch((err) => {
        console.error("Failed to fetch topics:", err);
      });
  }, []);

  const handleSubmit = () => {
    if (!selectedTopic) {
      console.warn("No topic selected");
      return;
    }
    localStorage.setItem("selected_topic", selectedTopic);
    console.log("Topic saved to localStorage:", selectedTopic);
    navigate("/chat");
  };

  const handleSessionSelect = (sessionId, messages) => {
    setCurrentSessionId(sessionId);
    // You can handle the selected session here
    // For example, navigate to chat with the session loaded
    localStorage.setItem("current_session_id", sessionId);
    navigate("/chat", { state: { sessionId, messages } });
  };

  const toggleSidebar = () => {
    setShowSidebar(!showSidebar);
  };

  return (
    <div className="app-layout">
      {showSidebar && (
        <ChatSidebar 
          onSessionSelect={handleSessionSelect}
          currentSessionId={currentSessionId}
        />
      )}
      
      <div className={`main-content ${showSidebar ? 'with-sidebar' : 'full-width'}`}>
        <button 
          className="sidebar-toggle"
          onClick={toggleSidebar}
          aria-label="Toggle sidebar"
        >
          {showSidebar ? '◀' : '▶'}
        </button>

        <div className="select-topic-container">
          <div className="select-topic-box">
            <h2>Select a Medical Topic</h2>
            <select 
              onChange={(e) => setSelectedTopic(e.target.value)} 
              defaultValue=""
              className="topic-select"
            >
              <option value="" disabled>
                Select a topic
              </option>
              {topics.map((topic) => (
                <option key={topic.value} value={topic.value}>
                  {topic.label}
                </option>
              ))}
            </select>
            <button 
              onClick={handleSubmit} 
              disabled={!selectedTopic}
              className="continue-btn"
            >
              Continue to Chat
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SelectTopic;