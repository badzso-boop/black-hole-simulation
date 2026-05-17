import React from "react";

interface ConfigPanelProps {
  mass: number;
  norbiMode: boolean;
  loading: boolean;
  onMassChange: (mass: number) => void;
  onNorbiToggle: (enabled: boolean) => void;
  onRun: () => void;
}

const MASS_PRESETS = [
  { label: "Planck-tömeg", value: 2.176e-8 },
  { label: "Csillag (1 M☉)", value: 1.989e30 },
  { label: "Szupermasszív (1M M☉)", value: 1.989e36 },
];

export const ConfigPanel: React.FC<ConfigPanelProps> = ({
  mass,
  norbiMode,
  loading,
  onMassChange,
  onNorbiToggle,
  onRun,
}) => {
  const log10Mass = Math.log10(Math.max(mass, 1e-10));

  return (
    <div className="config-panel">
      <h3>Szimuláció beállítások</h3>

      <div className="field">
        <label>Fekete lyuk tömege</label>
        <input
          type="range"
          min={-10}
          max={40}
          step={0.1}
          value={log10Mass}
          onChange={(e) => onMassChange(Math.pow(10, parseFloat(e.target.value)))}
        />
        <span className="value">{mass.toExponential(3)} kg</span>
      </div>

      <div className="presets">
        {MASS_PRESETS.map((p) => (
          <button key={p.label} onClick={() => onMassChange(p.value)} className="preset-btn">
            {p.label}
          </button>
        ))}
      </div>

      <div className="field toggle">
        <label>Norbi-hipotézis mód</label>
        <input
          type="checkbox"
          checked={norbiMode}
          onChange={(e) => onNorbiToggle(e.target.checked)}
        />
        <span className="hint">
          {norbiMode ? "Bébiuniverzum + kvantumvisszapattanás" : "Standard Hawking-sugárzás"}
        </span>
      </div>

      <button className="run-btn" onClick={onRun} disabled={loading}>
        {loading ? "Futtatás..." : "▶ Szimuláció indítása"}
      </button>
    </div>
  );
};
