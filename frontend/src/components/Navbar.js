import React from 'react';

function Navbar({ 
  activeTab, 
  setActiveTab, 
  projects, 
  selectedProjectId, 
  setSelectedProjectId,
  projectsLoading,
  projectsError 
}) {
  const tabs = [
    { id: 'metrics', label: 'Metrics' },
    { id: 'productivity', label: 'Productivity' },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h1>Productivity Framework</h1>
      </div>
      <div className="navbar-center">
        <div className="navbar-tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`navbar-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      <div className="navbar-project-selector">
        <label htmlFor="project-select">Project:</label>
        {projectsLoading ? (
          <span className="loading-text">Loading...</span>
        ) : projectsError ? (
          <span className="error-text" title={projectsError}>Error</span>
        ) : (
          <select
            id="project-select"
            value={selectedProjectId}
            onChange={(e) => setSelectedProjectId(parseInt(e.target.value))}
            className="project-select"
          >
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
