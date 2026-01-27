import React, { useState } from 'react';
import Navbar from './components/Navbar';
import MetricsPage from './components/MetricsPage';
import ProductivityPage from './components/ProductivityPage';

function App() {
  const [activeTab, setActiveTab] = useState('metrics');

  const renderPage = () => {
    switch (activeTab) {
      case 'metrics':
        return <MetricsPage />;
      case 'productivity':
        return <ProductivityPage />;
      default:
        return <MetricsPage />;
    }
  };

  return (
    <div className="app">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
