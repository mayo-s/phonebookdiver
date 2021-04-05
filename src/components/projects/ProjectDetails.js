import React from 'react'

const ProjectDetails = (props) => {
  const id = props.match.params.id;
  return (
    <div className="container section project-details">
      <div className="card z-depth-0">
        <div className="card-content">
          <span className="card-title">Project Title - {id}</span>
          <p>Lorem ipsum color sit amet...</p>
        </div>
        <div className="card-action gret lighten-4 grey-text">
          <div>Posted by Mario</div>
          <div>6th April, 2021</div>
        </div>
      </div>
    </div>
  )
}

export default ProjectDetails