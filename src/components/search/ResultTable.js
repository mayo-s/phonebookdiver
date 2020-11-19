import React, { Component } from 'react';


class ResultTable extends Component {

  addTableRow = (result) => {
    return (
      <tr key={result._id}>
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
      if (!first) data += ', ' + list[i];
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
            <th onClick={() => this.sortByField('lastname')}>Lastname</th>
            <th onClick={() => this.sortByField('firstname')}>Firstname</th>
            <th onClick={() => this.sortByField('city')}>City</th>
            <th onClick={() => this.sortByField('zip')}>ZIP</th>
            <th>Street</th>
            <th onClick={() => this.sortByField('area_code')}>Area Code</th>
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

  // TODO - REFACTOR sorting algorithm
  sortByField = (field) => {
    let sorted_results = this.props.results;
    sorted_results = this.props.results.sort((r1, r2) => (r1[field] > r2[field] ? 1 : -1));

    this.props.update_results(sorted_results);
  }

  render() {

    return (
      <div>
        {this.props.results.length ? (
          <div className="card">
            {this.createTable(this.props.results)}
          </div>
        ) : null}
      </div>
    )
  }
}

export default ResultTable
