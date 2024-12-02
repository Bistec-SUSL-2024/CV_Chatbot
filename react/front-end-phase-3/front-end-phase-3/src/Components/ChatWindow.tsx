import React, { useState } from 'react';
import { ChatMessage } from './ChatMessage';
import { Message } from '../types';

interface ChatWindowProps {
  currentCandidate: string;
  messages: Message[];
  onSendMessage: (message: string) => void;
  onClearChat: () => void;
}

export function ChatWindow({ currentCandidate, messages, onSendMessage, onClearChat }: ChatWindowProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSendMessage(input);
      setInput('');
    }
  };

  return (
    <div className="flex flex-col h-[600px]">
      <div className="bg-gray-700 text-white p-4 rounded-t-lg">
        <h2 className="text-lg font-semibold">
          Ask more info about {currentCandidate}
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.map((msg, idx) => (
          <ChatMessage key={idx} text={msg.text} isUser={msg.isUser} />
        ))}
      </div>

      <div className="border-t p-4">
        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter your question..."
            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={onClearChat}
              className="bg-gray-500 hover:bg-gray-600 text-white p-2 rounded transition-colors"
            >
              Clear Chat
            </button>
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded transition-colors"
            >
              Ask
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}