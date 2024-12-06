const CandidatesList = ({ candidates, selectedCandidateId, onShowCV, onChat }) => {
    return (
      <div className="bg-white p-4 rounded-lg text-black shadow-lg max-w-4xl mx-auto">
        <h4
          className="text-lg mb-4 font-bold shadow-lg text-center"
          style={{ fontFamily: "'Inter', sans-serif" }}
        >
          Relevant Candidates
        </h4>
        {candidates.map((candidate) => (
          <div
            key={candidate.id}
            className={`flex justify-between items-center p-2 rounded mb-2 transition-all duration-200 ${
              candidate.id === selectedCandidateId
                ? "font-bold bg-blue-100"
                : "bg-gray-100 hover:bg-gray-200"
            }`}
          >
            <span>{candidate.title}</span>
            <div className="flex space-x-2">
              <button
                className="bg-blue-300 px-4 py-2 rounded hover:bg-blue-600"
                onClick={() => onShowCV(candidate)}
              >
                Show CV
              </button>
              <button
                className="bg-orange-300 px-4 py-2 rounded hover:bg-orange-600"
                onClick={() => onChat(candidate)}
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
  