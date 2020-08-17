import React, { Component } from 'react';
import Filterbar from './Filterbar';
import Heatmap from './Heatmap';

class Map extends Component {

  state = {
    collection: '',
    field: '',
    search_string: '',
    coords: []
  }

  handleChange = (e) => {
    this.setState({
      [e.target.id]: e.target.value
    })
  }

  get_coords = (response) => {
    this.setState({coords: response});
    // console.log(this.state.coords);
  }

  render() {
    return (
      <div className="dashboard">
        <Filterbar get_coords={this.get_coords}/>
        <Heatmap />
      </div>
    )
  }
}

export default Map