const CandidatesList = ({ candidates, selectedCandidateId, onShowCV, onChat }) => {
  return (
    <div className="bg-white p-4 rounded-lg text-black shadow-lg max-w-4xl mx-auto">
      <h4 className="text-lg mb-4 font-bold shadow-lg text-center" style={{ fontFamily: "'Inter', sans-serif" }}>
        Relevant Candidates
      </h4>
      {candidates.map((candidate) => (
        <div
          key={candidate.cv_id}
          className={`flex justify-between items-center p-2 rounded mb-2 transition-all duration-200 ${
            candidate.cv_id === selectedCandidateId ? "font-bold bg-blue-100" : "bg-gray-100 hover:bg-gray-200"
          }`}
        >
          <span>{candidate.cv_id}</span> {/* Displaying cv_id */}
          <span className="text-sm text-gray-500">
            Score: {candidate.score.toFixed(3)} {/* Round the score to 3 decimal places */}
          </span>
          <div className="flex space-x-2">
          <button
              className="bg-blue-300 px-4 py-2 rounded hover:bg-blue-600 hover:text-white"
              onClick={(e) => {
                e.stopPropagation(); // Prevent interfering with parent click events
                onShowCV(candidate); // Call the onShowCV handler
              }}
            >
              Show CV
            </button>
            <button
              className="bg-blue-300 px-4 py-2 rounded hover:bg-gray-500 hover:text-white"
              onClick={() => onChat(candidate)} // Triggers the chat function
            >
              Ask More Info
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CandidatesList;
