import React, { useState, useRef, useEffect } from "react";
import Picker from "@emoji-mart/react"; // Emoji Picker
import data from "@emoji-mart/data"; // Emoji data

const ChatPopup = ({ candidate, onClose }) => {
  const [messages, setMessages] = useState(
    JSON.parse(localStorage.getItem("chatMessages")) || []
  ); // Load saved messages
  const [userMessage, setUserMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem("chatMessages", JSON.stringify(messages));
  }, [messages]);

  // Clear chat when popup closes
  const handleClose = () => {
    // Clear messages from state and localStorage
    setMessages([]);
    localStorage.removeItem("chatMessages");
    onClose(); // Call the parent onClose function to close the popup
  };

  const handleSend = () => {
    if (!userMessage.trim()) return;

    // Add user message
    const newMessages = [...messages, { sender: "user", text: userMessage }];
    setMessages(newMessages);

    // Simulate bot response by echoing the user's message
    setIsTyping(true);
    setTimeout(() => {
      setMessages((prev) => [...prev, { sender: "bot", text: userMessage }]);
      setIsTyping(false);
    }, 500); // Simulate a short delay for typing effect

    setUserMessage(""); // Clear input field
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setMessages([...messages, { sender: "user", text: `File uploaded: ${file.name}` }]);
    }
  };

  return (
    <div
      className={`fixed top-0 left-0 w-full h-full ${
        isMaximized ? "z-50" : "flex items-center justify-center bg-black bg-opacity-50 z-50"
      }`}
    >
      <div
        className={`${
          isMaximized
            ? "w-full h-full bg-white"
            : "w-[500px] h-[600px] bg-white p-4 rounded-lg shadow-lg dark:bg-gray-800 dark:text-white"
        } relative flex flex-col`}
      >
        {/* Header Section */}
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">
            {candidate?.title ? `Chat with ${candidate.title}` : "Chat"}
          </h2>
          <div className="flex items-center">
            <button
              className="text-gray-500 p-2"
              onClick={() => setIsMinimized(!isMinimized)}
            >
              {isMinimized ? "-" : "-"} {/* Minimize/Restore icon */}
            </button>
            <button
              className="text-gray-500 p-2"
              onClick={() => setIsMaximized(!isMaximized)}
            >
              {isMaximized ? "🗗" : "🗗"} {/* Maximize/Restore icon */}
            </button>
            <button
              className="text-red-500 font-bold text-lg"
              onClick={handleClose} // Use handleClose to clear chat and close the popup
            >
              ×
            </button>
          </div>
        </div>

        {/* Chat Content */}
        {!isMinimized && (
          <div className="flex-1 overflow-y-auto mb-16 p-2 border rounded">
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`mb-2 p-2 rounded ${
                    message.sender === "user"
                      ? "bg-blue-600 text-left"
                      : "bg-gray-700 text-right"
                  }`}
                >
                  {message.sender === "user" ? `You: ${message.text}` : message.text}
                </div>
              ))}
              {isTyping && (
                <p className="text-gray-500 text-sm italic">Bot is typing...</p>
              )}
            </div>
            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Fixed Bottom Input Section */}
        <div
          className="absolute bottom-0 left-0 w-full p-4 bg-white dark:bg-gray-800 border-t"
          style={{ zIndex: 1 }}
        >
          <div className="flex items-center">
            {showEmojiPicker && (
              <Picker
                data={data}
                onEmojiSelect={(emoji) =>
                  setUserMessage(userMessage + emoji.native)
                }
                style={{ position: "absolute", bottom: "60px", left: "20px" }}
              />
            )}
            <button
              onClick={() => setShowEmojiPicker(!showEmojiPicker)}
              className="p-2 bg-gray-300 rounded-l-lg"
            >
              😊
            </button>
            <input
              type="file"
              onChange={handleFileUpload}
              className="hidden"
              id="file-input"
            />
            <label
              htmlFor="file-input"
              className="cursor-pointer bg-gray-300 p-2"
            >
              📎
            </label>
            <input
              type="text"
              value={userMessage}
              onChange={(e) => setUserMessage(e.target.value)}
              placeholder="Type a message..."
              className="flex-1 border p-2 focus:outline-none text-black bg-white dark:text-white dark:bg-gray-700"
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
    </div>
  );
};

export default ChatPopup;
