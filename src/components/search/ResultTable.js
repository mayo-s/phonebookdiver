import React, { Component } from 'react';


class ResultTable extends Component {

  addTableRow = (result) => {
  
    return (
      <tr>
        <td>{result.lastname}</td>
        <td>{result.firstname}</td>
        <td>{result.city}</td>
        <td>{result.zip}</td>
        <td>{result.street} {result.street_number}</td>
        <td>{result.area_code}</td>
        <td>{result.phonenumber}</td>
        <td>{this.beautify_appearance_data(result.appearance)}</td>
      </tr>)
  }
  
  beautify_appearance_data = (list) => {
    let data = '';
    let first = true;
    for (let i in list) {
      if(!first) data += ', ' + list[i];
      else {
        data += list[i];
        first = false;
      }
    }
    return data
  }
  
  createTable = (results) => {
    return (
      <table className="striped highlight ">
        <thead>
          <tr>
            <th>Lastname</th>
            <th>Firstname</th>
            <th>City</th>
            <th>ZIP</th>
            <th>Street</th>
            <th>Area Code</th>
            <th>Phone Number</th>
            <th>Appearance</th>
          </tr>
        </thead>
        <tbody>
          {results.map((result, index) => {
            return this.addTableRow(result)
          })}
        </tbody>
      </table>
    )
  }

  render() {
    return(
      <div className="card material-table">
        {this.createTable(this.props.results)}
      </div>
    )
  }
}
  
export default ResultTable
