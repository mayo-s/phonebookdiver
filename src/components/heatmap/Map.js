import React, { Component } from 'react';
import Filterbar from './Filterbar';
import Heatmap from './Heatmap';

class Map extends Component {

  state = {
    collection: '',
    field: '',
    search_string: '',
    heatMapData: {
      positions: [
        [52.5200, 13.3718, 1],
        [52.5200, 13.2020, 0.9],
        [52.5252, 13.5000, 0.5],
        [52.4244, 13.7498, 0.3],
        [52.4871245, 13.523143, 0.1],
        [54.3753392, 13.0219532, 0.4],
        [54.374027, 13.021522342, 0.7],
        [52.1485886, 8.52067245666357, 1]
      ]
    }
  }

  handleChange = (e) => {
    this.setState({
      [e.target.id]: e.target.value
    })
  }

  update_heatMapData = (response) => {
    let data = {
      positions: response
    }
    this.setState({heatMapData: data});
  }

  render() {
    return (
      <div className="dashboard">
        <Filterbar update_heatMapData={this.update_heatMapData}/>
        <Heatmap heatMapData={this.state.heatMapData} />
      </div>
    )
  }
}

export default Map