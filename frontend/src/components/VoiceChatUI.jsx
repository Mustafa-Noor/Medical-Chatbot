import React, { useState, useRef } from "react";

const VoiceChatUI = ({ onSendAudio }) => {
  const [voiceMode, setVoiceMode] = useState(false);
  const [status, setStatus] = useState("Tap to speak");
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const toggleVoiceMode = () => {
    setVoiceMode((prev) => !prev);
    setStatus("Tap to speak");
  };

  const startRecording = async () => {
    try {
      setStatus("🎙️ Now Listening...");
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
        setStatus("⏳ Sending to AI...");
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });

        try {
            await onSendAudio(audioBlob);  // 👈 Let parent handle audio playback
            setStatus("🔊 AI Speaking...");
            setIsSpeaking(true);
        } catch (err) {
            console.error("Voice processing failed:", err);
            setStatus("❌ Couldn't process voice.");
        } finally {
            // Reset after delay (optional)
            setTimeout(() => {
            setStatus("✅ Done. Tap to speak again.");
            setIsSpeaking(false);
            }, 5000); // give audio time to play before resetting
        }
        };

      mediaRecorder.start();
      setTimeout(() => {
        if (mediaRecorder.state !== "inactive") {
          mediaRecorder.stop();
        }
      }, 6000); // auto stop after 6s
    } catch (err) {
      console.error("Microphone error:", err);
      setStatus("❌ Mic error. Try again.");
      setIsRecording(false);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  };

  return (
    <div className="voice-chat-ui">
      <button
        className="toggle-voice-mode px-3 py-1 bg-blue-500 text-white rounded"
        onClick={toggleVoiceMode}
      >
        {voiceMode ? "Disable Voice Mode" : "Enable Voice Mode"}
      </button>

      {voiceMode && (
        <div className="voice-controls mt-4">
          <button
            className="record-button px-4 py-2 text-white rounded disabled:opacity-50 bg-green-600"
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isSpeaking}
          >
            {isRecording ? "🛑 Stop" : "🎤 Speak"}
          </button>

          <p className="status-text mt-2 text-sm text-gray-700">{status}</p>
        </div>
      )}
    </div>
  );
};

export default VoiceChatUI;
