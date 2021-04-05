import React from 'react';

const Imprint = () => {

  // const imprintContent = [

  //   { headline: 'SPECIAL CREDITS', content: 'Prof. Weber-Wulff of the University of Applied Sciences Berlin and Erdgeist.' },
  //   { headline: 'LICENSE', content: 'CC-BY 4.0' },
  //   { headline: 'LICENSE', content: 'CC-BY 4.0' },
  // ]

  // const createImprintBlock = (block) => {
  //   return (
  //     <div className="card z-depth-0 section">
  //       <div className="card-content grey-text text-darken-3">
  //         <span className="card-title">SPECIAL CREDITS</span>
  //         <span className="card-content">Prof. Weber-Wulff of the University of Applied Sciences Berlin and Erdgeist.</span>
  //       </div>
  //     </div>);
  // }

  return (
    <div className="dashboard container">
      <div className="row">
        <div className="col s12 m6">
          <div className="card z-depth-0 section">
            <div className="card-content grey-text text-darken-3">
              <span className="card-title">SPECIAL CREDITS</span>
              <span className="card-content">Special credits to Prof. Weber-Wulff from the University of Applied Sciences Berlin and Erdgeist for the project support and the provision of the telephone book data.</span>
            </div>
          </div>
          <div className="card z-depth-0 section">
            <div className="card-content grey-text text-darken-3">
              <span className="card-title">PROJECT IMPLEMENTATION</span>
              <span className="card-content">Project implementation by Mario Schütz (Berlin University of Applied Sciences) in the context of an independent coursework and subsequent master thesis.</span>
            </div>
          </div>
          <div className="card z-depth-0 section">
            <div className="card-content grey-text text-darken-3">
              <span className="card-title">DISCLAIMER</span>
              <span className="card-content">The provided tools are designed to query 25 years of telephone book data.
              The telephone book data is NOT PROVIDED with this project.
              The use of the provided tools is at your own responsibility.
In no way can the author be held responsible for incorrect information or damages incurred.</span>
            </div>
          </div>
          <div className="card z-depth-0 section">
            <div className="card-content grey-text text-darken-3">
              <span className="card-title">LICENSE</span>
              <span className="card-content">Unless otherwise stated, this project is licensed under <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank">CC-BY 4.0.</a></span>
            </div>
          </div>
        </div>
        <div className="col s12 m5 offset-m1">
          {/* <Notifications /> */}
        </div>
      </div>
    </div>
  )
}

export default Imprint
