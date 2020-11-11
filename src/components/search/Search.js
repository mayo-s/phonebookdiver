import React, { Component } from 'react';

class Search extends Component {

  state = {
    cOptions: [],
    collection_start: '',
    collection_end: '',
    key: '',
    search_str: '',

    startError: '',
    endError: '',
    keyError: '',
    strError: '',

    queryMsg: '',
  }

  handleSubmit = (e) => {
    e.preventDefault();
    const isValid = this.validateForm();

    if(isValid) {
      let queryMsg = 'Querying the years from ' + this.state.collection_start.substr(0, 4) + ' to ' + this.state.collection_end.substr(0, 4) + ' for ' + this.state.key + ' = ' + this.state.search_str;
      this.setState({queryMsg})
      let url = 'http://localhost:5000/search?start=' + this.state.collection_start + '&end=' + this.state.collection_end + '&key=' + this.state.key + '&value=' + this.state.search_str;
      fetch(url)
        .then(response => response.json())
        .then(data => this.update_resultView(data));
    }
  }

  validateForm = () => {
    let keyError, strError = '';

    if (!this.state.collection_start) this.setState({collection_start: this.state.first});
    if (!this.state.collection_end) this.setState({collection_end: this.state.last});
    if(!this.state.key) {
      keyError = 'Please choose a FIELD to query';
    }
    if(!this.state.search_str || this.state.search_str.length < 2) {
      strError = 'Search string cannot be empty and must have at least 2 letters';
    }

    if(keyError || strError) {
      this.setState({keyError, strError});
      return false;
    }

    this.setState({keyError, strError});
    return true
  }

  update_resultView = (data) => {

  }

  handleChange = (e) => {
    // TODO double check start and end year
    if(e.target.id === 'collection_start' || e.target.id === 'collection_end') {
      // doublecheck_range(e.target)
    }
    this.setState({
      [e.target.id]: e.target.value
    });
    console.log(this.state);
  }

  getCollections = () => {
    let options = [];
    fetch('http://localhost:5000/all_collections')
      .then(response => response.json())
      .then(data => {
        let first = '9999_Q0';
        let last = '0000_Q0';
        for (let d in data) {
          options.push(<option value={d} >{d}</option>);
          if(parseInt(first.substr(0, 4)) > parseInt(d.substr(0, 4))) first = d;
          if(parseInt(last.substr(0, 4)) < parseInt(d.substr(0, 4))) last = d;
        }
        this.setState({ cOptions: options, collection_start: first, collection_end: last });
      })
  }

  render() {
    if (!this.state.cOptions.length) this.getCollections();

    return (
      <div className='dashboard'>

        <div className="wrapper grey darken-2">

          <form onSubmit={this.handleSubmit}>
            <div className="col">

              <div className="row">
                <div className="input-field col s6 m3">
                  <select className="browser-default" id="collection_start" onChange={this.handleChange} >
                    <option value="" disabled selected>Choose Start YEAR to query</option>
                    {this.state.cOptions}
                  </select>
                  {this.state.startError ? (
                    <div style={{fontSize: 12, color: "red"}}>{this.state.startError}</div>
                  ) : null}
                </div>

                <div className="input-field col s6 m3">
                  <select className="browser-default" id="collection_end" onChange={this.handleChange} >
                    <option value="" disabled selected>Choose End YEAR to query</option>
                    {this.state.cOptions}
                  </select>
                  {this.state.endError ? (
                    <div style={{fontSize: 12, color: "red"}}>{this.state.endError}</div>
                  ) : null}
                </div>
                <div className="input-field col s6 m3">
                  <button className="btn center-align" >Search</button>
                </div>
              </div>

              <div className="row">
                <div className="input-field col s6 m3">
                  <select className="browser-default" id="key" onChange={this.handleChange} >
                    <option value="" disabled selected>Choose FIELD to query</option>
                    <option value="lastname">Lastname</option>
                    <option value="firstname">Firstname</option>
                    {/* <option value="street">Street</option> */}
                  </select>
                  {this.state.keyError ? (
                    <div style={{fontSize: 12, color: "red"}}>{this.state.keyError}</div>
                  ) : null}
                </div>
                <div className="col s6 m3">
                  <div className="input-field">
                    <label htmlFor="search_str">Search string</label>
                    <input className="white-text" type="text" id="search_str" onChange={this.handleChange} />
                    {this.state.strError ? (
                      <div style={{fontSize: 12, color: "red"}}>{this.state.strError}</div>
                    ) : null}
                  </div>
                </div>
              </div>

            </div>
            <div className="row">
              {this.state.queryMsg ? (
                <div>{this.state.queryMsg}</div>
              ) : null}
            </div>
          </form>
        </div>
      </div>
    )
  }
}

export default Search