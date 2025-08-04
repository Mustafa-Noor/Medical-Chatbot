import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import "./ChatPage.css";
import ReactMarkdown from "react-markdown";
import VoiceChatUI from "../components/VoiceChatUI";
import { FaMicrophone } from "react-icons/fa";
import { useLocation } from "react-router-dom";

const ChatPage = () => {
  const location = useLocation();
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [topic, setTopic] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [recordedAudio, setRecordedAudio] = useState(null);
  const [isVoiceProcessing, setIsVoiceProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [hasSentMessage, setHasSentMessage] = useState(false);

  const handleNewChat = () => {
  setMessages([]);
  setSessionId(null);
  setHasSentMessage(false); // also reset suggestions visibility if needed
};




  const navigate = useNavigate();
  const chatBoxRef = useRef(null);
  const voiceRef = useRef();
  

  useEffect(() => {
    const storedTopic = localStorage.getItem("selected_topic");
    setTopic(storedTopic || "");
  }, []);

  useEffect(() => {
  const fetchSuggestions = async () => {
    try {
      if (!sessionId && topic) {
        const res = await API.get(`/chat/suggestions?topic=${encodeURIComponent(topic)}`);
        setSuggestions(res.data); // response is: ["question1", "question2", "question3"]
      }
    } catch (err) {
      console.error("Failed to load suggestions", err);
    }
  };

  fetchSuggestions();
}, [sessionId, topic]);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const sessionIdFromUrl = params.get("sessionId");
    const topicFromUrl = params.get("topic");

    if (topicFromUrl) {
      setTopic(topicFromUrl);
      localStorage.setItem("selected_topic", topicFromUrl);
    }

    if (sessionIdFromUrl) {
      setSessionId(sessionIdFromUrl);
      handleSessionClick(sessionIdFromUrl); // Make sure handleSessionClick is defined
    }
  }, [location.search]);

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
  // ✅ If sending recorded voice
  if (recordedAudio) {
  const formData = new FormData();
  formData.append("audio", recordedAudio);

  setMessages((prev) => [...prev, { sender: "user", text: "🎙️ Sending your voice..." }]);
  setInput("");
  setRecordedAudio(null);
  setShowConfirm(false);
  setIsRecording(false);
  setIsVoiceProcessing(true);

  try {
    // Step 1️⃣: Transcribe voice
    const transcribeRes = await API.post("/voice/transcribe", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    const userInput = transcribeRes.data.user_input || "[Voice message]";

    // ⏱️ Replace placeholder with real transcription early
    setMessages((prev) => {
      const updated = [...prev];
      const lastIndex = updated.length - 1;
      if (updated[lastIndex].text === "🎙️ Sending your voice...") {
        updated[lastIndex] = { sender: "user", text: userInput };
      }
      return updated;
    });

    // Step 2️⃣: Get bot reply
    const replyRes = await API.post("/voice/reply", {
      user_input: userInput,
      topic,
      session_id: sessionId,
    });

    const botText = replyRes.data.text;
    const newSessionId = replyRes.data.session_id;

    if (newSessionId && newSessionId !== sessionId) {
      setSessionId(newSessionId);
      const updatedSessions = await API.get(`/chat/sessions?topic=${encodeURIComponent(topic)}`);
      setSessions(updatedSessions.data);
    }

    // Step 3️⃣: TTS
    const ttsRes = await API.post("/voice/tts", { text: botText }, { responseType: "arraybuffer" });

    const audioBlob = new Blob([ttsRes.data], { type: "audio/mpeg" });
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);

    setMessages((prev) => [...prev, { sender: "bot", text: botText }]);

    setIsSpeaking(true);
    audio.play();
    audio.onended = () => setIsSpeaking(false);
  } catch (err) {
    console.error("Voice chat error:", err);
    setMessages((prev) => [...prev, { sender: "bot", text: "Voice processing failed." }]);
  } finally {
    setIsVoiceProcessing(false);
  }

  return;
}

  // ✅ If sending normal text message
  if (!input.trim() || input === "🎙️ Recorded. Press Send") return;

  const userMessage = { sender: "user", text: input };
  setMessages((prev) => [...prev, userMessage]);
  setInput(""); // ✅ Clear right after sending
  setIsLoading(true);

    
  try {

    if (!hasSentMessage) setHasSentMessage(true);
    const response = await API.post("/chat/send-message", {
      session_id: sessionId,
      topic,
      message: input,
    });

    
    console.log("Response session_id:", response.data.session_id);

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

      const binary = atob(data.audio_base64);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
      }
      const audioBlob = new Blob([bytes], { type: "audio/wav" });
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);

      setMessages((prev) => [
        ...prev,
        { sender: "user", text: data.user_input },
        { sender: "bot", text: data.text },
      ]);
      
      setIsSpeaking(true); // 🔒 Lock input

      audio.play();

      audio.onended = () => {
        setIsSpeaking(false); // 🔓 Unlock input
      };

    } catch (err) {
      console.error("Voice chat error:", err);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Voice processing failed." },
      ]);
    }
  };

  const deleteSession = async (id) => {
  try {
    await API.delete(`/chat/session/${id}`);
    setSessions((prev) => prev.filter((s) => s.id !== id));
    if (id === sessionId) {
      setSessionId(null);
      setMessages([]);
    }
  } catch (err) {
    console.error("Failed to delete session:", err);
    alert("Failed to delete session.");
  }
};


return (
  <div className={`chat-wrapper ${sidebarOpen ? "sidebar-open" : "sidebar-closed"}`}>
    {!sidebarOpen && (
      <button className="toggle-sidebar-btn-floating" onClick={toggleSidebar}>
        ☰
      </button>
    )}

    {sidebarOpen && (
      <div className="sidebar">
        {/* SIDEBAR HEADER */}
        <div className="sidebar-top-row">
          <button onClick={goBack} className="back-btn">← Back</button>
          <button onClick={toggleSidebar} className="toggle-sidebar-btn">⨯</button>
        </div>

        {/* NEW CHAT */}
        <button className="sidebar-new-chat" onClick={handleNewChat}>
          ✏️ New Chat
        </button>

        <hr className="sidebar-divider" />

        {/* SESSION TITLE */}
        <h2 className="sidebar-title">Chat Sessions</h2>

        {/* SESSION LIST */}
        <div className="session-list">
          {sessions.map((s) => (
            <div key={s.id} className="session-row">
              <button
                className={`session-btn ${s.id === sessionId ? "active" : ""}`}
                onClick={() => handleSessionClick(s.id)}
              >
                {s.title || `Session #${s.id}`}
              </button>
              <button
                className="delete-btn"
                onClick={() => deleteSession(s.id)}
                title="Delete session"
              >
                🗑️
              </button>
            </div>
          ))}
        </div>

        {/* LOGOUT */}
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
          {isVoiceProcessing && (
            <div className="chat-bubble bot loading">
              Processing voice<span className="dot">.</span><span className="dot">.</span><span className="dot">.</span>
            </div>
          )}
        </div>

        {!sessionId && suggestions.length > 0 && !hasSentMessage && (
  <div className="suggestion-chips">
    {suggestions.map((q, idx) => (
      <button
        key={idx}
        className="suggestion-chip"
        onClick={() => {
          setInput(q);
          handleSend(q); // or just setInput(q) if you want to delay sending
        }}
      >
        {q}
      </button>
    ))}
  </div>
)}

        <div className="chat-input-wrapper">
          <input
            type="text"
            className="chat-input"
            value={
              isRecording
                ? "🎙️ Listening..."
                : recordedAudio
                ? "🎙️ Recorded. Press Send"
                : input
            }
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            disabled={isRecording || recordedAudio !== null || isSpeaking} 
            placeholder="Type your question..."    
          />

          {showConfirm && (
            <>
              <button
                className="confirm-btn success"
                onClick={() => {
                  setShowConfirm(false);
                  setIsRecording(false);
                  setInput("🎙️ Recorded. Press Send");
                }}
              >
                ✅
              </button>
              <button
                className="confirm-btn cancel"
                onClick={() => {
                  setShowConfirm(false);
                  setIsRecording(false);
                  setRecordedAudio(null);
                  setInput("");
                }}
              >
                ❌
              </button>
            </>
          )}


          <button className="send-btn" onClick={handleSend}>Send</button>
          {/* <button
            className="voice-btn"
            onClick={() => {
              setIsVoiceMode(true);
              voiceRef.current?.startRecording();
            }}
            title="Tap to speak"
          >
            <FaMicrophone />
          </button>
          <VoiceChatUI ref={voiceRef} onSendAudio={handleVoiceResponse} /> */}
          {!showConfirm && (
            <button
              className="voice-btn"
              onClick={() => {
                setIsRecording(true);
                setShowConfirm(true);
                voiceRef.current?.startRecording();
              }}
              title="Tap to speak"
              disabled={isSpeaking}
            >
              <FaMicrophone />
            </button>
          )}

          <VoiceChatUI
            ref={voiceRef}
            onSendAudio={(blob) => {
              setRecordedAudio(blob);
            }}
            onCancel={() => {
              setShowConfirm(false);
              setIsRecording(false);
              setRecordedAudio(null);
              setInput("");
            }}
          />

        </div>
      </div>

    </div>
  );
};

export default ChatPage;