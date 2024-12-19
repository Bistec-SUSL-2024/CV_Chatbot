import React from "react";

const JobDescriptionInput = ({
  onSubmit,
  setJobDescription,
  setCandidates,
  jobDescription,
  handleClearDescription,
}) => {
  return (
    <div className="job-description-container p-6 mb-8 bg-white rounded-lg shadow-lg max-w-4xl mx-auto">
      <div className="header mb-4 text-center">
        <h2
          className="text-2xl font-bold text-gray-900"
          style={{ fontFamily: "'Inter', sans-serif" }} // Apply Inter font here
        >
          Input the Job Description
        </h2>
      </div>

      <textarea
        value={jobDescription} // Make sure this textarea is controlled
        onChange={(e) => setJobDescription(e.target.value)} // Update jobDescription on change
        className="w-full p-4 border-2 border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-200"
        rows="6"
        placeholder="Enter job description here..."
      />

      <div className="actions mt-4 flex justify-end space-x-4"> {/* Align buttons to the right */}
        <button
          onClick={handleClearDescription} // Clear both jobDescription and candidates
          className="px-4 py-2 bg-gray-400 text-black rounded-md hover:bg-gray-700 hover:text-white focus:outline-black font-medium text-shadow-white"
        >
          Clear Description
        </button>

        <button
          onClick={() => onSubmit(jobDescription)} // Pass the job description to submit
          className="px-4 py-2 bg-blue-400 text-black rounded-md hover:bg-blue-800 hover:text-white focus:outline-black font-medium"
        >
          Submit Description
        </button>
      </div>
    </div>
  );
};

export default JobDescriptionInput;
