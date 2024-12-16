import React, { useState } from "react";

const JobDescriptionInput = ({ onSubmit, setJobDescription }) => {
  const [inputValue, setInputValue] = useState("");

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
    setJobDescription(e.target.value); // Update job description in App.jsx
  };

  const handleSubmit = () => {
    if (inputValue.trim() !== "") {
      onSubmit(inputValue);
    }
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Enter job description"
        value={inputValue}
        onChange={handleInputChange}
      />
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
};

export default JobDescriptionInput;
