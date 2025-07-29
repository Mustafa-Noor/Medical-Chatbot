import React, {
  useState,
  useRef,
  useImperativeHandle,
  forwardRef,
} from "react";
import { FaCheck, FaTimes } from "react-icons/fa";

const VoiceChatUI = forwardRef(({ onSendAudio }, ref) => {
  const [status, setStatus] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);


  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recordedAudioRef = useRef(null);

  const startRecording = async () => {
    try {
      setStatus("🎙️ Listening...");
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
      setStatus("Mic access failed.");
      setIsRecording(false);
    }
  };

  const sendAudio = async () => {
    if (!recordedAudioRef.current) return;
    setShowConfirm(false);
    setStatus("Sending...");
    setIsSpeaking(true);

    try {
      await onSendAudio(recordedAudioRef.current);
      setStatus("Sent to AI.");
    } catch (err) {
      console.error("Audio send failed:", err);
      setStatus("Failed to process.");
    } finally {
      setTimeout(() => {
        setIsSpeaking(false);
        setStatus("");
      }, 3000);
    }
  };

  const cancelAudio = () => {
    recordedAudioRef.current = null;
    setShowConfirm(false);
    setStatus("Cancelled.");
    setTimeout(() => setStatus(""), 2000);
  };

  // Let parent call startRecording()
  useImperativeHandle(ref, () => ({
    startRecording,
  }));

  return (
    <div className="voice-feedback inline-flex items-center gap-2 ml-3">
      {isRecording && (
        <div className="text-red-600 font-semibold animate-pulse">{status}</div>
      )}
      {showConfirm && (
        <div className="flex gap-2">
          <button
            className="bg-green-600 text-white p-3 rounded-full shadow hover:bg-green-700"
            onClick={sendAudio}
            disabled={isSpeaking}
          >
            <FaCheck />
          </button>
          <button
            className="bg-red-600 text-white p-3 rounded-full shadow hover:bg-red-700"
            onClick={cancelAudio}
            disabled={isSpeaking}
          >
            <FaTimes />
          </button>
        </div>
      )}
      {!isRecording && !showConfirm && status && (
        <p className="text-sm text-gray-500">{status}</p>
      )}
    </div>
  );
});

export default VoiceChatUI;
