import { useState } from "react";
import { BACKEND_URL } from "../config.js";

export default function Chat() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");

  const handleSend = async () => {
    if (!message) return;
    try {
      const res = await fetch(`${BACKEND_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat: message }),
      });
      const data = await res.json();
      setResponse(data.text);
    } catch (err) {
      console.error(err);
      setResponse("Error connecting to backend");
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">ChatBot</h2>
      <input
        className="border p-2 w-full mb-2"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your message..."
      />
      <button
        className="bg-blue-600 text-white px-4 py-2"
        onClick={handleSend}
      >
        Send
      </button>
      <div className="mt-4 p-2 border bg-gray-100">
        <strong>Response:</strong>
        <p>{response}</p>
      </div>
    </div>
  );
}
