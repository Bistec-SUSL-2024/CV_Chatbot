import React, { useState, useRef, useEffect } from "react";
import { Picker } from "emoji-mart"; // Emoji Picker
import "emoji-mart/css/emoji-mart.css"; // Emoji Picker Styles
import axios from "axios";

const ChatPopup = ({ candidate, onClose }) => {
  const [messages, setMessages] = useState(
    JSON.parse(localStorage.getItem("chatMessages")) || []
  ); // Load saved messages
  const [userMessage, setUserMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
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

  const handleSend = async () => {
    if (!userMessage.trim()) return;

    const newMessages = [...messages, { sender: "user", text: userMessage }];
    setMessages(newMessages);
    setIsTyping(true);

    try {
      // Simulated API request to OpenAI (replace with your actual API logic)
      const response = await axios.post("https://api.openai.com/v1/completions", {
        prompt: userMessage,
        model: "text-davinci-003",
        max_tokens: 100,
      });
      const botResponse = response.data.choices[0].text.trim();

      setMessages((prev) => [...prev, { sender: "bot", text: botResponse }]);
    } catch (error) {
      console.error("Error fetching bot response:", error);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Oops! Something went wrong." },
      ]);
    } finally {
      setIsTyping(false);
    }

    setUserMessage("");
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setMessages([...messages, { sender: "user", text: `File uploaded: ${file.name}` }]);
    }
  };

  return (
    <div className="fixed top-0 left-0 w-full h-full flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white w-96 p-4 rounded-lg shadow-lg dark:bg-gray-800 dark:text-white">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">
            {candidate?.title ? `Chat with ${candidate.title}` : "Chat"}
          </h2>
          <button className="text-red-500 font-bold text-lg" onClick={onClose}>
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
          {isTyping && (
            <p className="text-gray-500 text-sm italic">Bot is typing...</p>
          )}
          <div ref={messagesEndRef} />
        </div>
        <div className="flex items-center mt-4">
          {showEmojiPicker && (
            <Picker
              onSelect={(emoji) => setUserMessage(userMessage + emoji.native)}
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
            className="flex-1 border p-2 focus:outline-none"
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
