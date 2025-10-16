import React, { useState, useRef, useEffect } from 'react';
import { Camera, RotateCcw, Brain, CheckCircle, XCircle, Upload, RefreshCw, Server } from 'lucide-react';

const API_BASE_URL = 'http://localhost:5000';

const HandwritingApp = () => {
  const [isDrawing, setIsDrawing] = useState(false);
  const [lastPos, setLastPos] = useState({ x: 0, y: 0 });
  const [predictions, setPredictions] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentProblem, setCurrentProblem] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [score, setScore] = useState(0);
  const [attempts, setAttempts] = useState(0);
  const [apiStatus, setApiStatus] = useState('checking');
  const [modelInfo, setModelInfo] = useState(null);
  
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const [context, setContext] = useState(null);

  // Check API health and load initial problem
  useEffect(() => {
    checkApiHealth();
    getModelInfo();
    generateNewProblem();
  }, []);

  // Initialize canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.strokeStyle = '#000';
      ctx.lineWidth = 3;
      setContext(ctx);
      clearCanvas();
    }
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      const data = await response.json();
      setApiStatus(data.model_loaded ? 'connected' : 'model_not_loaded');
    } catch (error) {
      console.error('API health check failed:', error);
      setApiStatus('disconnected');
    }
  };

  const getModelInfo = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/model/info`);
      const data = await response.json();
      if (data.success) {
        setModelInfo(data);
      }
    } catch (error) {
      console.error('Failed to get model info:', error);
    }
  };

  const generateNewProblem = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/generate/problem`);
      const data = await response.json();
      if (data.success) {
        setCurrentProblem(data);
        setAttempts(0);
        setFeedback(null);
        setPredictions([]);
        clearCanvas();
      }
    } catch (error) {
      console.error('Failed to generate problem:', error);
      // Fallback to local problem generation
      const fallbackProblems = [
        { question: "What comes after 3?", answer: 4, type: "sequence" },
        { question: "What comes before 7?", answer: 6, type: "sequence" },
        { question: "2 + 3 = ?", answer: 5, type: "addition" }
      ];
      const randomProblem = fallbackProblems[Math.floor(Math.random() * fallbackProblems.length)];
      setCurrentProblem(randomProblem);
    }
  };

  const getCoordinates = (event) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    return {
      x: (event.clientX - rect.left) * scaleX,
      y: (event.clientY - rect.top) * scaleY
    };
  };

  const startDrawing = (event) => {
    setIsDrawing(true);
    const coords = getCoordinates(event);
    setLastPos(coords);
  };

  const draw = (event) => {
    if (!isDrawing || !context) return;
    
    const coords = getCoordinates(event);
    
    context.beginPath();
    context.moveTo(lastPos.x, lastPos.y);
    context.lineTo(coords.x, coords.y);
    context.stroke();
    
    setLastPos(coords);
  };

  const stopDrawing = () => {
    setIsDrawing(false);
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (context && canvas) {
      context.fillStyle = '#fff';
      context.fillRect(0, 0, canvas.width, canvas.height);
      setPredictions([]);
      setFeedback(null);
    }
  };

  const recognizeHandwriting = async () => {
    console.log('get');
    if (!canvasRef.current || apiStatus !== 'connected') return;
    
    setIsProcessing(true);
    
    try {
      // Convert canvas to base64
      const canvas = canvasRef.current;
      const imageData = canvas.toDataURL('image/png');
      
      // Send to API
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: imageData,
          top_k: 5,
          expected_answer: currentProblem?.answer
        })
      });
            
      const result = await response.json();
      console.log(result);

      
      if (result.success) {
        setPredictions(result.predictions);
        
        const newAttempts = attempts + 1;
        setAttempts(newAttempts);
        
        // Generate feedback
        const isCorrect = result.is_correct;
        const topPrediction = result.predictions[0];
        const feedbackData = generateFeedback(isCorrect, topPrediction, newAttempts);
        setFeedback(feedbackData);
        
        if (isCorrect) {
          setScore(score + 1);
          setTimeout(() => {
            generateNewProblem();
          }, 2000);
        }
      } else {
        setFeedback({
          type: 'error',
          message: result.error || 'Recognition failed. Please try again!',
          color: '#f44336'
        });
      }
      
    } catch (error) {
      console.error('Recognition failed:', error);
      setFeedback({
        type: 'error',
        message: 'Network error. Please check your connection!',
        color: '#f44336'
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const generateFeedback = (isCorrect, prediction, attemptCount) => {
    if (isCorrect && prediction.confidence > 0.8) {
      return {
        type: 'success',
        message: `Perfect! Great handwriting! ⭐ (${prediction.percentage.toFixed(1)}% confidence)`,
        color: '#4caf50',
        icon: <CheckCircle size={24} />
      };
    } else if (isCorrect) {
      return {
        type: 'success',
        message: `Correct! Nice work! 🎉 (${prediction.percentage.toFixed(1)}% confidence)`,
        color: '#4caf50',
        icon: <CheckCircle size={24} />
      };
    } else {
      const encouragement = attemptCount >= 3 
        ? `Good try! The answer is ${currentProblem.answer}. Let's try a new one!`
        : `I see "${prediction.digit}" but the answer is ${currentProblem.answer}. Try again! 💪`;
      
      return {
        type: 'error',
        message: encouragement,
        color: '#f44336',
        icon: <XCircle size={24} />
      };
    }
  };

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || apiStatus !== 'connected') return;
    
    setIsProcessing(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('top_k', '5');
      if (currentProblem?.answer !== undefined) {
        formData.append('expected_answer', currentProblem.answer.toString());
      }
      
      const response = await fetch(`${API_BASE_URL}/predict/file`, {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      if (result.success) {
        // Display uploaded image on canvas
        const reader = new FileReader();
        reader.onload = (e) => {
          const img = new Image();
          img.onload = () => {
            const canvas = canvasRef.current;
            const ctx = canvas.getContext('2d');
            
            ctx.fillStyle = '#fff';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const scale = Math.min(canvas.width / img.width, canvas.height / img.height);
            const scaledWidth = img.width * scale;
            const scaledHeight = img.height * scale;
            const x = (canvas.width - scaledWidth) / 2;
            const y = (canvas.height - scaledHeight) / 2;
            
            ctx.drawImage(img, x, y, scaledWidth, scaledHeight);
          };
          img.src = e.target.result;
        };
        reader.readAsDataURL(file);
        
        setPredictions(result.predictions);
        
        const newAttempts = attempts + 1;
        setAttempts(newAttempts);
        
        const isCorrect = result.is_correct;
        const topPrediction = result.predictions[0];
        const feedbackData = generateFeedback(isCorrect, topPrediction, newAttempts);
        setFeedback(feedbackData);
        
        if (isCorrect) {
          setScore(score + 1);
          setTimeout(() => {
            generateNewProblem();
          }, 2000);
        }
      } else {
        setFeedback({
          type: 'error',
          message: result.error || 'Upload failed. Please try again!',
          color: '#f44336'
        });
      }
      
    } catch (error) {
      console.error('Upload failed:', error);
      setFeedback({
        type: 'error',
        message: 'Upload failed. Please check your connection!',
        color: '#f44336'
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const getStatusColor = () => {
    switch (apiStatus) {
      case 'connected': return 'text-green-600';
      case 'disconnected': return 'text-red-600';
      case 'model_not_loaded': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusText = () => {
    switch (apiStatus) {
      case 'connected': return 'API Connected';
      case 'disconnected': return 'API Disconnected';
      case 'model_not_loaded': return 'Model Not Loaded';
      default: return 'Checking...';
    }
  };

  if (apiStatus === 'disconnected') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-red-100 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <Server className="mx-auto mb-4 text-red-500" size={48} />
          <h2 className="text-2xl font-bold text-red-800 mb-2">API Connection Failed</h2>
          <p className="text-red-600 mb-4">
            Cannot connect to the Flask API server. Please make sure the server is running on {API_BASE_URL}
          </p>
          <button
            onClick={checkApiHealth}
            className="flex items-center gap-2 mx-auto px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
          >
            <RefreshCw size={18} />
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-indigo-800 mb-2">
            AI Math Handwriting Practice
          </h1>
          <p className="text-gray-600">Write your answers and let our AI model check them!</p>
          
          {/* Status and Stats */}
          <div className="flex justify-center gap-6 mt-4 text-sm">
            <span className={`flex items-center gap-1 ${getStatusColor()}`}>
              <Server size={16} />
              {getStatusText()}
            </span>
            <span className="bg-white px-3 py-1 rounded-full">
              Score: <strong>{score}</strong>
            </span>
            <span className="bg-white px-3 py-1 rounded-full">
              Attempts: <strong>{attempts}</strong>
            </span>
          </div>
          
          {/* Model Info */}
          {modelInfo && (
            <div className="text-xs text-gray-500 mt-2">
              Model: {modelInfo.total_parameters.toLocaleString()} parameters
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Problem Display */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow-lg p-6 mb-6 text-center">
              {currentProblem ? (
                <>
                  <h2 className="text-3xl font-bold text-blue-600 mb-4">
                    {currentProblem.question}
                  </h2>
                  {attempts >= 2 && !feedback?.type === 'success' && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                      <p className="text-yellow-800">
                        💡 Hint: Take your time and write clearly! Expected answer: 0-9
                      </p>
                    </div>
                  )}
                </>
              ) : (
                <div className="animate-pulse">
                  <div className="h-8 bg-gray-300 rounded w-64 mx-auto"></div>
                </div>
              )}
            </div>
          </div>

          {/* Drawing Canvas */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-semibold">Write Your Answer</h3>
                <div className="flex gap-2">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={apiStatus !== 'connected'}
                    className="flex items-center gap-2 px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 rounded-lg transition-colors"
                  >
                    <Upload size={16} />
                    Upload Image
                  </button>
                </div>
              </div>
              
              <div className="border-2 border-gray-300 rounded-lg overflow-hidden mb-4 bg-white">
                <canvas
                  ref={canvasRef}
                  width={400}
                  height={300}
                  className="cursor-crosshair w-full"
                  onMouseDown={startDrawing}
                  onMouseMove={draw}
                  onMouseUp={stopDrawing}
                  onMouseLeave={stopDrawing}
                />
              </div>
              
              <div className="flex gap-3 justify-center">
                <button
                  onClick={clearCanvas}
                  className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                >
                  <RotateCcw size={18} />
                  Clear
                </button>
                
                <button
                  onClick={recognizeHandwriting}
                  disabled={isProcessing || apiStatus !== 'connected'}
                  className="flex items-center gap-2 px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 transition-colors"
                >
                  <Brain size={18} />
                  {isProcessing ? 'Checking...' : 'Check Answer'}
                </button>
              </div>
            </div>
          </div>

          {/* Results Panel */}
          <div className="space-y-6">
            {/* Feedback */}
            {feedback && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-center gap-3 mb-3">
                  {feedback.icon}
                  <h3 className="text-lg font-semibold" style={{ color: feedback.color }}>
                    {feedback.type === 'success' ? 'Correct!' : 'Try Again'}
                  </h3>
                </div>
                <p className="text-gray-700">{feedback.message}</p>
              </div>
            )}

            {/* Predictions */}
            {predictions.length > 0 && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-semibold mb-4">AI Predictions</h3>
                <div className="space-y-2">
                  {predictions.map((pred, index) => (
                    <div
                      key={index}
                      className={`flex justify-between items-center p-3 rounded-lg ${
                        index === 0 ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50'
                      }`}
                    >
                      <span className="font-semibold text-lg">{pred.digit}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${pred.confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-600">
                          {pred.percentage}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Controls */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Controls</h3>
              <div className="space-y-3">
                <button
                  onClick={generateNewProblem}
                  disabled={apiStatus !== 'connected'}
                  className="w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-400 transition-colors"
                >
                  New Problem
                </button>
                
                <button
                  onClick={() => {
                    setScore(0);
                    setAttempts(0);
                    generateNewProblem();
                  }}
                  className="w-full px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
                >
                  Reset Game
                </button>
                
                <button
                  onClick={checkApiHealth}
                  className="w-full px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                >
                  Check API Status
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HandwritingApp;