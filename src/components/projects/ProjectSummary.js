import React from 'react';

const ProjectSummary = ({project}) => {
  return (
    <div className="card z-depth-0 project-summary">
      <div className="card-content grey-text text-darken-3">
        <span className="card-title">{project.title}</span>
        <span className="card-content">{project.content}</span>
        <p className="grey-text created-by">Posted by {project.author} -  {project.timestamp}</p>
      </div>
    </div>
  )
}

export default ProjectSummary