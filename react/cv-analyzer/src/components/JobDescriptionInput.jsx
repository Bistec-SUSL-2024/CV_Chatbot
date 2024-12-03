import React, { useState } from "react";

const JobDescriptionInput = ({ setJobDescription, onSubmit }) => {
  const [description, setDescription] = useState("");

  return (
    <div className="p-4 bg-gray-800 rounded-lg text-white">
      <h4 className="text-lg mb-2">Input the Job Description</h4>
      <textarea
        className="w-full p-2 rounded bg-gray-700"
        placeholder="Enter job description here..."
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      ></textarea>
      <div className="flex justify-between mt-2">
        <button
          className="bg-red-500 px-4 py-2 rounded"
          onClick={() => setDescription("")}
        >
          Clear Description
        </button>
        <button
          className="bg-green-500 px-4 py-2 rounded"
          onClick={() => {
            setJobDescription(description);
            onSubmit();
          }}
        >
          Submit Description
        </button>
      </div>
    </div>
  );
};

export default JobDescriptionInput;
