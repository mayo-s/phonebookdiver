import React, { Component } from 'react';
import GoogleMapReact from 'google-map-react';

const AnyReactComponent = ({ text }) => <div>{text}</div>;

class Heatmap extends Component {
  static defaultProps = {
    center: {
      // Center to Berlin
      lat: 52.5200,
      lng: 13.4050
    },
    zoom: 11
  };

  render() {
    var heatMapData = {    
      positions: [
        {lat: 52.5200, lng: 13.3700},
        {lat: 52.5252, lng: 13.5000},
        {lat: 52.4244, lng: 13.7498}
      ],
      options: {   
        radius: 50,   
        opacity: 0.6,
    }};

    return (
      <div style={{ height: '90vh', width: '100%' }}>
        <GoogleMapReact
          bootstrapURLKeys={{ key: process.env.REACT_APP_GOOGLE_API_KEY }}
          defaultCenter={this.props.center}
          defaultZoom={this.props.zoom}
          heatmapLibrary={true}
          heatmap={heatMapData}
        >

          <AnyReactComponent
            lat={52.5200}
            lng={13.4050}
            text="Center"
          />
        </GoogleMapReact>
      </div>
    );
  }
}

export default Heatmap
