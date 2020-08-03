import React, { Component } from 'react';
import ProjectList from './ProjectList';

class Dashboard extends Component {
  render() {
    return(
    <div className="dashboard container">
      <div className="row">
        <div className="col s12 m6">
          <ProjectList />
        </div>
        <div className="col s12 m5 offset-m1">
            some notifications<br />
            some information<br />
            some updates
        </div>
      </div>
    </div>
    )
  }
}

export default Dashboard