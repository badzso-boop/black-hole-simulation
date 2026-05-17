import React from "react";

interface KruskalDiagramProps {
  norbiMode: boolean;
  evaporationComplete: boolean;
}

export const KruskalDiagram: React.FC<KruskalDiagramProps> = ({
  norbiMode,
  evaporationComplete,
}) => {
  const W = 400;
  const H = 300;
  const cx = W / 2;
  const cy = H / 2;

  return (
    <div className="kruskal-diagram">
      <h4>Kruskal–Szekeres diagram</h4>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" height={H} style={{ background: "#0a0a1a" }}>
        {/* Tengelyek */}
        <line x1={0} y1={cy} x2={W} y2={cy} stroke="#333" strokeWidth="1" />
        <line x1={cx} y1={0} x2={cx} y2={H} stroke="#333" strokeWidth="1" />

        {/* Fényszerű irányok (45°) */}
        <line x1={0} y1={H} x2={W} y2={0} stroke="#222" strokeWidth="1" strokeDasharray="4" />
        <line x1={0} y1={0} x2={W} y2={H} stroke="#222" strokeWidth="1" strokeDasharray="4" />

        {/* Singularitás (top) */}
        {!norbiMode && (
          <path d={`M ${cx - 100} ${cy - 80} Q ${cx} ${cy - 110} ${cx + 100} ${cy - 80}`}
            fill="none" stroke="#ff3333" strokeWidth="2" strokeDasharray="8,4" />
        )}
        <text x={cx + 4} y={cy - 65} fill="#ff3333" fontSize="10">
          {norbiMode ? "kvantumvissza-pattanás" : "szingularitás"}
        </text>

        {/* Eseményhorizont */}
        <line x1={cx} y1={0} x2={W} y2={cy} stroke="#ff8c00" strokeWidth="2" />
        <line x1={cx} y1={0} x2={0} y2={cy} stroke="#ff8c00" strokeWidth="2" />
        <text x={cx + 40} y={cy - 30} fill="#ff8c00" fontSize="10">eseményhorizont</text>

        {/* Fekete lyuk belseje */}
        <path
          d={`M ${cx} 20 L ${W - 20} ${cy} L ${cx} ${cy - 20} L ${20} ${cy} Z`}
          fill="rgba(255, 140, 0, 0.08)"
        />

        {/* Norbi bébiuniverzum */}
        {norbiMode && (
          <ellipse
            cx={cx}
            cy={cy - 60}
            rx={40}
            ry={25}
            fill="rgba(60, 100, 255, 0.3)"
            stroke="#4488ff"
            strokeWidth="1.5"
          />
        )}
        {norbiMode && (
          <text x={cx - 35} y={cy - 57} fill="#88aaff" fontSize="9">bébiuniverzum</text>
        )}

        {/* Elpárlás jele */}
        {evaporationComplete && (
          <text x={cx - 30} y={H - 10} fill="#aaffaa" fontSize="11">✓ Elpárolgott</text>
        )}

        <text x="4" y="14" fill="#555" fontSize="9">T (Kruskal-idő) ↑</text>
        <text x={W - 50} y={H - 4} fill="#555" fontSize="9">X →</text>
      </svg>
    </div>
  );
};
