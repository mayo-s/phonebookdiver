import React, { Component } from 'react';
import { Map, TileLayer } from 'react-leaflet';
import HeatmapLayer from 'react-leaflet-heatmap-layer';

class Heatmap extends Component {

  state = {
    mapHidden: false,
    layerHidden: false,
    center: {
      // Center of Berlin
      lat: 52.5200,
      lng: 13.4050,
    },
    zoom: 11,
    radius: 10,
    blur: 14,
    max: 0.1
  };

  render() {
    const position = [this.state.center.lat, this.state.center.lng];
    const points = this.props.heatMapData.positions;
    console.log(points)
    const zoom = this.state.zoom;
    const radius = this.state.radius;
    const blur = this.state.blur;
    const max = this.state.max;
    const gradient = // { 0.0: 'green', 0.5: 'yellow', 1.0: 'red'}
    { 0.0: 'green', 0.2: '#FFFF33', 0.4: '#FFB266', 0.8: '#FF8000', 1.0: 'red' }
    // {
    //   0.1: '#89BDE0', 0.2: '#96E3E6', 0.4: '#82CEB6',
    //   0.6: '#FAF3A5', 0.8: '#F5D98B', 1.0: '#DE9A96'
    // };

    return (

      <Map center={position} zoom={zoom}>
        <HeatmapLayer
          fitBoundsOnLoad
          fitBoundsOnUpdate
          gradient={gradient}
          points={points}
          longitudeExtractor={m => m[1]}
          latitudeExtractor={m => m[0]}
          intensityExtractor={m => parseFloat(m[2] * 10)} 
          radius={radius} 
          blur={blur}
          max={max}
          />
        <TileLayer
          attribution='&amp;copy <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
      </Map>
    );
  }
}

export default Heatmap