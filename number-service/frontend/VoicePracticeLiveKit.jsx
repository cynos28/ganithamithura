import React, { useState, useEffect, useRef } from 'react';
import {
  LiveKitRoom,
  useRoomContext,
  useLocalParticipant,
  RoomAudioRenderer,
  useTracks,
} from '@livekit/components-react';
import { Track } from 'livekit-client';
import { Mic, MicOff, Loader, Award, HelpCircle, RefreshCw, Volume2, Lightbulb, AlertCircle } from 'lucide-react';
import '@livekit/components-styles';

const API_BASE_URL = 'http://localhost:5000';

const VoicePracticeLiveKit = () => {
  const [token, setToken] = useState('');
  const [liveKitUrl, setLiveKitUrl] = useState('');
  const [roomName, setRoomName] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const [difficulty, setDifficulty] = useState('easy');
  const [error, setError] = useState(null);
  const [connectionAttempt, setConnectionAttempt] = useState(0);

  useEffect(() => {
    initializeRoom();
  }, []);

  const initializeRoom = async () => {
    setIsConnecting(true);
    setError(null);
    
    try {
      console.log('Requesting LiveKit token...');
      const response = await fetch(`${API_BASE_URL}/livekit/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          room: `math-practice-${Date.now()}`,
          participant: `student-${Math.floor(Math.random() * 9999)}`,
          difficulty: difficulty
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Token response:', data);
      
      if (data.success) {
        setToken(data.token);
        setLiveKitUrl(data.url);
        setRoomName(data.room);
        console.log('LiveKit configured:', data.url);
      } else {
        throw new Error(data.error || 'Failed to get token');
      }
    } catch (error) {
      console.error('Failed to initialize room:', error);
      setError(error.message);
      setConnectionAttempt(prev => prev + 1);
    } finally {
      setIsConnecting(false);
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl p-8 max-w-2xl">
          <div className="flex items-center gap-4 mb-6">
            <AlertCircle className="text-red-500 flex-shrink-0" size={48} />
            <div>
              <h2 className="text-2xl font-bold text-red-800 mb-2">
                Connection Error
              </h2>
              <p className="text-gray-600">{error}</p>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-blue-800 mb-2">Checklist:</h3>
            <ul className="text-sm text-blue-700 space-y-2">
              <li>✓ Flask backend running on port 5000?</li>
              <li>✓ LiveKit Cloud credentials in <code className="bg-blue-100 px-2 py-1 rounded">.env</code>?</li>
              <li>✓ Check <code className="bg-blue-100 px-2 py-1 rounded">LIVEKIT_URL</code>, <code className="bg-blue-100 px-2 py-1 rounded">LIVEKIT_API_KEY</code>, <code className="bg-blue-100 px-2 py-1 rounded">LIVEKIT_API_SECRET</code></li>
              <li>✓ Visit <a href="https://cloud.livekit.io" className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">cloud.livekit.io</a> to get credentials</li>
            </ul>
          </div>

          <div className="flex gap-3">
            <button
              onClick={initializeRoom}
              className="flex items-center gap-2 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <RefreshCw size={18} />
              Retry Connection
            </button>

            <button
              onClick={() => window.open('https://cloud.livekit.io', '_blank')}
              className="flex items-center gap-2 px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
            >
              Get LiveKit Credentials
            </button>
          </div>

          {connectionAttempt > 2 && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                <strong>Still having issues?</strong> Make sure your Flask backend is running and check the browser console (F12) for detailed error messages.
              </p>
            </div>
          )}
        </div>
      </div>
    );
  }

  if (!token || isConnecting) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-xl p-8 text-center">
          <Loader className="mx-auto mb-4 animate-spin text-purple-600" size={48} />
          <h2 className="text-2xl font-bold text-purple-800 mb-2">
            Connecting to LiveKit Cloud...
          </h2>
          <p className="text-gray-600">
            Setting up your voice practice session
          </p>
          <div className="mt-4 text-sm text-gray-500">
            Attempt: {connectionAttempt + 1}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-purple-800 mb-2">
            🎤 Voice Math Practice
          </h1>
        </div>

        <LiveKitRoom
          token={token}
          serverUrl={liveKitUrl}
          connect={true}
          audio={true}
          video={false}
          onConnected={() => {
            console.log('Connected to LiveKit room!');
          }}
          onDisconnected={(reason) => {
            console.log('Disconnected from room:', reason);
            setToken('');
            setTimeout(() => initializeRoom(), 2000);
          }}
          onError={(error) => {
            console.error('LiveKit error:', error);
            setError(error.message || 'Connection error occurred');
          }}
        >
          <VoicePracticeRoom
            difficulty={difficulty}
            setDifficulty={setDifficulty}
            roomName={roomName}
          />
          <RoomAudioRenderer />
        </LiveKitRoom>
      </div>
    </div>
  );
};

// Main room component with LiveKit context
const VoicePracticeRoom = ({ difficulty, setDifficulty, roomName }) => {
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [score, setScore] = useState(0);
  const [totalAttempts, setTotalAttempts] = useState(0);
  const [showHint, setShowHint] = useState(false);
  const [hint, setHint] = useState('');
  const [transcript, setTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [consecutiveCorrect, setConsecutiveCorrect] = useState(0);
  const [isRecording, setIsRecording] = useState(false);

  const room = useRoomContext();
  const { localParticipant } = useLocalParticipant();
  const recognitionRef = useRef(null);

  // Setup Web Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';
      
      recognition.onstart = () => {
        console.log('Speech recognition started');
        setIsListening(true);
      };
      
      recognition.onresult = (event) => {
        const speechResult = event.results[0][0].transcript;
        console.log('Speech result:', speechResult);
        setTranscript(speechResult);
        handleSpeechResult(speechResult);
      };
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
      
      recognition.onend = () => {
        console.log('Speech recognition ended');
        setIsListening(false);
      };
      
      recognitionRef.current = recognition;
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [currentQuestion]);

  // Generate initial question
  useEffect(() => {
    generateNewQuestion();
  }, [difficulty]);

  // Listen for room events
  useEffect(() => {
    if (!room) return;

    console.log('Room connected:', room.name);
    
  }, [room]);

  const generateNewQuestion = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/voice/generate?difficulty=${difficulty}`);
      const data = await response.json();
      
      if (data.success) {
        setCurrentQuestion(data);
        setFeedback(null);
        setShowHint(false);
        setHint('');
        setTranscript('');
        speakQuestion(data.question);
      }
    } catch (error) {
      console.error('Failed to generate question:', error);
    }
  };

  const speakQuestion = (text) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1.1;
      utterance.volume = 1;
      window.speechSynthesis.speak(utterance);
    }
  };

  const startListening = async () => {
    if (!recognitionRef.current || !currentQuestion) return;
    
    setTranscript('');
    setFeedback(null);
    
    try {
      // Enable microphone in LiveKit room
      if (localParticipant) {
        await localParticipant.setMicrophoneEnabled(true);
        setIsRecording(true);
      }
      
      // Start speech recognition
      recognitionRef.current.start();
      
    } catch (error) {
      console.error('Failed to start listening:', error);
      setFeedback({
        message: 'Failed to start microphone. Please check permissions!',
        type: 'error',
        color: '#f44336'
      });
    }
  };

  const stopListening = async () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
    
    if (localParticipant) {
      await localParticipant.setMicrophoneEnabled(false);
      setIsRecording(false);
    }
  };

  const handleSpeechResult = async (speechText) => {
    if (!currentQuestion) return;
    
    // Stop recording after getting result
    if (localParticipant) {
      await localParticipant.setMicrophoneEnabled(false);
      setIsRecording(false);
    }
    
    setTotalAttempts(prev => prev + 1);
    
    try {
      const response = await fetch(`${API_BASE_URL}/voice/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: speechText,
          answer: currentQuestion.answer,
          type: currentQuestion.type,
          params: currentQuestion.params
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        setFeedback(result.feedback);
        
        if (result.is_correct) {
          setScore(prev => prev + 1);
          setConsecutiveCorrect(prev => prev + 1);
          speakQuestion(result.feedback.message);
          
          setTimeout(() => {
            generateNewQuestion();
          }, 2500);
          
          // Auto-increase difficulty
          if (consecutiveCorrect + 1 >= 3 && difficulty === 'easy') {
            setDifficulty('medium');
            setConsecutiveCorrect(0);
          } else if (consecutiveCorrect + 1 >= 5 && difficulty === 'medium') {
            setDifficulty('hard');
            setConsecutiveCorrect(0);
          }
        } else {
          setConsecutiveCorrect(0);
          speakQuestion(result.feedback.message);
        }
      }
      
    } catch (error) {
      console.error('Validation failed:', error);
      setFeedback({
        message: 'Failed to check answer. Please try again!',
        type: 'error',
        color: '#f44336'
      });
    }
  };

  const getHint = async () => {
    if (!currentQuestion) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/voice/hints`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: currentQuestion.type,
          params: currentQuestion.params
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setHint(data.hint);
        setShowHint(true);
        speakQuestion(data.hint);
      }
    } catch (error) {
      console.error('Failed to get hint:', error);
    }
  };

  const accuracy = totalAttempts > 0 ? ((score / totalAttempts) * 100).toFixed(1) : 0;

  return (
    <>
      {/* Stats Bar */}
      <div className="flex justify-center gap-4 mb-6 flex-wrap">
        <div className="bg-white px-4 py-2 rounded-full shadow">
          <span className="text-sm text-gray-600">Score: </span>
          <strong className="text-green-600">{score}</strong>
        </div>
        <div className="bg-white px-4 py-2 rounded-full shadow">
          <span className="text-sm text-gray-600">Accuracy: </span>
          <strong className="text-blue-600">{accuracy}%</strong>
        </div>
        <div className="bg-white px-4 py-2 rounded-full shadow">
          <span className="text-sm text-gray-600">Level: </span>
          <strong className="text-purple-600 capitalize">{difficulty}</strong>
        </div>
        {consecutiveCorrect > 0 && (
          <div className="bg-yellow-100 px-4 py-2 rounded-full shadow border border-yellow-300">
            <span className="text-sm">🔥 Streak: </span>
            <strong className="text-orange-600">{consecutiveCorrect}</strong>
          </div>
        )}
        <div className="bg-green-100 px-4 py-2 rounded-full shadow border border-green-300">
          <span className="text-sm">☁️ LiveKit Cloud</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Question Area */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow-xl p-8">
            {currentQuestion ? (
              <>
                <div className="text-center mb-6">
                  <h2 className="text-3xl font-bold text-purple-700 mb-4">
                    {currentQuestion.question}
                  </h2>
                  
                  <button
                    onClick={() => speakQuestion(currentQuestion.question)}
                    className="flex items-center gap-2 mx-auto px-4 py-2 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-lg transition-colors"
                  >
                    <Volume2 size={18} />
                    Repeat Question
                  </button>
                </div>

                {showHint && hint && (
                  <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-4 mb-6">
                    <div className="flex items-start gap-3">
                      <Lightbulb className="text-yellow-600 flex-shrink-0" size={24} />
                      <div>
                        <p className="font-semibold text-yellow-800 mb-1">Hint:</p>
                        <p className="text-yellow-700">{hint}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Microphone Control */}
                <div className="text-center">
                  <button
                    onClick={isListening ? stopListening : startListening}
                    className={`relative mx-auto mb-4 w-32 h-32 rounded-full flex items-center justify-center transition-all duration-300 ${
                      isListening 
                        ? 'bg-red-500 hover:bg-red-600 animate-pulse shadow-lg shadow-red-300' 
                        : 'bg-green-500 hover:bg-green-600 shadow-lg hover:shadow-xl'
                    }`}
                  >
                    {isListening ? (
                      <Mic className="text-white" size={48} />
                    ) : (
                      <MicOff className="text-white" size={48} />
                    )}
                    
                    {isListening && (
                      <div className="absolute inset-0 rounded-full border-4 border-red-300 animate-ping" />
                    )}
                    
                    {isRecording && (
                      <div className="absolute -top-2 -right-2 bg-red-600 text-white text-xs px-2 py-1 rounded-full">
                        REC
                      </div>
                    )}
                  </button>
                  
                  <p className="text-lg font-semibold mb-2">
                    {isListening ? '🎤 Listening...' : '🎤 Click to Speak'}
                  </p>
                  
                  {transcript && (
                    <div className="bg-gray-100 rounded-lg p-4 mb-4">
                      <p className="text-sm text-gray-600 mb-1">You said:</p>
                      <p className="text-lg font-semibold text-gray-800">{transcript}</p>
                    </div>
                  )}

                  <div className="text-xs text-gray-500 mt-4">
                    Room: {roomName}
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-8">
                <Loader className="mx-auto mb-4 animate-spin text-purple-600" size={48} />
                <p className="text-gray-600">Loading question...</p>
              </div>
            )}
          </div>

          {/* Feedback */}
          {feedback && (
            <div 
              className="rounded-lg shadow-lg p-6"
              style={{ 
                backgroundColor: `${feedback.color}20`, 
                borderLeft: `4px solid ${feedback.color}` 
              }}
            >
              <div className="flex items-center gap-3">
                {feedback.type === 'success' && (
                  <Award size={32} style={{ color: feedback.color }} />
                )}
                <div>
                  <h3 className="text-xl font-bold mb-1" style={{ color: feedback.color }}>
                    {feedback.type === 'success' ? 'Correct!' : 'Try Again!'}
                  </h3>
                  <p className="text-gray-700 text-lg">{feedback.message}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Controls */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Controls</h3>
            <div className="space-y-3">
              <button
                onClick={getHint}
                disabled={!currentQuestion || showHint}
                className="w-full flex items-center gap-2 px-4 py-2 bg-yellow-500 hover:bg-yellow-600 disabled:bg-gray-300 text-white rounded-lg transition-colors"
              >
                <HelpCircle size={18} />
                Get Hint
              </button>
              
              <button
                onClick={generateNewQuestion}
                disabled={!currentQuestion}
                className="w-full flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white rounded-lg transition-colors"
              >
                <RefreshCw size={18} />
                New Question
              </button>
              
              <button
                onClick={() => {
                  setScore(0);
                  setTotalAttempts(0);
                  setConsecutiveCorrect(0);
                  generateNewQuestion();
                }}
                className="w-full px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition-colors"
              >
                Reset Score
              </button>
            </div>
          </div>

          {/* Difficulty Selector */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Difficulty</h3>
            <div className="space-y-2">
              {['easy', 'medium', 'hard'].map((level) => (
                <button
                  key={level}
                  onClick={() => {
                    setDifficulty(level);
                    setConsecutiveCorrect(0);
                  }}
                  className={`w-full px-4 py-2 rounded-lg transition-colors ${
                    difficulty === level
                      ? 'bg-purple-500 text-white'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                  }`}
                >
                  <span className="capitalize">{level}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default VoicePracticeLiveKit;