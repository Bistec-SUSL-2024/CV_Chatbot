import React, { useState } from "react";
import JobDescriptionInput from "./components/JobDescriptionInput";
import CandidatesList from "./components/CandidatesList";
import ChatPopup from "./components/ChatPopup";
import Header from "./components/Header";
import Footer from "./components/Footer";

const App = () => {
  const [jobDescription, setJobDescription] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [selectedCandidateId, setSelectedCandidateId] = useState(null); // Track the selected candidate's ID
  const [isJobSubmitted, setIsJobSubmitted] = useState(false); // Track if a job description was submitted

  const handleJobSubmit = (description) => {
    setJobDescription(description);
    setCandidates([
      { id: 1, title: "Candidate 1" },
      { id: 2, title: "Candidate 2" },
      { id: 3, title: "Candidate 3" },
      { id: 4, title: "Candidate 4" },
      { id: 5, title: "Candidate 5" },
    ]);
    setIsJobSubmitted(true); // Mark job submission as true
  };

  const handleShowCV = (candidate) => {
    setSelectedCandidateId(candidate.id); // Highlight the candidate
    alert(`Displaying CV for ${candidate.title}`);
  };

  const handleShowChat = (candidate) => {
    setSelectedCandidateId(candidate.id); // Highlight the candidate
    setIsChatOpen(true);
  };

  const handleCloseChat = () => {
    setIsChatOpen(false);
    setSelectedCandidateId(null); // Reset the highlight when closing the chat
  };

  const handleClearDescription = () => {
    setJobDescription("");
    setCandidates([]);
    setSelectedCandidateId(null); // Clear the selected candidate
    setIsJobSubmitted(false); // Reset the job submission flag
  };

  return (
    <div className="App flex flex-col min-h-screen bg-lightBg dark:bg-darkBg text-lightText dark:text-darkText">
      <Header />

      <div className="content flex-1 p-4">
        <JobDescriptionInput
          onSubmit={handleJobSubmit}
          setJobDescription={setJobDescription}
          setCandidates={setCandidates}
          jobDescription={jobDescription}
          handleClearDescription={handleClearDescription}
        />

        {isJobSubmitted && candidates.length === 0 ? (
          <p className="text-center text-gray-500 dark:text-gray-300 mt-4">
            No candidates available.
          </p>
        ) : (
          candidates.length > 0 && (
            <CandidatesList
              candidates={candidates}
              selectedCandidateId={selectedCandidateId}
              onShowCV={handleShowCV}
              onChat={handleShowChat}
            />
          )
        )}

        {isChatOpen && (
          <ChatPopup
            candidate={candidates.find((c) => c.id === selectedCandidateId)}
            onClose={handleCloseChat}
          />
        )}
      </div>

      <Footer />
    </div>
  );
};

export default App;
