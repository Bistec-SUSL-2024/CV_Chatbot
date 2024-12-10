import React, { useState, useEffect } from "react";
import { FaSun, FaMoon } from "react-icons/fa"; // Icons for light and dark modes

const Header = ({ title }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Load theme from localStorage on component mount
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
      setIsDarkMode(true);
      document.documentElement.classList.add("dark");
    } else {
      setIsDarkMode(false);
      document.documentElement.classList.remove("dark");
    }
  }, []);

  // Toggle dark mode
  const toggleDarkMode = () => {
    const newTheme = !isDarkMode ? "dark" : "light";
    setIsDarkMode(!isDarkMode);
    localStorage.setItem("theme", newTheme);
    if (newTheme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  return (
    <header
      aria-label="Application Header"
      className="relative w-full py-4 shadow-md flex items-center justify-center"
      style={{
        backgroundColor: isDarkMode ? "#1e293b" : "#ebe9fe",
        color: isDarkMode ? "#f1f5f9" : "#000",
        fontFamily: "'Inter', sans-serif",
      }}
    >
      <h1 className="text-3xl sm:text-2xl md:text-3xl font-bold tracking-normal">
        {title || "CV Analysis Chatbot Phase-3"}
      </h1>

      {/* Dark Mode Toggle Button */}
      <button
        onClick={toggleDarkMode}
        className="absolute right-4 p-2 rounded-full focus:outline-none"
        style={{
          backgroundColor: isDarkMode ? "#f1f5f9" : "#1e293b",
          color: isDarkMode ? "#1e293b" : "#f1f5f9",
        }}
      >
        {isDarkMode ? <FaSun size={18} /> : <FaMoon size={18} />}
      </button>
    </header>
  );
};

export default Header;
