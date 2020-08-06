import React, { Component } from 'react';
import { Map, TileLayer } from 'react-leaflet';
import HeatmapLayer from './HeatmapLayer';

class Heatmap extends Component {
  
  state = {
    mapHidden: false,
    layerHidden: false,
    radius: 2,
    blur: 10,
    max: 0.5,
    // Center of Berlin
    center: {
      lat: 52.5200,
      lng: 13.4050,
    },
    zoom: 11,
  };
  
  render() {
    var heatMapData = {
      positions: [
        [ 52.5200, 13.3700 ], 
        [ 52.5252, 13.5000 ],
        [ 52.4244, 13.7498 ]
      ],
    };

    const position = [this.state.center.lat, this.state.center.lng];
    const gradient = {
      0.1: '#89BDE0', 0.2: '#96E3E6', 0.4: '#82CEB6',
      0.6: '#FAF3A5', 0.8: '#F5D98B', '1.0': '#DE9A96'
    };
    return (

      <Map center={position} zoom={this.state.zoom}>
        <HeatmapLayer
          fitBoundsOnLoad
          fitBoundsOnUpdate
          points={heatMapData.positions}
          latitudeExtractor={m => m[0]}
          longitudeExtractor={m => m[1]}
          intensityExtractor={m => parseFloat(m[2])} />
        <TileLayer
          attribution='&amp;copy <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
      </Map>

    );
  }
}

export default Heatmap