import React from "react";

const Header = ({ title }) => {
  return (
    <header
      aria-label="Application Header"
      className="w-full py-4 shadow-md"
      style={{ backgroundColor: "#ebe9fe", fontFamily: "'Inter', sans-serif" }} // Apply Inter font
    >
      <h1 className="text-center text-3xl sm:text-2xl md:text-3xl font-bold tracking-normal">
        {title || "CV Analysis Chatbot Phase-3"}
      </h1>
    </header>
  );
};

export default Header;