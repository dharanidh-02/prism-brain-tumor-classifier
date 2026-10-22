import React from 'react';
import {
  ScanLine,
  History,
  ChartNoAxesCombined,
  BrainCircuit,
  Compass
} from 'lucide-react';
import NavigationTile from './NavigationTile';

export default function NavigationPanel() {
  return (
    <section className="nav-panel" aria-labelledby="navigate-prism-heading">
      <div className="nav-panel-title" id="navigate-prism-heading">
        <Compass size={22} style={{ color: 'var(--prism-indigo)' }} />
        <span>Navigate PRISM</span>
      </div>

      <div className="tiles-grid">
        {/* Tile 1: Analyze MRI */}
        <NavigationTile
          title="Analyze MRI"
          description="Upload an MRI image and run AI classification."
          to="/analyze"
          icon={ScanLine}
          iconBg="var(--prism-indigo-subtle)"
          iconColor="var(--prism-indigo)"
        />

        {/* Tile 2: Prediction History */}
        <NavigationTile
          title="Prediction History"
          description="Review previous analyses and saved results."
          to="/history"
          icon={History}
          iconBg="var(--prism-teal-subtle)"
          iconColor="var(--prism-teal)"
        />

        {/* Tile 3: Analytics & Reports */}
        <NavigationTile
          title="Analytics & Reports"
          description="Explore prediction trends and model metrics."
          to="/analytics"
          icon={ChartNoAxesCombined}
          iconBg="var(--prism-amber-subtle)"
          iconColor="var(--prism-amber)"
        />

        {/* Tile 4: Model Laboratory */}
        <NavigationTile
          title="Model Laboratory"
          description="Inspect trained models and their status."
          to="/models"
          icon={BrainCircuit}
          iconBg="var(--prism-emerald-subtle)"
          iconColor="var(--prism-emerald)"
        />
      </div>
    </section>
  );
}
