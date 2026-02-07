import React, { useState, useCallback } from 'react';
import MetricsAnalysisPanel from './MetricsAnalysisPanel';

function MetricsPage({ projectId }) {
  // Track panels by unique IDs
  const [panels, setPanels] = useState([{ id: 1 }]);
  const [nextPanelId, setNextPanelId] = useState(2);

  const handleAddPanel = useCallback(() => {
    setPanels(prev => [...prev, { id: nextPanelId }]);
    setNextPanelId(prev => prev + 1);
  }, [nextPanelId]);

  const handleRemovePanel = useCallback((panelId) => {
    setPanels(prev => prev.filter(p => p.id !== panelId));
  }, []);

  return (
    <div className="metrics-page">
      <div className="metrics-page-header">
        <h2>Metrics Analysis</h2>
        <button 
          className="add-panel-btn"
          onClick={handleAddPanel}
          title="Add comparison panel"
        >
          + Add Comparison View
        </button>
      </div>

      <div className={`metrics-panels-container ${panels.length > 1 ? 'side-by-side' : ''}`}>
        {panels.map((panel, index) => (
          <MetricsAnalysisPanel
            key={panel.id}
            panelId={panel.id}
            projectId={projectId}
            title={panels.length > 1 ? `Analysis ${index + 1}` : 'Analysis'}
            onRemove={handleRemovePanel}
            canRemove={panels.length > 1}
          />
        ))}
      </div>
    </div>
  );
}

export default MetricsPage;
