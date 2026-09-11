// Deterministic force-directed layout (no d3 dep, ADR-0012): repulsion + edge
// springs + gravity. T402 guarantees:
// 1. fixed seed - the PRNG is seeded from a hash of the graph structure
//    (node id set + edge set), so the same structure always yields the same
//    layout; badge/status refreshes never move nodes;
// 2. collision pass - node bounding boxes are pushed apart until the free gap
//    between every pair is >= MIN_GAP (qc5_no_overlap, constructive guarantee);
// 3. result cache - cached per structure key, recomputed only when the graph
//    structure (or canvas) changes.
// Nodes are processed sorted by id, so payload order cannot change the layout.
import type { Lineage } from "./api";

export interface Pt {
  x: number;
  y: number;
}

export interface NodeSize {
  width: number;
  height: number;
}

/** Minimum free spacing between node bounding boxes (qc5_no_overlap). */
export const MIN_GAP = 8;
/** Default node box size; matches the table card size rendered in GraphHome. */
export const DEFAULT_NODE_SIZE: NodeSize = { width: 160, height: 60 };

const LAYER_COLUMN: Record<string, number> = {
  ODS: 0,
  CDM: 1,
  DIM: 1.6,
  ADS: 2.6,
};

const BOUND_PAD_X = 50;
const BOUND_PAD_Y = 40;
const COLLISION_ITERS = 200;

/** FNV-1a 32-bit hash. */
export function hashString(s: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

/** Canonical structure key: sorted node ids + sorted directed edge pairs. */
export function structureKey(lineage: Lineage): string {
  const ids = lineage.nodes
    .map((n) => n.id)
    .sort()
    .join(",");
  const edges = lineage.edges
    .map((e) => `${e.source}->${e.target}`)
    .sort()
    .join(",");
  return `n:${ids};e:${edges}`;
}

/** mulberry32 PRNG: tiny and deterministic, sufficient for layout jitter. */
export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Pure: returns a new array with every bounding-box pair separated to >= gap. */
export function separateCollisions(
  pos: readonly Pt[],
  size: NodeSize,
  gap = MIN_GAP
): Pt[] {
  const p = pos.map((q) => ({ ...q }));
  const minDx = size.width + gap;
  const minDy = size.height + gap;
  for (let iter = 0; iter < COLLISION_ITERS; iter++) {
    let violated = false;
    for (let i = 0; i < p.length; i++) {
      for (let j = i + 1; j < p.length; j++) {
        const dx = p[j].x - p[i].x;
        const dy = p[j].y - p[i].y;
        const needX = minDx - Math.abs(dx);
        const needY = minDy - Math.abs(dy);
        if (needX <= 0 || needY <= 0) continue; // already clear on some axis
        violated = true;
        // Push along the axis nearer clearance; ties broken by index parity.
        if (needX < needY || (needX === needY && (i + j) % 2 === 0)) {
          const dir = dx >= 0 ? 1 : -1;
          const step = needX / 2 + 0.5;
          p[i].x -= dir * step;
          p[j].x += dir * step;
        } else {
          const dir = dy >= 0 ? 1 : -1;
          const step = needY / 2 + 0.5;
          p[i].y -= dir * step;
          p[j].y += dir * step;
        }
      }
    }
    if (!violated) break;
  }
  return p;
}

function clampToCanvas(p: Pt, width: number, height: number): Pt {
  return {
    x: Math.max(BOUND_PAD_X, Math.min(width - BOUND_PAD_X, p.x)),
    y: Math.max(BOUND_PAD_Y, Math.min(height - BOUND_PAD_Y, p.y)),
  };
}

function samePositions(a: readonly Pt[], b: readonly Pt[]): boolean {
  return a.length === b.length && a.every((q, i) => q.x === b[i].x && q.y === b[i].y);
}

/** Alternate collision separation with canvas clamping until both hold. */
function settle(pos: Pt[], size: NodeSize, width: number, height: number): Pt[] {
  let cur = pos;
  for (let round = 0; round < 40; round++) {
    const separated = separateCollisions(cur, size);
    const clamped = separated.map((q) => clampToCanvas(q, width, height));
    if (samePositions(separated, clamped)) return clamped;
    cur = clamped;
  }
  // Pathological tiny canvas: prefer the qc5 spacing guarantee over bounds.
  return separateCollisions(cur, size);
}

function initPositions(
  nodes: { id: string; layer: string }[],
  width: number,
  height: number,
  rng: () => number
): Pt[] {
  return nodes.map((n) => {
    const col = LAYER_COLUMN[n.layer] ?? 1;
    return {
      x: ((col / 2.6) * 0.72 + 0.14) * width + (rng() - 0.5) * 60,
      y: (0.18 + rng() * 0.64) * height,
    };
  });
}

function simulate(
  pos: Pt[],
  edges: [number, number][],
  width: number,
  height: number,
  iterations: number,
  rng: () => number
): void {
  const nodes = pos.length;
  const repulse = 26000;
  const springLen = 110;
  const springK = 0.015;
  const gravity = 0.03;

  for (let it = 0; it < iterations; it++) {
    const fx = new Array(nodes).fill(0);
    const fy = new Array(nodes).fill(0);
    for (let i = 0; i < nodes; i++) {
      for (let j = i + 1; j < nodes; j++) {
        let dx = pos[i].x - pos[j].x;
        let dy = pos[i].y - pos[j].y;
        let d2 = dx * dx + dy * dy;
        if (d2 < 1) {
          dx = rng() - 0.5;
          dy = rng() - 0.5;
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
    for (let i = 0; i < nodes; i++) {
      // gravity to canvas center
      fx[i] += (width / 2 - pos[i].x) * gravity;
      fy[i] += (height / 2 - pos[i].y) * gravity;
      const mag = Math.hypot(fx[i], fy[i]);
      const disp = Math.min(mag, 40 * cool + 2);
      const norm = mag || 1;
      pos[i].x += (fx[i] / norm) * disp;
      pos[i].y += (fy[i] / norm) * disp;
    }
  }
}

/** Pure geometry (no cache): deterministic layout for the given lineage. */
export function computeForceLayout(
  lineage: Lineage,
  width: number,
  height: number,
  iterations = 300,
  nodeSize: NodeSize = DEFAULT_NODE_SIZE
): Record<string, Pt> {
  // Sorted by id: identical structures produce identical layouts regardless
  // of the order nodes arrive in.
  const nodes = [...lineage.nodes].sort((a, b) => (a.id < b.id ? -1 : 1));
  const idx = new Map(nodes.map((n, i) => [n.id, i]));
  const edges = lineage.edges
    .map((e) => [idx.get(e.source), idx.get(e.target)] as [number | undefined, number | undefined])
    .filter(
      (pair): pair is [number, number] => pair[0] !== undefined && pair[1] !== undefined
    );
  const rng = mulberry32(hashString(structureKey(lineage)));
  const pos = initPositions(nodes, width, height, rng);
  simulate(pos, edges, width, height, iterations, rng);
  const settled = settle(pos, nodeSize, width, height);
  return Object.fromEntries(nodes.map((n, i) => [n.id, settled[i]]));
}

const layoutCache = new Map<string, Record<string, Pt>>();
/** Counters for observability/tests: real computes vs cache hits. */
export const layoutCacheStats = { computes: 0, hits: 0 };

export function clearLayoutCache(): void {
  layoutCache.clear();
  layoutCacheStats.computes = 0;
  layoutCacheStats.hits = 0;
}

/** Cached entry point (signature compatible with the original forceLayout). */
export function forceLayout(
  lineage: Lineage,
  width: number,
  height: number,
  iterations = 300,
  nodeSize: NodeSize = DEFAULT_NODE_SIZE
): Record<string, Pt> {
  const key = `${structureKey(lineage)}#${width}x${height}i${iterations}b${nodeSize.width}x${nodeSize.height}`;
  const hit = layoutCache.get(key);
  if (hit) {
    layoutCacheStats.hits++;
    return hit;
  }
  layoutCacheStats.computes++;
  const result = computeForceLayout(lineage, width, height, iterations, nodeSize);
  layoutCache.set(key, result);
  return result;
}
