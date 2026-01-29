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
            placeholder="Conor McGregor"
            value={redFighter}
            onChange={(e) => setRedFighter(e.target.value)}
          />
        </div>

        <div className="vs">VS</div>

        <div className="fighter blue">
          <h2>BLUE CORNER</h2>
          <input
            type="text"
            placeholder="Khabib Nurmagomedov"
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
          <div className="winner">WINNER: {prediction.predicted_winner}</div>
          <div className="prob red-prob">Red: {prediction.red_win_probability}</div>
          <div className="prob blue-prob">Blue: {prediction.blue_win_probability}</div>
          <div className="confidence">Confidence: {prediction.confidence}</div>
        </div>
      )}
    </div>
  );
}

export default App;
