import React, { useState } from "react";
import JobDescriptionInput from "./components/JobDescriptionInput";
import CandidatesList from "./components/CandidatesList";
import ChatPopup from "./components/ChatPopup";
import Header from "./components/Header";
import Footer from "./components/Footer";
import LoadingSpinner from "./components/LoadingSpinner";

const App = () => {
  const [jobDescription, setJobDescription] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [selectedCandidateId, setSelectedCandidateId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleJobSubmit = async (description) => {
    setJobDescription(description);
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:5000/submit-job-description", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_description: description }),
      });

      const data = await response.json();

      if (response.ok) {
        setCandidates(data.candidates);
      } else {
        console.error(data.error || "Failed to fetch candidates");
        alert("Error fetching candidates.");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Something went wrong while fetching candidates.");
    }

    setIsLoading(false);
  };

  const handleShowCV = async (candidate) => {
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:5000/show-cv", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cv_id: candidate.cv_id }),
      });

      const data = await response.json();

      if (response.ok) {
        alert(`CV Content: ${data.cv_text}`);
      } else {
        console.error(data.error || "Failed to fetch CV.");
      }
    } catch (error) {
      console.error("Error:", error);
    }

    setIsLoading(false);
  };

  return (
    <div className="App flex flex-col min-h-screen bg-lightBg dark:bg-darkBg text-lightText dark:text-darkText relative">
      {isLoading && (
        <LoadingSpinner
          size="h-20 w-20"
          primaryColor="border-blue-600"
          secondaryColor="border-purple-300"
        />
      )}

      <Header />

      <div className="content flex-1 p-4">
        <JobDescriptionInput onSubmit={handleJobSubmit} />

        {candidates.length > 0 && (
          <CandidatesList
            candidates={candidates}
            onShowCV={handleShowCV}
            onChat={(candidate) => setIsChatOpen(true)}
          />
        )}

        {isChatOpen && (
          <ChatPopup candidate={selectedCandidateId} onClose={() => setIsChatOpen(false)} />
        )}
      </div>

      <Footer />
    </div>
  );
};

export default App;
