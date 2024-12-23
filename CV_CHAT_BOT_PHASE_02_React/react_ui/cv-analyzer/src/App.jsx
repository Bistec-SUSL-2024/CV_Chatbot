import React, { useState } from "react";
import JobDescriptionInput from "./components/JobDescriptionInput";
import CandidatesList from "./components/CandidatesList";
import ChatPopup from "./components/ChatPopup";
import Header from "./components/Header";
import Footer from "./components/Footer";
import LoadingSpinner from "./components/LoadingSpinner";
import axios from "axios";

const App = () => {
  const [jobDescription, setJobDescription] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [selectedCandidateId, setSelectedCandidateId] = useState(null);
  const [isJobSubmitted, setIsJobSubmitted] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  //---------------------------------Handle Cv Ranking Function-----------------------------------------

  const handleJobSubmit = async (description) => {
    setJobDescription(description);
    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8000/rank_cvs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ description }),
      });

      const data = await response.json();
      if (data.ranked_cvs) {
        setCandidates(data.ranked_cvs); // Update candidates with the backend response
        setIsJobSubmitted(true);
      } else {
        throw new Error("Failed to fetch ranked candidates.");
      }
    } catch (error) {
      console.error("Error fetching candidates:", error);
      alert("Something went wrong while fetching candidates.");
    }
    setIsLoading(false);
  };

  //----------------------------Handle Show CV Function---------------------------------

  const handleShowCV = async (candidate) => {
    setSelectedCandidateId(candidate.cv_id); // Highlight the candidate
    try {
      const response = await axios.post("http://localhost:8000/show_cv", {
        cv_id: candidate.cv_id,
      });

      // Backend opens the CV itself; no need to open another tab here
      if (response.data && response.data.message) {
        console.log("CV opened successfully on the backend.");
        alert(response.data.message); // Optionally display a message
      } else {
        alert("CV not available.");
      }
    } catch (error) {
      console.error("Error fetching CV:", error);
      alert("Failed to fetch CV");
    }
  };

  //-----------------------------------------Handle Query_CV Function-----------------------------------------------------

  const handleAskMoreInfo = async (candidate) => {
    try {
      // Trigger query_cv API to set context in the backend
      const response = await axios.post("http://localhost:8000/query_cv", {
        cv_id: candidate.cv_id,
      });

      console.log("Backend Response:", response.data);

      // Check if the response contains cv_id and cv_text
      if (response.data.cv_id && response.data.cv_text) {
        console.log("Candidate Details:", response.data.cv_text); // Log CV text for debugging

        // Store selected candidate details in the state
        setSelectedCandidate({
          ...candidate,
          cv_text: response.data.cv_text, // Store the cv_text along with candidate info
        });

        // Open the ChatPopup with the selected candidate
        setIsChatOpen(true);
      } else {
        alert("Failed to load candidate details.");
      }
    } catch (error) {
      console.error("Error selecting CV:", error);
      alert("An error occurred while fetching candidate details.");
    }
  };

  const handleCloseChat = () => {
    setIsChatOpen(false);
    setSelectedCandidate(null);
  };

  const handleClearDescription = () => {
    setJobDescription("");
    setCandidates([]);
    setSelectedCandidateId(null);
    setIsJobSubmitted(false);
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
      <div
        className={
          isLoading
            ? "pointer-events-none blur-md flex flex-col min-h-screen"
            : "flex flex-col min-h-screen"
        }
      >
        <Header />
        <div className="content flex-1 p-4">
          <JobDescriptionInput
            onSubmit={handleJobSubmit}
            setJobDescription={setJobDescription}
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
                onChat={handleAskMoreInfo} // Use the new function here
              />
            )
          )}
          {isChatOpen && selectedCandidate && (
            <ChatPopup
              candidate={selectedCandidate}
              onClose={() => setIsChatOpen(false)}
            />
          )}
        </div>
        <Footer />
      </div>
    </div>
  );
};

export default App;
