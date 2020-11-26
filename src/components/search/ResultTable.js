import React, { Component } from 'react';


class ResultTable extends Component {

  state = {
    header: ['lastname', 'firstname', 'city', 'zip', 'street', 'area_code', 'phonenumber', 'appearance']
  }

  addTableRow = (result) => {
    return (
      <tr key={result._id}>
        {this.state.header.map((h) => {
          if(h === 'appearance') return (<td>{this.beautify_appearance_data(result.appearance)}</td>)
          if(h === 'street') return (<td>{result.street} {result.street_number}</td>)
          return (<td>{result[h]}</td>)
        })}
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
            {this.state.header.map((h) => {
              return (<th onClick={() => this.sortByField(h)}>{this.makeHeaderStr(h)}</th>)
            })}
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

  makeHeaderStr = (word) => {
    if(typeof word !== 'string') return word
    return (word.charAt(0).toUpperCase() + word.slice(1)).replace('_', ' ')
  }

  mergeSortByField = (list, field) => {
    if (list.length < 2) {
      return list
    }

    const left = list.splice(0, list.length / 2);
    return this.merge(this.mergeSortByField(left, field), this.mergeSortByField(list, field), field)
  }

  merge = (left, right, field) => {

    let list = [];

    while (left.length && right.length) {
      if (left[0][field] < right[0][field]) {
        list.push(left.shift());
      } else {
        list.push(right.shift());
      }
    }
    return [...list, ...left, ...right];
  }

  // TODO - REFACTOR sorting algorithm
  sortByField = (field) => {
    this.props.update_results(this.mergeSortByField(this.props.results, field));
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
