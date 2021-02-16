import React, { Component } from 'react';


class ResultTable extends Component {

  state = {
    header: ['lastname', 'firstname', 'city', 'zip', 'street', 'area_code', 'phonenumber', 'edition'],
    ignore_header: ['_id', 'flags', 'street_number', 'street_index_hnr', 'street_index'],
  }

  addTableRow = (header, result) => {
    return (
      <tr key={result._id}>
        {header.map((h) => {
          if(this.state.ignore_header.includes(h)) return null

          if(h === 'edition') return (<td>
            {result.edition.map((a) => {
              return (<a onClick={() => this.fetch_details(a)}>{a.substr(0,7)} </a>)
            })}
          </td>)

          if(h === 'street') return (<td>{result.street} {result.street_number}</td>)
          return (<td>{result[h]}</td>)
        })}
      </tr>)
  }

  fetch_details = (resp_id) => {
    let url = 'http://localhost:3000/fetch_details?id=' + resp_id;
    fetch(url)
        .then(response => response.json())
        .then(data => this.props.details_overlay(resp_id, data));
  }

  createTable = (results) => {
    let header = this.fetchTableHeader(results);
    return (
      <table className="striped">
        <thead>
          <tr>
            {header.map((h) => {
              return (<th onClick={() => this.sortByField(h)}>{this.makeHeaderStr(h)}</th>)
            })}
          </tr>
        </thead>
        <tbody>
          {results.map((result, index) => {
            return this.addTableRow(header, result)
          })}
        </tbody>
      </table>
    )
  }

  fetchTableHeader = (results) => {
    let header = [...this.state.header];
    results.forEach((result) => {
      Object.keys(result).forEach((r) => {
        if(!this.state.ignore_header.includes(r) && !header.includes(r)) {
          header.push(r);
        }
      });
    });
    return header
  }

  makeHeaderStr = (header_str) => {
    if(typeof header_str !== 'string') return header_str
    return (header_str.charAt(0).toUpperCase() + header_str.slice(1)).replace('_', ' ')
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
