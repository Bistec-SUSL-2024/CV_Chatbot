import React, { useState } from "react";

const ChatPopup = ({ candidate, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [userMessage, setUserMessage] = useState("");

  const handleSend = () => {
    if (!userMessage.trim()) return;

    // Add user's message
    const newMessages = [...messages, { sender: "user", text: userMessage }];
    setMessages(newMessages);

    // Simulate a bot response
    setTimeout(() => {
      const botResponse = `Bot: Response to '${userMessage}'`;
      setMessages((prev) => [...prev, { sender: "bot", text: botResponse }]);
    }, 1000);

    setUserMessage("");
  };

  return (
    <div className="fixed top-0 left-0 w-full h-full flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white w-96 p-4 rounded-lg shadow-lg">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Chat with {candidate.title}</h2>
          <button
            className="text-red-500 font-bold text-lg"
            onClick={onClose}
          >
            ×
          </button>
        </div>
        <div className="h-64 overflow-y-auto border p-2 rounded">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`mb-2 p-2 rounded ${
                message.sender === "user"
                  ? "bg-blue-100 text-left"
                  : "bg-gray-200 text-right"
              }`}
            >
              {message.sender === "user" ? `You: ${message.text}` : message.text}
            </div>
          ))}
        </div>
        <div className="flex mt-4">
          <input
            type="text"
            value={userMessage}
            onChange={(e) => setUserMessage(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 border p-2 rounded-l-lg focus:outline-none"
          />
          <button
            onClick={handleSend}
            className="bg-blue-500 text-white px-4 py-2 rounded-r-lg hover:bg-blue-600"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPopup;
