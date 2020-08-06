import React, { Component } from 'react';
import Filterbar from './Filterbar';
import Heatmap from './Heatmap';

class Map extends Component {
  render() {
    return (
      <div className="dashboard">
        <Filterbar />
        <Heatmap />
      </div>
    )
  }
}

export default Map