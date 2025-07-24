// src/components/SelectTopic.jsx

import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import "./SelectTopics.css";


const SelectTopic = () => {
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
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

  return (
    <div className="select-topic-container">
      <div className="select-topic-box">
        <h2>Select a Medical Topic</h2>
        <select onChange={(e) => setSelectedTopic(e.target.value)} defaultValue="">
          <option value="" disabled>
            Select a topic
          </option>
          {topics.map((topic) => (
            <option key={topic.value} value={topic.value}>
              {topic.label}
            </option>
          ))}
        </select>
        <button onClick={handleSubmit} disabled={!selectedTopic}>
          Continue to Chat
        </button>
      </div>
    </div>
  );
};

export default SelectTopic;
