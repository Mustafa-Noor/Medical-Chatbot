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

        // ✅ This sends the audio to ChatPage
        if (onSendAudio) {
          onSendAudio(recordedAudioRef.current);
        }
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

  return null;

});

export default VoiceChatUI;
