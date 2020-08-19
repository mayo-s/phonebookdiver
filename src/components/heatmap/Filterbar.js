import React, { Component } from 'react';

class Filterbar extends Component {

  state = {
    collection: '',
    field: '',
    search_str: '',
  }

  handleChange = (e) => {
    this.setState({
      [e.target.id]: e.target.value
    });
  }

  handleSubmit = (e) => {
    e.preventDefault();
    let url = 'http://localhost:5000/search?collection=' + this.state.collection + '&key=' + this.state.field + '&value=' + this.state.search_str;
    fetch(url)
      .then(response => response.json())
      .then(data => this.props.update_heatMapData(data));
  }

  render() {
    return (
      <div className="wrapper grey darken-2">
        <div className="row">
          <form onSubmit={this.handleSubmit}>
            <div className="col s6 m3">
              <div className="input-field">
                <label htmlFor="collection">Collection</label>
                <input className="white-text" type="text" id="collection" onChange={this.handleChange} />
              </div>
            </div>
            <div className="col s6 m3">
              <div className="input-field">
                <label htmlFor="field">Field</label>
                <input className="white-text" type="text" id="field" onChange={this.handleChange} />
              </div>
            </div>
            <div className="col s6 m3">
              <div className="input-field">
                <label htmlFor="search_str">Search string</label>
                <input className="white-text" type="text" id="search_str" onChange={this.handleChange} />
              </div>
            </div>
            <div className="col s6 m3">
              <button className="btn center-align" >Search</button>
            </div>
          </form>
        </div>
      </div>
    )
  }

}

export default Filterbar