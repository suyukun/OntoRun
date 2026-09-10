// Minimal force-directed layout (no d3 dep): repulsion + edge springs +
// gravity, seeded by layer column (ODS->CDM->ADS pipeline flow, DIM below).
import type { Lineage } from "./api";

export interface Pt {
  x: number;
  y: number;
}

const LAYER_COLUMN: Record<string, number> = {
  ODS: 0,
  CDM: 1,
  DIM: 1.6,
  ADS: 2.6,
};

export function forceLayout(
  lineage: Lineage,
  width: number,
  height: number,
  iterations = 300
): Record<string, Pt> {
  const nodes = lineage.nodes;
  const idx = new Map(nodes.map((n, i) => [n.id, i]));
  const pos: Pt[] = nodes.map((n) => {
    const col = LAYER_COLUMN[n.layer] ?? 1;
    return {
      x: ((col / 2.6) * 0.72 + 0.14) * width + (Math.random() - 0.5) * 60,
      y: (0.18 + Math.random() * 0.64) * height,
    };
  });
  const edges = lineage.edges
    .map((e) => [idx.get(e.source), idx.get(e.target)] as [number, number])
    .filter(([s, t]) => s !== undefined && t !== undefined);

  const repulse = 26000;
  const springLen = 110;
  const springK = 0.015;
  const gravity = 0.03;

  for (let it = 0; it < iterations; it++) {
    const fx = new Array(nodes.length).fill(0);
    const fy = new Array(nodes.length).fill(0);
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        let dx = pos[i].x - pos[j].x;
        let dy = pos[i].y - pos[j].y;
        let d2 = dx * dx + dy * dy;
        if (d2 < 1) {
          dx = Math.random() - 0.5;
          dy = Math.random() - 0.5;
          d2 = 1;
        }
        const d = Math.sqrt(d2);
        const f = repulse / d2;
        fx[i] += (dx / d) * f;
        fy[i] += (dy / d) * f;
        fx[j] -= (dx / d) * f;
        fy[j] -= (dy / d) * f;
      }
    }
    for (const [s, t] of edges) {
      const dx = pos[t].x - pos[s].x;
      const dy = pos[t].y - pos[s].y;
      const d = Math.sqrt(dx * dx + dy * dy) || 1;
      const f = (d - springLen) * springK;
      fx[s] += (dx / d) * f * d;
      fy[s] += (dy / d) * f * d;
      fx[t] -= (dx / d) * f * d;
      fy[t] -= (dy / d) * f * d;
    }
    const cool = 1 - it / iterations;
    for (let i = 0; i < nodes.length; i++) {
      // gravity to canvas center
      fx[i] += (width / 2 - pos[i].x) * gravity;
      fy[i] += (height / 2 - pos[i].y) * gravity;
      const disp = Math.min(Math.hypot(fx[i], fy[i]), 40 * cool + 2);
      const norm = Math.hypot(fx[i], fy[i]) || 1;
      pos[i].x += (fx[i] / norm) * disp;
      pos[i].y += (fy[i] / norm) * disp;
      pos[i].x = Math.max(50, Math.min(width - 50, pos[i].x));
      pos[i].y = Math.max(40, Math.min(height - 40, pos[i].y));
    }
  }
  return Object.fromEntries(nodes.map((n, i) => [n.id, pos[i]]));
}
