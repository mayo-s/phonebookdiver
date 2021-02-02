import React, { Component } from 'react';
import ResultTable from './ResultTable';

class Search extends Component {

  state = {
    cOptions: [],
    collection_start: '',
    collection_end: '',
    pri_key: '',
    pri_search_str: '',
    sec_field: false,
    sec_key: '',
    sec_search_str:'',

    startError: '',
    keyError: '',
    strError: '',
    secKeyError: '',
    secStrError: '',

    loading: false,
    queryMsg: '',
    results: [],

    overlay: '',
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
      
      let queryMsg = 'Querying the years from ' + this.state.collection_start.substr(0, 4) + ' to ' + this.state.collection_end.substr(0, 4) + ' for ' + this.state.pri_key + ' = ' + this.state.pri_search_str;
      if(this.state.sec_field && this.state.secKeyError && this.state.secStrError) queryMsg += ' and ' + this.state.sec_key + ' = ' + this.state.sec_search_str + '.';
      else queryMsg += '.';
      this.setState({ queryMsg, loading: true })

      let url = 'http://localhost:5000/search?start=' + this.state.collection_start + '&end=' + this.state.collection_end + '&key=' + this.state.pri_key + '&value=' + this.state.pri_search_str;
      if(this.state.sec_field) url += '&seckey=' + this.state.sec_key + '&secvalue=' + this.state.sec_search_str;
      console.log(url);
      fetch(url)
        .then(response => response.json())
        .then(data => this.update_resultView(data));
    }
  }

  validateForm = () => {
    let keyError, strError, startError, secKeyError, secStrError = '';

    if (parseInt(this.state.collection_start.substr(0, 4)) > parseInt(this.state.collection_end.substr(0, 4))) {
      startError = 'First YEAR value must be lower than second.';
    }

    if (!this.state.pri_key) {
      keyError = 'Please choose a FIELD to query';
    }

    if (!this.state.pri_search_str || this.state.pri_search_str.length < 2) {
      strError = 'Search string cannot be empty and must have at least 2 letters';
    }

    if (!this.state.sec_key) {
      secKeyError = 'Please choose a FIELD to query';
    }

    if (!this.state.sec_search_str || this.state.sec_search_str.length < 2) {
      secStrError = 'Empty second search string will not be considered';
    }

    if (startError || keyError || strError) {
      this.setState({ startError, keyError, strError, secKeyError, secStrError });
      return false;
    }

    this.setState({ startError, keyError, strError, secKeyError, secStrError });
    return true
  }

  update_resultView = (data) => {
    let queryMsg = this.state.queryMsg + ' Found ' + data.length + ' entries.';
    this.setState({ queryMsg, results: data, loading: false });
  }

  update_results = (results) => {
    this.setState({results})
  }

  add_sec_field = () => {
    let value = !this.state.sec_field;
    this.setState({sec_field: value});
    if(value === false) {
      this.setState({
        sec_key: '',
        sec_search_str: '',
      })
    }
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

  details_overlay = (id, data) => {
    data['c_id'] = id;
    let info = this.parse_details(data);

    let overlay = (      
      <div className="overlay_blur" onClick={() => this.setState({overlay: ''})}>
        <div className="card overlay_content">
          <h5>Record Details {data['c_id'].substr(0,7)}</h5>
          {info.map((i) => {
            return (<p><b>{i}:</b> {data[i]}</p>)
          })}
        </div>
      </div>)
    this.setState({overlay});
  }

  parse_details = (data) => {
    let info = [];
    Object.keys(data).forEach((d) => {
      info.push(d);
    });
    return info
  }

  render() {
    if (!this.state.cOptions.length) this.getCollections();

    return (
      <div className='dashboard'>
        {this.state.overlay ? (this.state.overlay) : null}


        <div className="wrapper grey darken-2">
          <form onSubmit={this.handleSubmit}>

            <div className="row lmargin">
              <div className="input-field col s6 m3">
                <select className="browser-default" id="collection_start" defaultValue={""} onChange={this.handleChange} >
                  <option value="" disabled key="start_year">Choose Start YEAR to query</option>
                  {this.state.cOptions}
                </select>
                {this.state.startError ? (
                  <div className="err_msg">{this.state.startError}</div>
                ) : null}
              </div>

              <div className="input-field col s6 m3">
                <select className="browser-default" id="collection_end" defaultValue={""} onChange={this.handleChange} >
                  <option value="" disabled key="end_year">Choose End YEAR to query</option>
                  {this.state.cOptions}
                </select>
              </div>
              <div className="input-field col s6 m3">
                <button className="btn center-align" >Search</button>
              </div>
            </div>

            <div className="row lmargin">
              <div className="input-field col s6 m3">
                <select className="browser-default" id="pri_key" defaultValue={""} onChange={this.handleChange} >
                  <option value="" disabled>Choose FIELD to query</option>
                  <option value="lastname">Lastname</option>
                  <option value="firstname">Firstname</option>
                </select>
                {this.state.keyError ? (
                  <div className="err_msg">{this.state.keyError}</div>
                ) : null}
              </div>
              <div className="col s6 m3">
                <div className="input-field">
                  <label htmlFor="search_str">Search string</label>
                  <input className="white-text" type="text" id="pri_search_str" onChange={this.handleChange} />
                  {this.state.strError ? (
                    <div className="err_msg">{this.state.strError}</div>
                  ) : null}
                </div>
              </div>
              {!this.state.sec_field ? (
              <div>
                <a className="btn-floating btn-small center-align" onClick={this.add_sec_field}><i className="material-icons">add</i></a>
              </div>) : null}
            </div>

            {this.state.sec_field ? (
              <div className="row lmargin">
                <div className="input-field col s6 m3">
                  <select className="browser-default" id="sec_key" defaultValue={""} onChange={this.handleChange} >
                    <option value="" disabled>Choose second FIELD to query</option>
                    {this.state.pri_key === 'lastname' ? (<option value="firstname">Firstname</option>) : (<option value="lastname">Lastname</option>)}
                    <option value="zip">ZIP</option>
                    <option value="city">City</option>
                    <option value="area_code">Area Code</option>
                  </select>
                  {this.state.secKeyError ? (
                    <div className="err_msg">{this.state.secKeyError}</div>
                  ) : null}
                </div>
                <div className="col s6 m3">
                  <div className="input-field">
                    <label htmlFor="search_str">2nd search string</label>
                    <input className="white-text" type="text" id="sec_search_str" onChange={this.handleChange} />
                    {this.state.secStrError ? (
                      <div className="err_msg">{this.state.secStrError}</div>
                    ) : null}
                  </div>
                </div>
                {this.state.sec_field ? (
                <div>
                  <a className="btn-floating btn-small center-align" onClick={this.add_sec_field}><i className="material-icons">remove</i></a>
                </div>) : null}
              </div>
            ) : null}

            <div className="row lmargin">
              {this.state.queryMsg ? (
                <div className="white-text query_msg">{this.state.queryMsg}{this.state.loading ? (
                  <div className="progress">
                    <div className="indeterminate"></div>
                  </div>
                ) : null}</div>
              ) : null}
            </div>
          </form>
          <div className="row lmargin">
            <ResultTable results = {this.state.results} update_results = {this.update_results} details_overlay = {this.details_overlay}/>
          </div>
        </div>

      </div>
    )
  }
}

export default Search