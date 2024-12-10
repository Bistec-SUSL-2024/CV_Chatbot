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

  const handleShowCV = (candidate) => {
    alert(`Displaying CV for ${candidate.title}`);
  };

  const handleShowChat = (candidate) => {
    setSelectedCandidate(candidate);
    setIsChatOpen(true);
  };

  const handleCloseChat = () => {
    setIsChatOpen(false);
    setSelectedCandidate(null);
  };

  const handleClearDescription = () => {
    setJobDescription("");
    setCandidates([]);
  };

  return (
    <div
      className="App flex flex-col min-h-screen"
      style={{ backgroundColor: "#F3FBFF" }}
    >
      <Header />

      <div className="content flex-1 p-4">
        <JobDescriptionInput
          onSubmit={handleJobSubmit}
          setJobDescription={setJobDescription}
          setCandidates={setCandidates}
          jobDescription={jobDescription}
          handleClearDescription={handleClearDescription}
        />

        {candidates.length > 0 && (
          <CandidatesList
            candidates={candidates}
            onShowCV={handleShowCV} // Pass handler for "Show CV"
            onChat={handleShowChat} // Pass handler for "Ask More Info"
          />
        )}

        {isChatOpen && (
          <ChatPopup candidate={selectedCandidate} onClose={handleCloseChat} />
        )}
      </div>

      <Footer />
    </div>
  );
};

export default App;
