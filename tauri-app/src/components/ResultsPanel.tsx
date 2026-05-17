import React from "react";
import type { SimulationResults } from "../hooks/useSimulation";

interface ResultsPanelProps {
  results: SimulationResults | null;
  error: string | null;
  norbiMode: boolean;
}

export const ResultsPanel: React.FC<ResultsPanelProps> = ({ results, error, norbiMode }) => {
  if (error) {
    return (
      <div className="results-panel error">
        <h4>Hiba</h4>
        <pre>{error}</pre>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="results-panel empty">
        <p>Futtasd a szimulációt az eredmények megjelenítéséhez.</p>
      </div>
    );
  }

  const first = results.timeline[0];
  const last = results.timeline[results.timeline.length - 1];
  const massDelta = first && last ? ((first.mass - last.mass) / first.mass) * 100 : 0;

  return (
    <div className="results-panel">
      <h4>Szimuláció eredményei</h4>

      <div className="result-grid">
        <div className="result-item">
          <span className="label">Kezdeti tömeg</span>
          <span className="value">{first?.mass.toExponential(4)} kg</span>
        </div>
        <div className="result-item">
          <span className="label">Végső tömeg</span>
          <span className="value">{last?.mass.toExponential(4)} kg</span>
        </div>
        <div className="result-item">
          <span className="label">Tömegveszteség</span>
          <span className="value">{massDelta.toFixed(6)}%</span>
        </div>
        <div className="result-item">
          <span className="label">Hőmérséklet (T)</span>
          <span className="value">{last?.temperature.toExponential(3)} K</span>
        </div>
        <div className="result-item">
          <span className="label">Entrópia (S)</span>
          <span className="value">{last?.entropy.toExponential(3)}</span>
        </div>
        <div className="result-item">
          <span className="label">Időlépések</span>
          <span className="value">{results.timeline.length}</span>
        </div>
        <div className="result-item">
          <span className="label">Mód</span>
          <span className="value">{norbiMode ? "Norbi-hipotézis" : "Standard Hawking"}</span>
        </div>
        <div className="result-item">
          <span className="label">Elpárolgott</span>
          <span className="value">{results.evaporation_complete ? "Igen ✓" : "Nem"}</span>
        </div>
      </div>

      {norbiMode && (
        <div className="norbi-note">
          <strong>Norbi-hipotézis:</strong> A fekete lyuk belsejében kvantumvisszapattanással
          bébiuniverzum keletkezett. A Hawking-sugárzás a belső tágulás szélén szétszakadó
          anyagból ered.
        </div>
      )}
    </div>
  );
};
