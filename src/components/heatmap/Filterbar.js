import React, { Component } from 'react';

class Filterbar extends Component {

  state = {
    collection: '',
    cOptions: [],
    field: '',
    search_str: '',

    loading: false,
    queryMsg: '',
  }

  handleChange = (e) => {
    this.setState({
      [e.target.id]: e.target.value
    });
  }

  handleSubmit = (e) => {
    e.preventDefault();
    if(this.setState.search_str === '') {
      this.setState({queryMsg: 'Search string missing.'})
      return null
    }
    let queryMsg = 'Querying phone book of ' + this.state.collection + ' for ' + this.state.field + ' = ' + this.state.search_str + '.';

    this.setState({ queryMsg, loading: true })
    // TODO double check for empty search string
    let url = 'http://localhost:5000/hm_search?collection=' + this.state.collection + '&key=' + this.state.field + '&value=' + this.state.search_str;
    fetch(url)
      .then(response => response.json())
      .then(data => {
        this.update_queryMsg(data.length);
        this.props.update_heatMapData(data);
      });
  }

  update_queryMsg = (d_length) => {
    let queryMsg = this.state.queryMsg + ' Found ' + d_length + ' locations.';
    this.setState({ queryMsg, loading: false });
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

            </div>
            <div className="input-field col s6 m3">
              <select className="browser-default" id="field" onChange={this.handleChange} >
                <option value="" disabled selected>Choose FIELD to query</option>
                <option value="lastname">Lastname</option>
                <option value="firstname">Firstname</option>
                <option value="street">Street</option>
              </select>
            </div>
            <div className="col s6 m3">
              <div className="input-field">
                <label htmlFor="search_str">Search string</label>
                <input className="white-text" type="text" id="search_str" onChange={this.handleChange} />
              </div>
            </div>
            <div className="input-field col s6 m3">
              <button className="btn center-align" >Search</button>
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