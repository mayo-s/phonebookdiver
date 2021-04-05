import React, { Component } from 'react';
import ResultTable from './ResultTable';

class Search extends Component {

  state = {
    cOptions: [],
    collection_start: '',
    collection_end: '',
    frst_key: '',
    frst_value: '',
    scnd_parameter: false,
    scnd_key: '',
    scnd_value: '',
    thrd_parameter: false,
    thrd_key: '',
    thrd_value: '',

    startError: '',
    frstKeyError: '',
    frstValueError: '',
    scndKeyError: '',
    scndValueError: '',
    thrdKeyError: '',
    thrdValueError: '',

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

      let queryMsg = 'Querying the phone book years from ' + this.state.collection_start + ' to ' + this.state.collection_end + ' for ' + this.state.frst_key + ' = ' + this.state.frst_value;
      if (this.state.scnd_key && this.state.scnd_value) queryMsg += ' AND ' + this.state.scnd_key + ' = ' + this.state.scnd_value;
      if (this.state.thrd_key && this.state.thrd_value) queryMsg += ' AND ' + this.state.thrd_key + ' = ' + this.state.thrd_value;
      queryMsg += '.';
      this.setState({ queryMsg, loading: true })

      let url = 'http://localhost:5000/search?start=' + this.state.collection_start + '&end=' + this.state.collection_end + '&frst_key=' + this.state.frst_key + '&frst_value=' + this.state.frst_value;
      if (this.state.scnd_value !== '') url += '&scnd_key=' + this.state.scnd_key + '&scnd_value=' + this.state.scnd_value;
      if (this.state.thrd_value !== '') url += '&thrd_key=' + this.state.thrd_key + '&thrd_value=' + this.state.thrd_value;
      fetch(url)
        .then(response => response.json())
        .then(data => this.update_resultView(data));
    }
  }

  validateForm = () => {
    let frstKeyError, frstValueError, startError, scndKeyError, scndValueError, thrdKeyError, thrdValueError = '';

    if (parseInt(this.state.collection_start.substr(0, 4)) > parseInt(this.state.collection_end.substr(0, 4))) {
      startError = 'First YEAR value must be lower than second.';
    }

    if (!this.state.frst_key) {
      frstKeyError = 'Please choose a FIELD to query';
    }

    if (!this.state.frst_value || this.state.frst_value.length < 2) {
      frstValueError = 'Search string cannot be empty and must have at least 2 letters';
    }

    if (!this.state.scnd_key) {
      scndKeyError = 'Please choose a FIELD to query';
    }

    if (!this.state.scnd_value || this.state.scnd_value.length < 2) {
      scndValueError = 'Empty search string will not be considered';
    }

    if (!this.state.thrd_key) {
      thrdKeyError = 'Please choose a FIELD to query';
    }

    if (!this.state.thrd_value || this.state.thrd_value.length < 2) {
      thrdValueError = 'Empty search string will not be considered';
    }

    if (startError || frstKeyError || frstValueError) {
      this.setState({
        startError,
        frstKeyError: frstKeyError,
        frstValueError: frstValueError,
        scndKeyError: scndKeyError,
        scndValueError: scndValueError,
        thrdKeyError: thrdKeyError,
        thrdValueError: thrdValueError
      });
      return false;
    }

    this.setState({
      startError,
      keyError: frstKeyError,
      strError: frstValueError,
      scndKeyError: scndKeyError,
      scndStrError: scndValueError,
      thrdKeyError: thrdKeyError,
      thrdValueError: thrdValueError
    });
    return true
  }

  update_resultView = (data) => {
    let queryMsg = this.state.queryMsg + ' Found ' + data.length + ' entries.';
    this.setState({ queryMsg, results: data, loading: false });
  }

  update_results = (results) => {
    this.setState({ results })
  }

  scndParameter = () => {
    let value = !this.state.scnd_parameter;
    this.setState({ scnd_parameter: value });
    if (value === false) {
      this.setState({
        scnd_key: '',
        scnd_value: '',
      })
    }
  }

  thrdParameter = () => {
    let value = !this.state.thrd_parameter;
    this.setState({ thrd_parameter: value });
    if (value === false) {
      this.setState({
        thrd_key: '',
        thrd_value: '',
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
          // TODO Check also for quarter
          if (parseInt(first.substr(0, 4)) > parseInt(d.substr(0, 4))) first = d;
          else if (parseInt(first.substr(0, 4)) === parseInt(d.substr(0, 4)) && parseInt(first.substr(first.length - 1) ) > parseInt(d.substr(d.length - 1) )) first = d;
          if (parseInt(last.substr(0, 4)) < parseInt(d.substr(0, 4))) last = d;
          else if (parseInt(last.substr(0, 4)) === parseInt(d.substr(0, 4)) && parseInt(first.substr(first.length - 1) ) < parseInt(d.substr(d.length - 1) )) last = d;
        }
        // by default range over all available collections
        this.setState({ cOptions: options, collection_start: first, collection_end: last });
      })
  }

  details_overlay = (id, data) => {
    data['c_id'] = id;
    let info = this.parse_details(data);

    let overlay = (
      <div className="overlay_blur" onClick={() => this.setState({ overlay: '' })}>
        <div className="card overlay_content">
          <h5>Record Details {data['c_id'].substr(0, 7)}</h5>
          {info.map((i) => {
            return (<p><b>{i}:</b> {data[i]}</p>)
          })}
        </div>
      </div>)
    this.setState({ overlay });
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
                <select className="browser-default" id="frst_key" defaultValue={""} onChange={this.handleChange} >
                  <option value="" disabled>Choose FIELD to query</option>
                  <option value="lastname">Lastname</option>
                  <option value="firstname">Firstname</option>
                </select>
                {this.state.frstKeyError ? (
                  <div className="err_msg">{this.state.frstKeyError}</div>
                ) : null}
              </div>
              <div className="col s6 m3">
                <div className="input-field">
                  <label htmlFor="search_str">Search string</label>
                  <input className="white-text" type="text" id="frst_value" onChange={this.handleChange} />
                  {this.state.frstValueError ? (
                    <div className="err_msg">{this.state.frstValueError}</div>
                  ) : null}
                </div>
              </div>
              {!this.state.scnd_parameter ? (
                <div>
                  <a className="btn-floating btn-small center-align" onClick={this.scndParameter}><i className="material-icons">add</i></a>
                </div>) : null}
            </div>

            {this.state.scnd_parameter ? (
              <div className="row lmargin">
                <div className="input-field col s6 m3">
                  <select className="browser-default" id="scnd_key" defaultValue={""} onChange={this.handleChange} >
                    <option value="" disabled>Choose second FIELD to query</option>
                    {this.state.frst_key === 'lastname' ? (<option value="firstname">Firstname</option>) : (<option value="lastname">Lastname</option>)}
                    {this.state.thrd_key === 'zip' ? (null) : (<option value="zip">ZIP</option>)}
                    {this.state.thrd_key === 'city' ? (null) : (<option value="city">City</option>)}
                    {this.state.thrd_key === 'area_code' ? (null) : (<option value="area_code">Area Code</option>)}
                  </select>
                  {this.state.scndKeyError ? (
                    <div className="err_msg">{this.state.scndKeyError}</div>
                  ) : null}
                </div>
                <div className="col s6 m3">
                  <div className="input-field">
                    <label htmlFor="search_str">2nd search string</label>
                    <input className="white-text" type="text" id="scnd_value" onChange={this.handleChange} />
                    {this.state.scndValueError ? (
                      <div className="err_msg">{this.state.scndValueError}</div>
                    ) : null}
                  </div>
                </div>
                <div>
                  {this.state.scnd_parameter ? (
                    <a className="btn-floating btn-small center-align" onClick={this.scndParameter}><i className="material-icons">remove</i></a>
                  ) : null}
                  {!this.state.thrd_parameter ? (
                    <a className="btn-floating btn-small center-align" onClick={this.thrdParameter}><i className="material-icons">add</i></a>
                  ) : null}
                </div>
              </div>
            ) : null}

            {this.state.thrd_parameter ? (
              <div className="row lmargin">
                <div className="input-field col s6 m3">
                  <select className="browser-default" id="thrd_key" defaultValue={""} onChange={this.handleChange} >
                    <option value="" disabled>Choose second FIELD to query</option>
                    {this.state.frst_key === 'lastname' ? (<option value="firstname">Firstname</option>) : (<option value="lastname">Lastname</option>)}
                    {this.state.scnd_key === 'zip' ? (null) : (<option value="zip">ZIP</option>)}
                    {this.state.scnd_key === 'city' ? (null) : (<option value="city">City</option>)}
                    {this.state.scnd_key === 'area_code' ? (null) : (<option value="area_code">Area Code</option>)}
                  </select>
                  {this.state.thrdKeyError ? (
                    <div className="err_msg">{this.state.thrdKeyError}</div>
                  ) : null}
                </div>
                <div className="col s6 m3">
                  <div className="input-field">
                    <label htmlFor="search_str">3rd search string</label>
                    <input className="white-text" type="text" id="thrd_value" onChange={this.handleChange} />
                    {this.state.thrdValueError ? (
                      <div className="err_msg">{this.state.thrdValueError}</div>
                    ) : null}
                  </div>
                </div>
                {this.state.thrd_parameter ? (
                  <div>
                    <a className="btn-floating btn-small center-align" onClick={this.thrdParameter}><i className="material-icons">remove</i></a>
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
            <ResultTable results={this.state.results} update_results={this.update_results} details_overlay={this.details_overlay} />
          </div>
        </div>

      </div>
    )
  }
}

export default Search