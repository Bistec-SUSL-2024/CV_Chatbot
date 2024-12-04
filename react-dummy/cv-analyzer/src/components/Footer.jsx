import React from "react";

const Footer = () => {
  return (
    <footer
      className="#030712 py-4 text-center mt-4 "
      style={{ backgroundColor: "#ebe9fe" }} // Applied extracted color here
    >
      <p>&copy; 2024 CV Analysis Chatbot - Phase 3. All rights reserved.</p>
      <p>
        Created by <a href="#" className="underline text-blue-600">CIS-FOC</a>
      </p>
    </footer>
  );
};

export default Footer;
