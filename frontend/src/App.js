import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import MetricsPage from './components/MetricsPage';
import ProductivityPage from './components/ProductivityPage';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('metrics');
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(1);
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [projectsError, setProjectsError] = useState(null);

  // Fetch available projects on component mount
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/projects`);
        if (!response.ok) {
          throw new Error('Failed to fetch projects');
        }
        const data = await response.json();
        setProjects(data);
        // Default to first project (should be Project 1)
        if (data.length > 0) {
          setSelectedProjectId(data[0].id);
        }
        setProjectsLoading(false);
      } catch (err) {
        setProjectsError('Failed to load projects. Make sure the backend is running.');
        console.error('Error fetching projects:', err);
        setProjectsLoading(false);
      }
    };

    fetchProjects();
  }, []);

  const renderPage = () => {
    switch (activeTab) {
      case 'metrics':
        return <MetricsPage projectId={selectedProjectId} />;
      case 'productivity':
        return <ProductivityPage projectId={selectedProjectId} />;
      default:
        return <MetricsPage projectId={selectedProjectId} />;
    }
  };

  return (
    <div className="app">
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab}
        projects={projects}
        selectedProjectId={selectedProjectId}
        setSelectedProjectId={setSelectedProjectId}
        projectsLoading={projectsLoading}
        projectsError={projectsError}
      />
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
