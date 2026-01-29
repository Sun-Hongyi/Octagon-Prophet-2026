import React, { useState } from 'react';
import './App.css';

function App() {
  const [redFighter, setRedFighter] = useState('');
  const [blueFighter, setBlueFighter] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const handlePredict = async () => {
    if (!redFighter || !blueFighter) {
      alert('Please enter both fighters!');
      return;
    }

    setLoading(true);
    
    try {
      const response = await fetch(
        `http://localhost:8000/predict-fight?red_name=${encodeURIComponent(redFighter)}&blue_name=${encodeURIComponent(blueFighter)}`
      );
      
      if (!response.ok) throw new Error('Prediction failed');
      
      const data = await response.json();
      console.log('API Response:', data); // Debug log
      setPrediction(data);
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>🥊 Octagon Prophet 2026</h1>
        <p>Machine Learning UFC Fight Predictor</p>
      </header>

      <div className="fight-inputs">
        <div className="fighter red">
          <h2>RED CORNER</h2>
          <input
            type="text"
            placeholder="Enter fighter name"
            value={redFighter}
            onChange={(e) => setRedFighter(e.target.value)}
          />
        </div>

        <div className="vs">VS</div>

        <div className="fighter blue">
          <h2>BLUE CORNER</h2>
          <input
            type="text"
            placeholder="Enter fighter name"
            value={blueFighter}
            onChange={(e) => setBlueFighter(e.target.value)}
          />
        </div>
      </div>

      <button onClick={handlePredict} disabled={loading}>
        {loading ? 'PREDICTING...' : 'PREDICT WINNER 🚀'}
      </button>

      {prediction && (
        <div className="prediction">
          <h3>🎯 PREDICTION</h3>
          <div className="fight-name">{prediction.fight}</div>
          <div className="winner">WINNER: {prediction.prediction}</div>
          <div className="confidence">Confidence: {prediction.confidence}</div>
          
          {/* Display probabilities - FIXED */}
          {prediction.probabilities && (
            <div className="probabilities">
              <div className="prob">
                {redFighter}: {prediction.probabilities[redFighter] || 'N/A'}
              </div>
              <div className="prob">
                {blueFighter}: {prediction.probabilities[blueFighter] || 'N/A'}
              </div>
            </div>
          )}
          
          {/* Show if it's a close fight */}
          {prediction.is_close_fight && (
            <div className="close-fight">⚠️ This is a close fight!</div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
