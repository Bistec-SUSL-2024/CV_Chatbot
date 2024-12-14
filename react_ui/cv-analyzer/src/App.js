import React, { useState } from "react";
import JobDescriptionInput from "./components/JobDescriptionInput";
import CandidatesList from "./components/CandidatesList";
import ChatSidebar from "./components/ChatSidebar";

const App = () => {
  const [jobDescription, setJobDescription] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [currentCandidate, setCurrentCandidate] = useState(null);
  const [messages, setMessages] = useState([]);

  const handleSubmitDescription = () => {
    setCandidates([
      { id: 1, title: "Candidate 1" },
      { id: 2, title: "Candidate 2" },
      { id: 3, title: "Candidate 3" },
    ]);
  };

  const handleSendMessage = (text) => {
    setMessages((prev) => [
      ...prev,
      { text, isUser: true },
      { text: Response for "${text}", isUser: false },
    ]);
  };

  return (
    <div className="flex h-screen">
      <div className="w-2/3 p-4 overflow-y-auto">
        <JobDescriptionInput
          setJobDescription={setJobDescription}
          onSubmit={handleSubmitDescription}
        />
        <CandidatesList
          candidates={candidates}
          onShowCV={(candidate) => alert(Showing CV for ${candidate.title})}
          onChat={(candidate) => setCurrentCandidate(candidate)}
        />
      </div>
      <div className="w-1/3 bg-gray-900 text-white">
        {currentCandidate && (
          <ChatSidebar
            currentCandidate={currentCandidate}
            messages={messages}
            onSendMessage={handleSendMessage}
          />
        )}
      </div>
    </div>
  );
};

export default App;
