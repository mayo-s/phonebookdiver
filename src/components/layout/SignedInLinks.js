import React from 'react'
import { NavLink } from 'react-router-dom';

const SignedInLinks = () => {
  return (
    <div>
      <ul className="right">
        <li><NavLink to='/'>Home</NavLink></li>
        <li><NavLink to='/heatmap'>Heatmap</NavLink></li>
        <li><NavLink to='/search'>Search</NavLink></li>
        {/* <li><NavLink to='/createProject'>Create Card</NavLink></li> */}
        <li><NavLink to='/'>Imprint</NavLink></li>
        <li><NavLink to='/'>Logout</NavLink></li>

      </ul>
    </div>
  )
}

export default SignedInLinks