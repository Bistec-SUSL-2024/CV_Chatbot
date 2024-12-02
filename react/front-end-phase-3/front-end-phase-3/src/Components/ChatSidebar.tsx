import React, { useState } from 'react';
import { ChatMessage } from './ChatMessage';
import { Message } from '../types';

interface ChatSidebarProps {
  currentCandidate: string;
  messages: Message[];
  onSendMessage: (message: string) => void;
  onClearChat: () => void;
}

export function ChatSidebar({ currentCandidate, messages, onSendMessage, onClearChat }: ChatSidebarProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSendMessage(input);
      setInput('');
    }
  };

  return (
    <div className="fixed right-0 top-0 h-screen w-80 bg-white shadow-lg p-4 overflow-y-auto">
      <div className="bg-gray-700 text-white p-3 rounded-lg mb-4">
        <h2 className="text-lg font-semibold">
          Ask more info about {currentCandidate}:
        </h2>
      </div>

      <div className="space-y-2 mb-4">
        {messages.map((msg, idx) => (
          <ChatMessage key={idx} text={msg.text} isUser={msg.isUser} />
        ))}
      </div>

      <form onSubmit={handleSubmit} className="space-y-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter your question..."
          className="w-full p-2 border rounded"
        />
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={onClearChat}
            className="bg-gray-500 hover:bg-gray-600 text-white p-2 rounded"
          >
            Clear Chat
          </button>
          <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded"
          >
            Ask
          </button>
        </div>
      </form>
    </div>
  );
}