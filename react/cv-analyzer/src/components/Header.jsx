import React from "react";

const Header = ({ title }) => {
  return (
    <header
      aria-label="Application Header"
      className="w-full text-gray-800 py-4 shadow-md"
      style={{ backgroundColor: "#ECEBFB" }} // Use extracted color here
    >
      <h1 className="text-center text-3xl sm:text-2xl md:text-3xl font-bold uppercase tracking-wider">
        {title || "CV Analysis Chatbot Phase-3"}
      </h1>
      
    </header>
  );
};

export default Header;
