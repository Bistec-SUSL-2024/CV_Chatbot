import React from 'react';
import { Candidate } from '../types';

interface CandidateListProps {
  candidates: Candidate[];
  onShowCV: (id: number) => void;
  onAskMore: (id: number) => void;
}

export function CandidateList({ candidates, onShowCV, onAskMore }: CandidateListProps) {
  return (
    <div className="bg-gray-800 p-4 rounded-lg text-white mb-4">
      <h2 className="text-lg font-semibold mb-3">Relevant Candidates:</h2>
      <div className="space-y-2">
        {candidates.map((candidate) => (
          <div key={candidate.id} className="flex items-center justify-between">
            <span className="font-medium">{candidate.title}</span>
            <div className="space-x-2">
              <button
                onClick={() => onShowCV(candidate.id)}
                className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm"
              >
                Show CV
              </button>
              <button
                onClick={() => onAskMore(candidate.id)}
                className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm"
              >
                Ask more info...
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}