import React, { Component } from 'react';
import ResultTable from './ResultTable';

class Search extends Component {

  state = {
    cOptions: [],
    collection_start: '',
    collection_end: '',
    key: '',
    search_str: '',

    startError: '',
    keyError: '',
    strError: '',

    queryMsg: '',
    results: [],
  }

  handleSubmit = (e) => {
    e.preventDefault();
    const isValid = this.validateForm();

    if (isValid) {
      let queryMsg = 'Querying the years from ' + this.state.collection_start.substr(0, 4) + ' to ' + this.state.collection_end.substr(0, 4) + ' for ' + this.state.key + ' = ' + this.state.search_str + '.';
      this.setState({ queryMsg })
      let url = 'http://localhost:5000/search?start=' + this.state.collection_start + '&end=' + this.state.collection_end + '&key=' + this.state.key + '&value=' + this.state.search_str;
      fetch(url)
        .then(response => response.json())
        .then(data => this.update_resultView(data));
    }
  }

  validateForm = () => {
    let keyError, strError, startError = '';

    if (parseInt(this.state.collection_start.substr(0, 4)) > parseInt(this.state.collection_end.substr(0, 4))) {
      startError = 'First YEAR value must be lower than second.';
    }

    if (!this.state.key) {
      keyError = 'Please choose a FIELD to query';
    }
    if (!this.state.search_str || this.state.search_str.length < 2) {
      strError = 'Search string cannot be empty and must have at least 2 letters';
    }

    if (startError || keyError || strError) {
      this.setState({ startError, keyError, strError });
      return false;
    }

    this.setState({ startError, keyError, strError });
    return true
  }

  update_resultView = (data) => {
    let queryMsg = this.state.queryMsg + ' Found ' + data.length + ' entries.';
    this.setState({ queryMsg, results: data });
  }

  update_results = (results) => {
    this.setState({results})
  }

  handleChange = (e) => {
    this.setState({
      [e.target.id]: e.target.value
    });
  }

  getCollections = () => {
    let options = [];
    fetch('http://localhost:5000/all_collections')
      .then(response => response.json())
      .then(data => {
        let first = '9999_Q0';
        let last = '0000_Q0';
        for (let d in data) {
          options.push(<option value={d} key={d}>{d}</option>);
          if (parseInt(first.substr(0, 4)) > parseInt(d.substr(0, 4))) first = d;
          if (parseInt(last.substr(0, 4)) < parseInt(d.substr(0, 4))) last = d;
        }
        // by default range over all available collections
        this.setState({ cOptions: options, collection_start: first, collection_end: last });
      })
  }

  render() {
    if (!this.state.cOptions.length) this.getCollections();

    return (
      <div className='dashboard'>

        <div className="wrapper grey darken-2">
          <form onSubmit={this.handleSubmit}>

            <div className="row lmargin">
              <div className="input-field col s6 m3">
                <select className="browser-default" id="collection_start" onChange={this.handleChange} >
                  <option value="" disabled selected key="start_year">Choose Start YEAR to query</option>
                  {this.state.cOptions}
                </select>
                {this.state.startError ? (
                  <div style={{ fontSize: 12, color: "red" }}>{this.state.startError}</div>
                ) : null}
              </div>

              <div className="input-field col s6 m3">
                <select className="browser-default" id="collection_end" onChange={this.handleChange} >
                  <option value="" disabled selected key="end_year">Choose End YEAR to query</option>
                  {this.state.cOptions}
                </select>
              </div>
              <div className="input-field col s6 m3">
                <button className="btn center-align" >Search</button>
              </div>
            </div>

            <div className="row lmargin">
              <div className="input-field col s6 m3">
                <select className="browser-default" id="key" onChange={this.handleChange} >
                  <option value="" disabled selected>Choose FIELD to query</option>
                  <option value="lastname">Lastname</option>
                  <option value="firstname">Firstname</option>
                </select>
                {this.state.keyError ? (
                  <div style={{ fontSize: 12, color: "red" }}>{this.state.keyError}</div>
                ) : null}
              </div>
              <div className="col s6 m3">
                <div className="input-field">
                  <label htmlFor="search_str">Search string</label>
                  <input className="white-text" type="text" id="search_str" onChange={this.handleChange} />
                  {this.state.strError ? (
                    <div style={{ fontSize: 12, color: "red" }}>{this.state.strError}</div>
                  ) : null}
                </div>
              </div>
            </div>

            <div className="row lmargin">
              {this.state.queryMsg ? (
                <div className="white-text query_msg">{this.state.queryMsg}</div>
              ) : null}
            </div>
          </form>
          <div className="row lmargin">
            <ResultTable results = {this.state.results} update_results = {this.update_results} />
          </div>
        </div>

      </div>
    )
  }
}

export default Search