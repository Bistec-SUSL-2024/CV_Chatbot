import React from "react";
import { FaFileUpload } from "react-icons/fa"; // Import the upload icon from react-icons

const JobDescriptionInput = ({
  onSubmit,
  setJobDescription,
  setCandidates,
  jobDescription,
  handleClearDescription,
}) => {
  const handleFileUpload = (e) => {
    const file = e.target.files[0]; // Get the selected file
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setJobDescription(event.target.result); // Set the content of the file as the job description
      };
      reader.readAsText(file); // Read the file as text
    }
  };

  return (
    <div className="job-description-container p-6 mb-8 bg-white rounded-lg shadow-lg max-w-4xl mx-auto relative">
      <div className="header mb-4 text-center">
        <h2
          className="text-2xl font-bold text-gray-900"
          style={{ fontFamily: "'Inter', sans-serif" }}
        >
          Input the Job Description
        </h2>
      </div>

      <div className="relative">
        <textarea
          value={jobDescription} // Make sure this textarea is controlled
          onChange={(e) => setJobDescription(e.target.value)} // Update jobDescription on change
          className="w-full p-4 border-2 border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-200"
          rows="6"
          placeholder="Enter job description here..."
        />
        {/* File upload icon */}
        <label
          htmlFor="file-upload"
          className="absolute bottom-3 right-3 bg-indigo-600 text-white p-2 rounded-full cursor-pointer hover:bg-indigo-800"
          title="Upload Job Description File"
        >
          <FaFileUpload size={20} />
        </label>
        <input
          id="file-upload"
          type="file"
          accept=".txt" // Accept text files
          onChange={handleFileUpload}
          className="hidden" // Hide the default input
        />
      </div>

      <div className="actions mt-4 flex justify-between">
        <button
          onClick={handleClearDescription} // Clear both jobDescription and candidates
          className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-700 focus:outline-none"
        >
          Clear Description
        </button>

        <button
          onClick={() => onSubmit(jobDescription)} // Pass the job description to submit
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-800 focus:outline-none"
        >
          Submit Description
        </button>
      </div>
    </div>
  );
};

export default JobDescriptionInput;
