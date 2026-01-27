import React from 'react';

function Navbar({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'metrics', label: 'Metrics' },
    { id: 'productivity', label: 'Productivity' },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h1>Productivity Framework</h1>
      </div>
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
    </nav>
  );
}

export default Navbar;
