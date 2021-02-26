import React, { Component } from 'react';

class Filterbar extends Component {

  state = {
    collection: '',
    cOptions: [],
    field: '',
    search_str: '',
    use_regex: false,

    loading: false,
    queryMsg: '',

    cError: '',
    fError: '',
    sError: '',
  }

  handleChange = (e) => {
    this.setState({
      [e.target.id]: e.target.value
    });
  }

  handleSubmit = (e) => {
    e.preventDefault();
    const isValid = this.validateForm();

    if (isValid) {
      if (this.setState.search_str === '') {
        this.setState({ queryMsg: 'Search string missing.' })
        return null
      }
      let queryMsg = 'Querying phone book of ' + this.state.collection + ' for ' + this.state.field + ' = ' + this.state.search_str + '.';

      this.setState({ queryMsg, loading: true })
      // TODO double check for empty search string
      let url = 'http://localhost:5000/hm_search?collection=' + this.state.collection + '&key=' + this.state.field + '&value=' + this.state.search_str;
      if(this.state.use_regex) url += '&use_regex=true';
      fetch(url)
        .then(response => response.json())
        .then(data => {
          this.update_queryMsg(data.length);
          this.props.update_heatMapData(data);
        });
    }
  }

  validateForm = () => {
    let cError, fError, sError = '';

    if (!this.state.collection) {
      cError = 'Please choose a COLLECTION to query';
    }

    if (!this.state.field) {
      fError = 'Please choose a FIELD to query';
    }

    if (!this.state.search_str || this.state.search_str.length < 2) {
      sError = 'Search string cannot be empty and must have at least 2 letters';
    }

    if (cError || fError || sError) {
      this.setState({ cError, fError, sError });
      return false;
    }

    this.setState({ cError, fError, sError });
    return true
  }

  update_queryMsg = (d_length) => {
    let queryMsg = this.state.queryMsg + ' Found ' + d_length + ' locations.';
    this.setState({ queryMsg, loading: false });
  }

  toggle_use_regex = () => {
    this.state.use_regex = !this.state.use_regex;
  }

  createDropdown = () => {
    let options = [];
    fetch('http://localhost:5000/all_collections')
      .then(response => response.json())
      .then(data => {
        options.push(
          <option value="" disabled selected id="">Choose YEAR to query</option>);
        for (let d in data) {
          options.push(<option value={d} id={d}>{d}</option>);
        }
        this.setState({ cOptions: options });
      })
  }

  render() {
    if (!this.state.cOptions.length) this.createDropdown();

    return (
      <div className="wrapper grey darken-2">
        <div className="row filterbar">
          <form onSubmit={this.handleSubmit}>
            <div className="input-field col s6 m3">
              <select className="browser-default" id="collection" onChange={this.handleChange} >
                {this.state.cOptions}
              </select>
              {this.state.cError ? (
                <div className="err_msg">{this.state.cError}</div>
              ) : null}

            </div>
            <div className="input-field col s6 m3">
              <select className="browser-default" id="field" onChange={this.handleChange} >
                <option value="" disabled selected>Choose FIELD to query</option>
                <option value="lastname">Lastname</option>
                <option value="firstname">Firstname</option>
                <option value="street">Street</option>
              </select>
              {this.state.fError ? (
                <div className="err_msg">{this.state.fError}</div>
              ) : null}
            </div>
            <div className="col s6 m3">
              <div className="input-field">
                <label htmlFor="search_str">Search string</label>
                <input className="white-text" type="text" id="search_str" onChange={this.handleChange} />
              {this.state.sError ? (
                <div className="err_msg">{this.state.sError}</div>
              ) : null}
            </div>
            </div>
            <div className="input-field col s6 m3">
              <button className="btn center-align" >Search</button>
            </div>
            <div>
              <label>
                <input type="checkbox" className="filled-in" onChange={this.toggle_use_regex}/>
                <span>Use Regex</span>
              </label>
            </div>
          </form>
        </div>
        <div className="row lmargin">
          {this.state.queryMsg ? (
            <div className="white-text query_msg">{this.state.queryMsg}{this.state.loading ? (
              <div className="progress">
                <div className="indeterminate"></div>
              </div>
            ) : null}</div>
          ) : null}
        </div>
      </div>

    )
  }

}

export default Filterbar