import React, { useMemo } from "react";
import type { TimeStep } from "../hooks/useSimulation";

interface SpectrumChartProps {
  timeline: TimeStep[];
}

export const SpectrumChart: React.FC<SpectrumChartProps> = ({ timeline }) => {
  const last = timeline[timeline.length - 1];

  const paths = useMemo(() => {
    if (!last?.spectrum?.intensities?.length) return null;
    const intensities = last.spectrum.intensities;
    const n = intensities.length;
    const maxI = Math.max(...intensities, 1e-100);
    const W = 400;
    const H = 150;

    const points = intensities
      .map((v, i) => `${(i / n) * W},${H - (v / maxI) * H * 0.95}`)
      .join(" ");

    return { points, W, H };
  }, [last]);

  if (!paths) {
    return <div className="chart-placeholder">Nincs spektrum adat</div>;
  }

  return (
    <div className="spectrum-chart">
      <h4>Hawking-sugárzás spektrum (T = {last.temperature.toExponential(3)} K)</h4>
      <svg viewBox={`0 0 ${paths.W} ${paths.H}`} width="100%" height={paths.H}>
        <polyline
          points={paths.points}
          fill="none"
          stroke="#ff8c00"
          strokeWidth="1.5"
        />
        <text x="4" y="14" fill="#aaa" fontSize="9">intenzitás</text>
        <text x={paths.W - 40} y={paths.H - 4} fill="#aaa" fontSize="9">frekvencia</text>
      </svg>
    </div>
  );
};
