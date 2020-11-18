import React from 'react';
import { NavLink } from 'react-router-dom';

const NavLinks = (props) => {
  return (
    <ul className="right">
      <li><NavLink to='/'>Home</NavLink></li>
      <li><NavLink to='/heatmap'>Heatmap</NavLink></li>
      <li><NavLink to='/search'>Search</NavLink></li>
      <li><NavLink to='/'>Imprint</NavLink></li>
    </ul>
  )
}

export default NavLinks