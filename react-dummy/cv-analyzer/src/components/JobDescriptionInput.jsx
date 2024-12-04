// JobDescriptionInput.jsx

import React from "react";

const JobDescriptionInput = ({ onSubmit, setJobDescription, setCandidates, jobDescription, handleClearDescription }) => {
  return (
    <div className="job-description-container p-6 mb-8 bg-white rounded-lg shadow-lg max-w-3xl mx-auto">
      <div className="header mb-4 text-center">
        <h2 className="text-2xl font-bold text-indigo-600">Input the Job Description</h2>
      </div>

      <textarea
        value={jobDescription}  // Make sure this textarea is controlled
        onChange={(e) => setJobDescription(e.target.value)}  // Update jobDescription on change
        className="w-full p-4 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        rows="6"
        placeholder="Enter job description here..."
      />

      <div className="actions mt-4 flex justify-between">
        <button
          onClick={handleClearDescription}  // Clear both jobDescription and candidates
          className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 focus:outline-none"
        >
          Clear Description
        </button>

        <button
          onClick={() => onSubmit(jobDescription)}  // Pass the job description to submit
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none"
        >
          Submit Description
        </button>
      </div>
    </div>
  );
};

export default JobDescriptionInput;
