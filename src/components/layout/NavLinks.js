import React from 'react';
import { NavLink } from 'react-router-dom';

const NavLinks = (props) => {
  return (
    <ul className="right">
      <li><NavLink to='/'>Home</NavLink></li>
      <li><NavLink to='/'>Heatmap</NavLink></li>
      <li><NavLink to='/'>Imprint</NavLink></li>

    </ul>
  )
}

export default NavLinks