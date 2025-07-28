import React, { useEffect, useRef, useState } from "react";
import { FaCheck, FaTimes } from "react-icons/fa";

const VoiceChatUI = ({ onSendAudio }) => {
  const [status, setStatus] = useState("🎙️ Listening...");
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recordedAudioRef = useRef(null);

  // Automatically start recording on mount
  useEffect(() => {
    startRecording();

    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
        mediaRecorderRef.current.stop();
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      setStatus("Now Listening...");
      setIsRecording(true);
      setShowConfirm(false);
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
        recordedAudioRef.current = new Blob(audioChunksRef.current, { type: "audio/wav" });
        setIsRecording(false);
        setShowConfirm(true);
        setStatus("✅ Ready to send or cancel");
      };

      mediaRecorder.start();

      // Auto stop after 6 seconds
      setTimeout(() => {
        if (mediaRecorder.state !== "inactive") {
          mediaRecorder.stop();
        }
      }, 6000);
    } catch (err) {
      console.error("Mic error:", err);
      setStatus(" Mic access failed");
      setIsRecording(false);
    }
  };

  const sendAudio = async () => {
    if (!recordedAudioRef.current) return;
    setShowConfirm(false);
    setStatus("Sending to AI...");
    setIsSpeaking(true);

    try {
      await onSendAudio(recordedAudioRef.current);
      setStatus("AI Speaking...");
    } catch (err) {
      console.error("Audio send failed:", err);
      setStatus("Failed to process.");
    } finally {
      setTimeout(() => {
        setIsSpeaking(false);
        setStatus("Done. Tap mic to speak again.");
      }, 5000);
    }
  };

  const cancelAudio = () => {
    recordedAudioRef.current = null;
    setShowConfirm(false);
    setStatus("Cancelled. Tap mic to speak again.");
  };

  return (
    <div className="flex flex-col items-center gap-2 mt-2">
      {isRecording && (
        <div className="text-red-600 font-medium animate-pulse">🎙️ Listening...</div>
      )}

      {showConfirm && (
        <div className="flex items-center gap-4">
          <button
            className="bg-green-600 text-white p-3 rounded-full shadow hover:bg-green-700"
            onClick={sendAudio}
            disabled={isSpeaking}
          >
            <FaCheck size={20} />
          </button>
          <button
            className="bg-red-600 text-white p-3 rounded-full shadow hover:bg-red-700"
            onClick={cancelAudio}
            disabled={isSpeaking}
          >
            <FaTimes size={20} />
          </button>
        </div>
      )}

      <p className="text-sm text-gray-600 mt-1">{status}</p>
    </div>
  );
};

export default VoiceChatUI;
