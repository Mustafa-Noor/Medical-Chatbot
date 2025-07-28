import React, { useState } from "react";
import { FaMicrophone, FaStop } from "react-icons/fa";

const VoiceConversationButton = ({ onTranscribe }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [chunks, setChunks] = useState([]);

  const handleStartRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      setIsRecording(true);
      setMediaRecorder(recorder);
      setChunks([]);

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          setChunks((prev) => [...prev, e.data]);
        }
      };

      recorder.onstop = () => {
        const audioBlob = new Blob(chunks, { type: "audio/wav" });
        onTranscribe(audioBlob); // ⬅️ Send blob to parent
      };

      recorder.start();
    } catch (err) {
      console.error("Mic access denied or error:", err);
    }
  };

  const handleStopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };

  return (
    <button
      className="voice-btn"
      onClick={isRecording ? handleStopRecording : handleStartRecording}
      title={isRecording ? "Stop recording" : "Start voice input"}
    >
      {isRecording ? <FaStop /> : <FaMicrophone />}
    </button>
  );
};

export default VoiceConversationButton;
