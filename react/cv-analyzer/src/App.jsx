import React, { useState } from "react";
import JobDescriptionInput from "./components/JobDescriptionInput";
import CandidatesList from "./components/CandidatesList";
import Header from "./components/Header";
import ChatPopup from "./components/ChatPopup";

const App = () => {
  const [jobDescription, setJobDescription] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState(null); // Track the candidate for chat

  const handleSubmitDescription = () => {
    if (!jobDescription.trim()) {
      alert("Please enter a job description before submitting.");
      return;
    }

    setCandidates([
      { id: 1, title: "Candidate 1" },
      { id: 2, title: "Candidate 2" },
      { id: 3, title: "Candidate 3" },
      { id: 4, title: "Candidate 4" },
      { id: 5, title: "Candidate 5" },
    ]);

    setIsSubmitted(true);
  };

  const handleChat = (candidate) => {
    setSelectedCandidate(candidate);
  };

  const closeChat = () => {
    setSelectedCandidate(null);
  };

  return (
    <div className="flex flex-col h-screen">
      <Header />
      <main className="flex flex-1">
        <div className="w-full p-4">
          <JobDescriptionInput
            setJobDescription={setJobDescription}
            onSubmit={handleSubmitDescription}
          />

          {isSubmitted && candidates.length > 0 && (
            <CandidatesList
              candidates={candidates}
              onShowCV={(candidate) => alert(`Showing CV for ${candidate.title}`)}
              onChat={handleChat} // Trigger chat popup
            />
          )}
        </div>
      </main>

      {/* ChatPopup renders conditionally */}
      {selectedCandidate && (
        <ChatPopup candidate={selectedCandidate} onClose={closeChat} />
      )}
    </div>
  );
};

export default App;
