import React, { useState } from "react";
import Header from "./components/Header";
import Footer from "./components/Footer";
import JobDescriptionInput from "./components/JobDescriptionInput";
import CandidatesList from "./components/CandidatesList";
import ChatPopup from "./components/ChatPopup";

const App = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [jobDescription, setJobDescription] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [isChatOpen, setIsChatOpen] = useState(false);

  const handleJobSubmit = (description) => {
    setIsLoading(true);
    setTimeout(() => {
      setCandidates([
        { id: 1, title: "Candidate 1" },
        { id: 2, title: "Candidate 2" },
        { id: 3, title: "Candidate 3" },
        { id: 4, title: "Candidate 4" },
        { id: 5, title: "Candidate 5" },
      ]);
      setJobDescription(description);
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="flex-1 p-4">
        {/* Job Description Input */}
        <JobDescriptionInput onSubmit={handleJobSubmit} />

        {/* Show Candidates List if available */}
        {!isLoading && candidates.length > 0 && (
          <CandidatesList
            candidates={candidates}
            onViewDetails={(candidate) => console.log(candidate)}
            onAskInfo={() => setIsChatOpen(true)}
          />
        )}

        {/* Chat Popup */}
        {isChatOpen && (
          <ChatPopup
            onClose={() => setIsChatOpen(false)}
            jobDescription={jobDescription}
          />
        )}
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default App;
