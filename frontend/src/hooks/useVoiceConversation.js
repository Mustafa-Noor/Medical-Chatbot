import { useRef } from "react";
import API from "../services/api";

const useVoiceConversation = (topic, setMessages) => {
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const isLooping = useRef(false);

  const start = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (e) => audioChunksRef.current.push(e.data);

      recorder.onstop = async () => {
        const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        audioChunksRef.current = [];

        const formData = new FormData();
        formData.append("audio", blob, "voice_input.webm");
        formData.append("topic", topic);

        try {
          const res = await API.post("/voice-chat", formData, {
            headers: { "Content-Type": "multipart/form-data" },
          });

          const { text, user_input, audio_path } = res.data;

          setMessages((prev) => [...prev, { sender: "user", text: user_input }]);
          setMessages((prev) => [...prev, { sender: "bot", text }]);

          const audio = new Audio(audio_path);
          audio.play();
          audio.onended = () => {
            if (isLooping.current) {
              setTimeout(() => recorder.start(), 500);
              setTimeout(() => recorder.stop(), 4000);
            }
          };
        } catch (err) {
          console.error("Voice chat error", err);
        }
      };

      isLooping.current = true;
      recorder.start();
      setTimeout(() => recorder.stop(), 4000);
    } catch (err) {
      console.error("Mic access error:", err);
    }
  };

  const stop = () => {
    isLooping.current = false;
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
  };

  return { startVoiceConversation: start, stopVoiceConversation: stop };
};

export default useVoiceConversation;
