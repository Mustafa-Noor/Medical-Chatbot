import React, { useRef } from "react";
import API from "../services/api";

const VoiceChatComponent = ({ topic, setMessages }) => {
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const conversationLoopRef = useRef(false);

  const startVoiceConversation = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        audioChunksRef.current = [];

        const formData = new FormData();
        formData.append("audio", audioBlob, "voice_input.webm");
        formData.append("topic", topic);

        try {
          const response = await API.post("/voice-chat", formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });

          const { text, user_input, audio_path } = response.data;

          setMessages((prev) => [...prev, { sender: "user", text: user_input }]);
          setMessages((prev) => [...prev, { sender: "bot", text }]);

          const audio = new Audio(audio_path);
          audio.play();

          audio.onended = () => {
            if (conversationLoopRef.current) {
              setTimeout(() => mediaRecorderRef.current.start(), 500);
              setTimeout(() => mediaRecorderRef.current.stop(), 4000);
            }
          };
        } catch (err) {
          console.error("❌ Voice chat error:", err);
        }
      };

      conversationLoopRef.current = true;
      mediaRecorderRef.current.start();
      setTimeout(() => mediaRecorderRef.current.stop(), 4000);

    } catch (err) {
      console.error("❌ Microphone access error:", err);
    }
  };

  const stopVoiceConversation = () => {
    conversationLoopRef.current = false;
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      mediaRecorderRef.current.stop();
    }
  };

  return (
    <div className="flex gap-2 mt-4">
      <button onClick={startVoiceConversation} className="bg-green-600 text-white p-2 rounded-xl shadow">
        🎙️ Start Conversation
      </button>
      <button onClick={stopVoiceConversation} className="bg-red-600 text-white p-2 rounded-xl shadow">
        🛑 Stop
      </button>
    </div>
  );
};

export default VoiceChatComponent;
