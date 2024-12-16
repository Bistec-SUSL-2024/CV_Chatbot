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
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  const handleJobSubmit = (description) => {
    setJobDescription(description);
    setCandidates([
      { id: 1, title: "Candidate 1" },
      { id: 2, title: "Candidate 2" },
      { id: 3, title: "Candidate 3" },
      { id: 4, title: "Candidate 4" },
      { id: 5, title: "Candidate 5" },
    ]);
  };

  const handleShowChat = (candidate) => {
    setSelectedCandidate(candidate);
    setIsChatOpen(true);
  };

  const handleCloseChat = () => {
    setIsChatOpen(false);
    setSelectedCandidate(null);
  };

  return (
    <div className="App flex flex-col min-h-screen">
      <Header />
      
      <div className="content flex-1 p-4">
        <JobDescriptionInput onSubmit={handleJobSubmit} setJobDescription={setJobDescription} />
        
        {candidates.length > 0 && (
          <CandidatesList
            candidates={candidates}
            onShowChat={handleShowChat}
          />
        )}
        
        {isChatOpen && (
          <ChatPopup 
            candidate={selectedCandidate}
            onClose={handleCloseChat}
          />
        )}
      </div>

      {/* Footer stays at the bottom */}
      <Footer />
    </div>
  );
};

export default App;
