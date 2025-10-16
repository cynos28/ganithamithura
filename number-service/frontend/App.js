import React, { useState } from 'react';
import './App.css';
import HandwritingApp from './HandwritingApp';
import VoicePracticeLiveKit from './VoicePracticeLiveKit';
import { PenTool, Radio } from 'lucide-react';

function App() {
  const [activeMode, setActiveMode] = useState('handwriting');

  return (
    <div className="App">
      <nav className="bg-white shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-2xl font-bold text-indigo-600">
              Math Learning Studio
            </h1>
            
            <div className="flex gap-3">
              <button
                onClick={() => setActiveMode('handwriting')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all ${
                  activeMode === 'handwriting'
                    ? 'bg-indigo-600 text-white shadow-lg'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <PenTool size={20} />
                Handwriting
              </button>

              <button
                onClick={() => setActiveMode('voice')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all ${
                  activeMode === 'voice'
                    ? 'bg-green-600 text-white shadow-lg'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Radio size={20} />
                Voice Practice
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="min-h-screen">
        {activeMode === 'handwriting' ? <HandwritingApp /> : <VoicePracticeLiveKit />}
      </div>
    </div>
  );
}

export default App;