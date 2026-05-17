import React, { useMemo } from "react";
import type { TimeStep } from "../hooks/useSimulation";

interface InteriorViewProps {
  timeline: TimeStep[];
  norbiMode: boolean;
}

export const InteriorView: React.FC<InteriorViewProps> = ({ timeline, norbiMode }) => {
  const last = timeline[timeline.length - 1];

  const animationProgress = useMemo(() => {
    if (!timeline.length) return 0;
    return timeline.length / 100;
  }, [timeline.length]);

  const W = 400;
  const H = 200;
  const cx = W / 2;
  const cy = H / 2;

  if (!last) {
    return <div className="interior-view placeholder">Belső állapot: nincs adat</div>;
  }

  const atPlanck = last.interior?.at_planck_scale ?? false;
  const bounce = last.interior?.bounce_occurred ?? false;
  const babyAge = last.interior?.baby_universe?.age ?? 0;
  const scaleFactor = last.interior?.baby_universe?.scale_factor ?? 1;

  const horizonR = 60 + animationProgress * 5;
  const babyR = norbiMode ? Math.min(20 + scaleFactor * 5, 50) : 0;

  return (
    <div className="interior-view">
      <h4>Belső állapot {norbiMode ? "(Norbi-mód)" : "(Standard)"}</h4>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" height={H} style={{ background: "#050510" }}>
        {/* Fekete lyuk eseményhorizont */}
        <circle cx={cx} cy={cy} r={horizonR} fill="#000" stroke="#ff8c00" strokeWidth="2" />
        <text x={cx - 18} y={cy + 4} fill="#ff8c00" fontSize="9">BL</text>

        {/* Hawking sugárzás részecskék */}
        {[0, 1, 2, 3, 4, 5].map((i) => {
          const a = (i / 6) * Math.PI * 2 + animationProgress * 3;
          const r = horizonR + 10 + (i * 7) % 25;
          return (
            <circle
              key={i}
              cx={cx + Math.cos(a) * r}
              cy={cy + Math.sin(a) * r}
              r={2.5}
              fill="#ff6600"
              opacity={0.8}
            />
          );
        })}

        {/* Norbi: bébiuniverzum */}
        {norbiMode && babyR > 0 && (
          <>
            <circle
              cx={cx}
              cy={cy}
              r={babyR}
              fill="rgba(60, 100, 255, 0.25)"
              stroke="#4488ff"
              strokeWidth="1.5"
              strokeDasharray={bounce ? "none" : "4,2"}
            />
            <text x={cx - 12} y={cy + 3} fill="#88aaff" fontSize="8">bU</text>
          </>
        )}

        {/* Planck-határ jelző */}
        {atPlanck && (
          <text x={4} y={H - 8} fill="#ff4444" fontSize="10">⚠ Planck-határon</text>
        )}
        {bounce && (
          <text x={4} y={H - 22} fill="#44ffaa" fontSize="10">↩ Kvantumvisszapattanás</text>
        )}

        {norbiMode && babyAge > 0 && (
          <text x={W - 110} y={H - 8} fill="#aaaaff" fontSize="9">
            bU kor: {babyAge.toExponential(2)} s
          </text>
        )}
      </svg>
    </div>
  );
};
