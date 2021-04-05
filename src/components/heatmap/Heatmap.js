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
    max: 0.1,
  };

  getMaxIntensityValue = () => {
    let max = 0
    for (let i of this.props.heatMapData.positions) {
      if (max < i[2]) max = i[2]
    }
    return max
  }

  render() {
    const center_berlin = [this.state.center.lat, this.state.center.lng];
    const points = this.props.heatMapData.positions;
    const maxIntensityValue = this.getMaxIntensityValue()
    const zoom = this.state.zoom;
    const radius = this.state.radius;
    const blur = this.state.blur;
    const max = this.state.max;
    const gradient = // { 0.1: 'green', 0.2: '#FFFF33', 0.4: '#FFB266', 0.6: '#FF9933', 0.8: '#FF8000', 1.0: '#FF3333' }
    {
      0.1: 'darkblue', 0.2: '#96E3E6', 0.4: '#82CEB6',
      0.6: '#FAF3A5', 0.8: '#F5D98B', 1.0: '#DE9A96'
    };

    return (

      <Map center={center_berlin} zoom={zoom}>
        <HeatmapLayer
          fitBoundsOnLoad
          fitBoundsOnUpdate
          gradient={gradient}
          points={points}
          longitudeExtractor={m => m[1]}
          latitudeExtractor={m => m[0]}
          intensityExtractor={m => parseFloat(m[2]/maxIntensityValue * 10)}
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