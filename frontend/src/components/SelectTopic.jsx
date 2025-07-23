// src/components/SelectTopic.jsx

import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./SelectTopics.css"; // ✅ Import the styling

const SelectTopic = () => {
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get("http://localhost:8000/topics")
      .then((res) => {
        console.log("Fetched topics:", res.data);
        setTopics(res.data);
      })
      .catch((err) => {
        console.error("Failed to fetch topics:", err);
      });
  }, []);

  const handleSubmit = async () => {
    const userId = localStorage.getItem("user_id");
    console.log("Clicked Continue:", { userId, selectedTopic });

    if (!userId || !selectedTopic) {
      console.warn("Missing user_id or topic");
      return;
    }

    try {
      const response = await axios.post("http://localhost:8000/topics/user/topic", {
        user_id: userId,
        topic: selectedTopic,
      });

      console.log("✅ Topic saved successfully:", response.data);

      localStorage.setItem("selected_topic", selectedTopic);
      console.log("Navigating to /chat...");
      navigate("/chat");
    } catch (err) {
      console.error("❌ Error saving topic:", err);
    }
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
