import React, { useState, useEffect } from "react";
import { useSimulation } from "../hooks/useSimulation";
import { ConfigPanel } from "./ConfigPanel";
import { SpectrumChart } from "./SpectrumChart";
import { EntropyPlot } from "./EntropyPlot";
import { KruskalDiagram } from "./KruskalDiagram";
import { ResultsPanel } from "./ResultsPanel";
import { InteriorView } from "./InteriorView";

export const Dashboard: React.FC = () => {
  const [mass, setMass] = useState(2.176e-8); // Planck-tömeg alapértelmezetten
  const [norbiMode, setNorbiMode] = useState(false);

  const {
    results,
    error,
    loading,
    runSimulation,
    toggleNorbiMode,
  } = useSimulation();

  useEffect(() => {
    // Ablak cím frissítése
    document.title = `Fekete Lyuk Szimulátor — ${norbiMode ? "Norbi" : "Standard"}`;
  }, [norbiMode]);

  const handleNorbiToggle = async (enabled: boolean) => {
    setNorbiMode(enabled);
    await toggleNorbiMode(enabled);
  };

  const handleRun = () => {
    runSimulation(mass, norbiMode);
  };

  return (
    <div className="dashboard">
      <header className="header">
        <h1>Fekete Lyuk — Belső Univerzum Szimulátor</h1>
        <p className="subtitle">
          {norbiMode
            ? "Norbi-hipotézis: kvantumvisszapattanás → bébiuniverzum → Hawking-sugárzás"
            : "Standard Hawking-sugárzás modell"}
        </p>
      </header>

      <div className="main-grid">
        <aside className="sidebar">
          <ConfigPanel
            mass={mass}
            norbiMode={norbiMode}
            loading={loading}
            onMassChange={setMass}
            onNorbiToggle={handleNorbiToggle}
            onRun={handleRun}
          />
          <ResultsPanel
            results={results}
            error={error}
            norbiMode={norbiMode}
          />
        </aside>

        <main className="content">
          <div className="charts-row">
            <SpectrumChart timeline={results?.timeline ?? []} />
            <EntropyPlot timeline={results?.timeline ?? []} />
          </div>
          <div className="charts-row">
            <KruskalDiagram
              norbiMode={norbiMode}
              evaporationComplete={results?.evaporation_complete ?? false}
            />
            <InteriorView
              timeline={results?.timeline ?? []}
              norbiMode={norbiMode}
            />
          </div>
        </main>
      </div>

      <footer className="footer">
        <span>Bevy 3D: <code>cargo run --manifest-path bevy-app/Cargo.toml</code></span>
        <span>CLI: <code>python -m python.main --mass {mass.toExponential(3)} --norbi-mode {norbiMode.toString()}</code></span>
      </footer>
    </div>
  );
};
