import React, { Component } from 'react';

class Filterbar extends Component {

  state = {
    collection: '',
    field: '',
    search_string: '',
  }

  handleChange = (e) => {
    this.setState({
      [e.target.id]: e.target.value
    })
  }

  render () {
    return (
      <div className="wrapper grey darken-2">
          <div className="row">
            <div className="col s12 m4">
              Slider here!
            </div>
            <div className="col s6 m4">

            </div>
            <div className="col s6 m4">
              <div className="input-field">
                <label htmlFor="title">Search String</label>
                <input className="white-text" type="text" id="search_string" onChange={this.handleChange} />
              </div>
            </div>
          </div>
        </div>
    )
  }

}

export default Filterbar