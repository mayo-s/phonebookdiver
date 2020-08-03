import React, { useState, useEffect } from 'react';

function App() {
  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    fetch('/time').then(res => res.json()).then(data => {
      setCurrentTime(data.time);
    });
  }, []);

  return (
    <div className="App">

      <h1>The Phonebookdiver</h1>

      <p>The current time is {currentTime}.</p>
    </div>
  );
}

export default App