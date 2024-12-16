import React, { useState } from "react";

const ChatSidebar = ({ currentCandidate, messages, onSendMessage }) => {
  const [message, setMessage] = useState("");

  return (
    <div className="p-4 h-full">
      <h4 className="text-lg mb-4">
        Chat with {currentCandidate?.title || "Candidate"}
      </h4>
      <div className="flex flex-col space-y-2 mb-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`p-2 rounded ${
              msg.isUser ? "bg-blue-500 text-left" : "bg-purple-500 text-right"
            }`}
          >
            {msg.text}
          </div>
        ))}
      </div>
      <div className="flex space-x-2">
        <input
          className="flex-grow p-2 rounded bg-gray-700"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message"
        />
        <button
          className="bg-green-500 px-4 py-2 rounded"
          onClick={() => {
            onSendMessage(message);
            setMessage("");
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatSidebar;
