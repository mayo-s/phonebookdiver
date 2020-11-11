import React, { Component } from 'react';

class Search extends Component {

  state = {
    cOptions: [],
    collection_start: '',
    collection_end: '',
    key: '',
    search_str: '',
  }

  handleSubmit = (e) => {
    e.preventDefault();
    // TODO double check for empty search string


    let url = 'http://localhost:5000/search?start=' + this.state.collection_start + '&end' + this.state.collection_end + '&key=' + this.state.key + '&value=' + this.state.search_str;
    fetch(url)
      .then(response => response.json())
      .then(data => this.update_resultView(data));
  }

  update_resultView = (data) => {

  }

  handleChange = (e) => {
    // TODO double check start and end year
    if(e.target.id == 'collection_start' || e.target.id == 'collection_end') {
      
      console.log('BOOOOOOOM');
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
        console.log(data);
        for (let d in data) {
          options.push(<option value={d} >{d}</option>);
        }
        this.setState({ cOptions: options });
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
                </div>
                <div className="input-field col s6 m3">
                  <select className="browser-default" id="collection_end" onChange={this.handleChange} >
                    <option value="" disabled selected>Choose End YEAR to query</option>
                    {this.state.cOptions}
                  </select>
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
                </div>
                <div className="col s6 m3">
                  <div className="input-field">
                    <label htmlFor="search_str">Search string</label>
                    <input className="white-text" type="text" id="search_str" onChange={this.handleChange} />
                  </div>
                </div>
              </div>

            </div>
          </form>
        </div>
      </div>
    )
  }
}

export default Search