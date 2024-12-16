const CandidatesList = ({ candidates, onShowCV, onChat }) => {
    return (
      <div className="bg-gray-800 p-4 rounded-lg text-white max-w-2xl mx-auto">
        <h4 className="text-lg mb-4 text-center">Relevant Candidates</h4>
        {candidates.map((candidate) => (
          <div
            key={candidate.id}
            className="flex justify-between items-center p-2 bg-gray-700 rounded mb-2"
          >
            <span>{candidate.title}</span>
            <div className="flex space-x-2">
              <button
                className="bg-blue-500 px-4 py-2 rounded"
                onClick={() => onShowCV(candidate)}
              >
                Show CV
              </button>
              <button
                className="bg-purple-500 px-4 py-2 rounded"
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
  