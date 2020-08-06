import React from 'react';

const Filterbar = () => {
  return (
    <div className="wrapper grey darken-2">
      <div className="container">
        Slider here!
        <a className='dropdown-trigger btn' href='#' data-target='field'>Choose</a>
        <ul id='field' className='dropdown-content'>
            <li><a href="#!">Firstname</a></li>
            <li><a href="#!">Lastname</a></li>
            <li className="divider" tabIndex="-1"></li>
            <li><a href="#!">City</a></li>
            <li><a href="#!">Zip</a></li>
        </ul>
        Textfield here!
      </div>
    </div>
  )
}

export default Filterbar