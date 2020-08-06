import React from 'react';

const Filterbar = () => {
  document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.dropdown-trigger');
    // var instances = M.Dropdown.init(elems, options);
  });
  return (
    <div className="wrapper grey darken-2">
      <div className="container">
        Slider here!
        <a class='dropdown-trigger btn' href='#' data-target='field'>Choose</a>
        <ul id='field' class='dropdown-content'>
            <li><a href="#!">Firstname</a></li>
            <li><a href="#!">Lastname</a></li>
            <li class="divider" tabindex="-1"></li>
            <li><a href="#!">City</a></li>
            <li><a href="#!">Zip</a></li>
        </ul>
        Textfield here!
      </div>
    </div>
  )
}

export default Filterbar