import React, { useState } from 'react';
import { CandidateList } from './Components/CandidatesList';
import { ChatWindow } from './Components/ChatWindow';
import { Modal } from './Components/Modal';
import { Message, Candidate } from './types';

const App: React.FC = () => {
  const [jobDescription, setJobDescription] = useState('');
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [showChat, setShowChat] = useState(false);
  const [currentCandidate, setCurrentCandidate] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);

  const handleSubmitDescription = () => {
    // Simulated results
    setCandidates([
      { id: 1, title: "Candidate 1" },
      { id: 2, title: "Candidate 2" },
      { id: 3, title: "Candidate 3" },
      { id: 4, title: "Candidate 4" },
      { id: 5, title: "Candidate 5" },
    ]);
  };

  const handleClear = () => {
    setJobDescription('');
    setCandidates([]);
    setShowChat(false);
    setCurrentCandidate('');
    setMessages([]);
  };

  const handleShowCV = (id: number) => {
    // Placeholder for CV display functionality
    console.log(`Showing CV for candidate ${id}`);
  };

  const handleAskMore = (id: number) => {
    setShowChat(true);
    setCurrentCandidate(`Candidate ${id}`);
  };

  const handleSendMessage = (text: string) => {
    setMessages([
      ...messages,
      { text, isUser: true },
      { text: `Response for '${text}' regarding ${currentCandidate} (Placeholder)`, isUser: false },
    ]);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">CV Analysis Chatbot - Phase_02</h1>
        
        <div className="bg-gray-800 p-1 rounded-t-lg">
          <h6 className="text-white text-sm px-3">Input the job description:</h6>
        </div>
        <textarea
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          placeholder="Enter job description here..."
          className="w-full p-4 border border-gray-300 rounded-b-lg mb-4 h-32"
        />

        <div className="grid grid-cols-2 gap-4 mb-6">
          <button
            onClick={handleClear}
            className="bg-gray-500 hover:bg-gray-600 text-white py-2 rounded"
          >
            Clear description
          </button>
          <button
            onClick={handleSubmitDescription}
            className="bg-blue-500 hover:bg-blue-600 text-white py-2 rounded"
          >
            Submit description
          </button>
        </div>

        {candidates.length > 0 && (
          <CandidateList
            candidates={candidates}
            onShowCV={handleShowCV}
            onAskMore={handleAskMore}
          />
        )}

        <Modal isOpen={showChat} onClose={() => setShowChat(false)}>
          <ChatWindow
            currentCandidate={currentCandidate}
            messages={messages}
            onSendMessage={handleSendMessage}
            onClearChat={() => setMessages([])}
          />
        </Modal>
      </div>
    </div>
  );
};

export default App;