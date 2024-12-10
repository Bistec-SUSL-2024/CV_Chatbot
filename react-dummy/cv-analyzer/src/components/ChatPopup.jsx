import React, { useState, useRef, useEffect } from "react";
import Picker from "@emoji-mart/react"; // Emoji Picker
import data from "@emoji-mart/data"; // Emoji data
import { FaShareAlt } from "react-icons/fa";
import { MdOutlineContentCopy } from "react-icons/md";
import { BiDislike } from "react-icons/bi";
import { BiLike } from "react-icons/bi";
import { FaRegSmileWink } from "react-icons/fa";

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

  return (
    <div
      className={`fixed top-0 left-0 w-full h-full ${
        isMaximized
          ? "z-50"
          : "flex items-center justify-center bg-black bg-opacity-50 z-50"
      }`}
    >
      <div
        className={`${
          isMaximized
            ? "w-full h-full bg-gray-900 p-8 rounded-2xl shadow-2xl dark:bg-gray-50 dark:text-black"
            : "w-[700px] h-[700px] bg-gray-900 p-4 rounded-2xl shadow-2xl dark:bg-gray-50 dark:text-black"
        } relative flex flex-col`}
      >
        {/* Header Section */}
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">
            {candidate?.title ? `Chat about ${candidate.title}` : "Chat"}
          </h2>
          <div className="flex items-center">
            <button
              className="text-black p-2 text-2xl"
              onClick={() => setIsMinimized(!isMinimized)}
            >
              {isMinimized ? "-" : "-"} {/* Minimize/Restore icon */}
            </button>
            <button
              className="text-black p-2 text-xl"
              onClick={() => setIsMaximized(!isMaximized)}
            >
              {isMaximized ? "🗗" : "🗗"} {/* Maximize/Restore icon */}
            </button>
            <button
              className="text-black p-2 font-bold text-2xl"
              onClick={handleClose} // Use handleClose to clear chat and close the popup
            >
              ×
            </button>
          </div>
        </div>

        {/* Chat Content */}
        {!isMinimized && (
          <div className="flex-1 overflow-y-auto mb-20 p-2 border rounded">
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`mb-2 p-2 rounded ${
                    message.sender === "user"
                      ? "bg-purple-200 text-left text-black hover:text-white hover:bg-purple-500"
                      : "bg-gray-200 text-right text-black hover:text-white hover:bg-gray-500"
                  }`}
                >
                  <p>
                    {message.sender === "user" ? (
                      <>
                        <span className="font-bold">You: </span> {message.text}
                      </>
                    ) : (
                      <>
                        <span className="font-bold">Response: </span>{" "}
                        {message.text}
                      </>
                    )}
                  </p>
                  {/* Add options only for bot responses */}
                  {message.sender === "bot" && (
                    <div className="flex justify-end items-center space-x-2 mt-2">
                      <button
                        className="text-black hover:text-blue-600 focus:outline-none"
                        title="Like"
                      >
                        <BiLike />
                      </button>
                      <button
                        className="text-black hover:text-red-600 focus:outline-none"
                        title="Dislike"
                      >
                        <BiDislike />
                      </button>
                      <button
                        className="text-black hover:text-blue-600 focus:outline-none"
                        title="Copy"
                        onClick={() =>
                          navigator.clipboard.writeText(message.text)
                        }
                      >
                        <MdOutlineContentCopy />
                      </button>
                      <button
                        className="text-black hover:text-blue-600 focus:outline-none"
                        title="Share"
                        onClick={() =>
                          alert("Share functionality is not implemented yet!")
                        }
                      >
                        <FaShareAlt />
                      </button>
                    </div>
                  )}
                </div>
              ))}
              {isTyping && (
                <p className="text-black text-sm italic">Bot is typing...</p>
              )}
            </div>
            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Fixed Bottom Input Section */}
        <div
          className="absolute bottom-0 left-0 w-full p-4 bg-white dark:bg-gray-100 border-t rounded-xl"
          style={{ zIndex: 1 }}
        >
          <div className="flex items-center space-x-0">
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
              className="p-2 bg-gray-200 rounded-l-xl hover:bg-gray-600 hover:text-white"
            >
              <FaRegSmileWink size={50} />
            </button>
            <textarea
              value={userMessage}
              onChange={(e) => setUserMessage(e.target.value)}
              placeholder="Type a message..."
              className="flex-1 border p-2 focus:outline-none text-black bg-white dark:text-black dark:bg-gray-50 h-16 resize-none"
            />
            <button
              onClick={handleSend}
              className="bg-green-500 text-black px-6 py-5 rounded-r-xl hover:bg-green-800 hover:text-white"
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
