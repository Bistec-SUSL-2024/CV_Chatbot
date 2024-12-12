import React, { useEffect, useState } from "react";
import { MdFileUpload } from "react-icons/md"; // Import the upload icon from react-icons

const JobDescriptionInput = ({
  onSubmit,
  setJobDescription,
  setCandidates,
  jobDescription,
  handleClearDescription,
}) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Check for dark mode on component mount and update state
  useEffect(() => {
    const isDark = document.documentElement.classList.contains("dark");
    setIsDarkMode(isDark);
  }, []);

  return (
    <div
      className={`job-description-container p-6 mb-8 rounded-lg shadow-lg max-w-4xl mx-auto ${
        isDarkMode ? "bg-gray-800 text-gray-200" : "bg-white text-gray-900"
      }`}
    >
      <div className="header mb-4 text-center">
        <h2
          className="text-2xl font-bold"
          style={{ fontFamily: "'Inter', sans-serif" }} // Apply Inter font here
        >
          Input the Job Description
        </h2>
      </div>

      <textarea
        value={jobDescription} // Make sure this textarea is controlled
        onChange={(e) => setJobDescription(e.target.value)} // Update jobDescription on change
        className={`w-full p-4 border-2 rounded-lg focus:outline-none focus:ring-2 ${
          isDarkMode
            ? "border-gray-600 bg-gray-700 text-gray-200 placeholder-gray-400 focus:ring-indigo-400"
            : "border-gray-400 bg-white text-gray-900 placeholder-gray-500 focus:ring-indigo-200"
        }`}
        rows="6"
        placeholder="Enter job description here..."
      />

      <div className="actions mt-4 flex justify-between items-center">
        {/* Upload Icon */}
        <div className="flex items-center">
          <label
            htmlFor="file-upload"
            className={`cursor-pointer flex items-center space-x-2 ${
              isDarkMode ? "text-gray-300 hover:text-indigo-400" : "text-gray-600 hover:text-blue-600"
            }`}
          >
            <MdFileUpload size={30} />
            <span>Upload File</span>
          </label>
          <input
            id="file-upload"
            type="file"
            accept=".txt"
            className="hidden"
            onChange={(event) => {
              const file = event.target.files[0];
              if (file) {
                const reader = new FileReader();
                reader.onload = (e) => setJobDescription(e.target.result);
                reader.readAsText(file);
              }
            }}
          />
        </div>

        <div className="flex space-x-4">
          <button
            onClick={handleClearDescription} // Clear both jobDescription and candidates
            className={`px-4 py-2 rounded-md font-medium focus:outline-none ${
              isDarkMode
                ? "bg-gray-600 text-gray-200 hover:bg-gray-500 hover:text-white"
                : "bg-gray-400 text-black hover:bg-gray-700 hover:text-white"
            }`}
          >
            Clear Description
          </button>

          <button
            onClick={() => onSubmit(jobDescription)} // Pass the job description to submit
            className={`px-4 py-2 rounded-md font-medium focus:outline-none ${
              isDarkMode
                ? "bg-blue-600 text-gray-200 hover:bg-blue-500 hover:text-white"
                : "bg-blue-400 text-black hover:bg-blue-800 hover:text-white"
            }`}
          >
            Submit Description
          </button>
        </div>
      </div>
    </div>
  );
};

export default JobDescriptionInput;
