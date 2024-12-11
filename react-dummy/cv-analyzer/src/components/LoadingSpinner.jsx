import React from "react";

const LoadingSpinner = ({
  size = "h-16 w-16",
  primaryColor = "border-blue-500",
  secondaryColor = "border-gray-300",
}) => {
  return (
    <div className="fixed inset-0 z-50 flex justify-center items-center bg-black bg-opacity-50 backdrop-blur-sm">
      <div className="relative flex justify-center items-center">
        {/* Outer pulsating ring */}
        <div
          className={`absolute rounded-full ${size} border-4 ${secondaryColor} opacity-50 animate-pulse`}
        ></div>

        {/* Inner spinning loader */}
        <div
          className={`animate-spin rounded-full ${size} border-4 border-t-4 ${primaryColor}`}
          style={{ borderTopColor: "transparent" }} // Make one side transparent for the spin effect
        ></div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
