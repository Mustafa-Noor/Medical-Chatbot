import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import "./ChatPage.css";
import ReactMarkdown from "react-markdown";
import VoiceChatUI from "../components/VoiceChatUI";
import { FaMicrophone, FaStop } from "react-icons/fa";

const ChatPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [topic, setTopic] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [voiceMode, setVoiceMode] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState("Tap to speak");
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

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

  const startVoiceRecording = async () => {
  try {
    setVoiceStatus("Listening...");
    setIsRecording(true);
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;
    audioChunksRef.current = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        audioChunksRef.current.push(e.data);
      }
    };

    mediaRecorder.onstop = async () => {
      setVoiceStatus("Sending to AI...");
      const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
      await handleVoiceResponse(audioBlob);
      setVoiceStatus("Listening done");
      setIsRecording(false);
    };

    mediaRecorder.start();
    setTimeout(() => {
      if (mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
      }
    }, 6000);
  } catch (err) {
    console.error("Voice recording failed:", err);
    setVoiceStatus("Mic error");
    setIsRecording(false);
  }
};

const stopVoiceRecording = () => {
  if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
    mediaRecorderRef.current.stop();
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

      const botMessage = { sender: "bot", text: response.data.reply };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Sorry, something went wrong." },
      ]);
      console.error("Chat error:", err);
    } finally {
      setIsLoading(false);
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
  const handleVoiceResponse = async (audioBlob) => {
  const formData = new FormData();
  formData.append("audio", audioBlob);
  formData.append("topic", topic);

  try {
    const res = await API.post("/voice/voice-chat", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    const data = res.data;

    // Decode base64 to audio blob
    const binary = atob(data.audio_base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    const audioBlob = new Blob([bytes], { type: "audio/wav" });
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);

    // Update chat UI
    setMessages((prev) => [
      ...prev,
      { sender: "user", text: data.user_input },
      { sender: "bot", text: data.text },
    ]);
    audio.onplay = () => setIsSpeaking(true);
    audio.onended = () => setIsSpeaking(false);
    audio.play();
  } catch (err) {
    console.error("Voice chat error:", err);
    setMessages((prev) => [
      ...prev,
      { sender: "bot", text: "Voice processing failed." },
    ]);
  }
};


//   const handleVoiceResponse = async (audioBlob) => {
//   const formData = new FormData();
//   formData.append("audio", audioBlob);
//   formData.append("topic", topic);

//   try {
//     const res = await API.post("/voice/voice-chat", formData, {
//       headers: { "Content-Type": "multipart/form-data" },
//     });

//     const audioBlob = await res.blob(); // receive streamed audio
//     const audioUrl = URL.createObjectURL(audioBlob);
//     const audio = new Audio(audioUrl);

//     // Extract headers
//     const chatbotText = res.headers.get("X-Text");
//     const userInput = res.headers.get("X-User-Input");

//     setMessages((prev) => [
//       ...prev,
//       { sender: "user", text: userInput },
//       { sender: "bot", text: chatbotText },
//     ]);
//     audio.play();
//   } catch (err) {
//     console.error("Voice chat error:", err);
//     setMessages((prev) => [
//       ...prev,
//       { sender: "bot", text: "Voice processing failed." },
//     ]);
//   }
// };


  return (
    <div className={`chat-wrapper ${sidebarOpen ? "sidebar-open" : "sidebar-closed"}`}>
      {!sidebarOpen && (
        <button className="toggle-sidebar-btn-floating" onClick={toggleSidebar}>
          ☰
        </button>
      )}

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

      <div className="main-content">
        <div className="topic-bar-wrapper">
          <div className="topic-title">
            Topic: {topic.replace(/__/g, ": ").replace(/_/g, " ")}
          </div>
        </div>

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

        <div className="chat-input-wrapper">
  <input
    type="text"
    className={`chat-input ${voiceMode ? "disabled" : ""}`}
    value={voiceMode ? "🎙️ " + voiceStatus : input}
    disabled={voiceMode}
    onChange={(e) => setInput(e.target.value)}
    onKeyDown={handleKeyPress}
    placeholder={voiceMode ? "Voice mode active..." : "Type your question..."}
  />

  {voiceMode ? (
    <>
      <button
        className="send-btn"
        onClick={() => {
          if (isRecording) {
            stopVoiceRecording(); // defined below
          } else {
            startVoiceRecording(); // defined below
          }
        }}
        disabled={isSpeaking}
      >
        {isRecording ? "Stop" : "Speak"}
      </button>
    </>
  ) : (
    <button className="send-btn" onClick={handleSend}>Send</button>
  )}

  <button
    className="voice-btn"
    onClick={() => setVoiceMode((prev) => !prev)}
  >
    {voiceMode ? "End Conversation" : "Start Conversation"}
  </button>
</div>
      </div>
    </div>
  );
};

export default ChatPage;
