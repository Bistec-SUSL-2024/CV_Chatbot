import React from "react";

const CandidateDetails = ({ candidate, onClose }) => {
  return (
    <div className="fixed top-0 left-0 w-full h-full bg-black bg-opacity-50 z-50 flex justify-center items-center">
      <div className="bg-white p-4 rounded-lg shadow-lg">
        <h2 className="text-xl font-bold">{candidate.title}</h2>
        <p>Experience: 5 years (Placeholder)</p>
        <p>Skills: JavaScript, React, TailwindCSS</p>
        <button
          className="bg-red-500 text-white px-4 py-2 rounded mt-4"
          onClick={onClose}
        >
          Close
        </button>
      </div>
    </div>
  );
};

export default CandidateDetails;
