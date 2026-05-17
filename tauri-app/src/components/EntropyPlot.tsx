import React, { useMemo } from "react";
import type { TimeStep } from "../hooks/useSimulation";

interface EntropyPlotProps {
  timeline: TimeStep[];
}

export const EntropyPlot: React.FC<EntropyPlotProps> = ({ timeline }) => {
  const path = useMemo(() => {
    if (!timeline.length) return null;
    const W = 400;
    const H = 150;
    const maxS = Math.max(...timeline.map((t) => t.entropy), 1e-100);
    const n = timeline.length;

    const points = timeline
      .map((t, i) => `${(i / (n - 1 || 1)) * W},${H - (t.entropy / maxS) * H * 0.95}`)
      .join(" ");

    const halfTime = timeline.length / 2;
    const pageX = (halfTime / n) * W;

    return { points, W, H, pageX };
  }, [timeline]);

  if (!path) {
    return <div className="chart-placeholder">Nincs entrópia adat</div>;
  }

  return (
    <div className="entropy-plot">
      <h4>Bekenstein-Hawking entrópia + Page-görbe</h4>
      <svg viewBox={`0 0 ${path.W} ${path.H}`} width="100%" height={path.H}>
        {/* Page-görbe vonal */}
        <line
          x1={path.pageX} y1={0}
          x2={path.pageX} y2={path.H}
          stroke="#4488ff"
          strokeDasharray="4"
          strokeWidth="1"
          opacity="0.5"
        />
        <text x={path.pageX + 4} y="14" fill="#4488ff" fontSize="9">Page-idő</text>
        <polyline
          points={path.points}
          fill="none"
          stroke="#00cc88"
          strokeWidth="1.5"
        />
        <text x="4" y="14" fill="#aaa" fontSize="9">S (entrópia)</text>
      </svg>
    </div>
  );
};
