// T402 geometry tests for the deterministic force layout:
// determinism (fixed seed), collision guarantee (qc5_no_overlap, gap >= 8px),
// structure-keyed cache, and re-layout on structure change.
import { describe, expect, it } from "vitest";
import type { Lineage } from "../api";
import {
  DEFAULT_NODE_SIZE,
  MIN_GAP,
  clearLayoutCache,
  computeForceLayout,
  forceLayout,
  layoutCacheStats,
  mulberry32,
  separateCollisions,
  structureKey,
} from "../forceLayout";
import type { Pt } from "../forceLayout";

const W = 1400;
const H = 820;

function makeLineage(ids: string[], edges: [string, string][]): Lineage {
  return {
    nodes: ids.map((id) => ({ id, label: id, layer: "CDM", unconfirmed: false })),
    edges: edges.map(([source, target]) => ({
      source,
      target,
      via_script: "",
      unconfirmed: false,
    })),
    layers: {},
    stats: { nodes: ids.length, edges: edges.length, unconfirmed_edges: 0 },
  };
}

/** Worst-case axis clearance over all pairs (AABB free gap, >= MIN_GAP required). */
function minPairGap(pos: Record<string, Pt>, size = DEFAULT_NODE_SIZE): number {
  const ids = Object.keys(pos);
  let worst = Infinity;
  for (let i = 0; i < ids.length; i++) {
    for (let j = i + 1; j < ids.length; j++) {
      const dx = Math.abs(pos[ids[i]].x - pos[ids[j]].x) - size.width;
      const dy = Math.abs(pos[ids[i]].y - pos[ids[j]].y) - size.height;
      worst = Math.min(worst, Math.max(dx, dy));
    }
  }
  return worst;
}

/** Dense 10-node graph: two tight clusters plus cross links. */
const DENSE_IDS = [
  "d_auth",
  "d_channel",
  "d_cust",
  "d_order",
  "d_payment",
  "d_product",
  "d_risk",
  "d_supply",
  "d_user",
  "d_warehouse",
];
const DENSE_EDGES: [string, string][] = [
  ["d_order", "d_payment"],
  ["d_order", "d_product"],
  ["d_order", "d_cust"],
  ["d_order", "d_supply"],
  ["d_payment", "d_risk"],
  ["d_cust", "d_user"],
  ["d_user", "d_auth"],
  ["d_product", "d_warehouse"],
  ["d_supply", "d_warehouse"],
  ["d_channel", "d_order"],
  ["d_channel", "d_cust"],
  ["d_auth", "d_risk"],
  ["d_payment", "d_supply"],
  ["d_risk", "d_order"],
];

describe("structureKey / mulberry32 (pure helpers)", () => {
  it("structure key ignores node array order and badge flags", () => {
    const a = makeLineage(["n1", "n2", "n3"], [["n1", "n2"]]);
    const shuffled = makeLineage(["n3", "n1", "n2"], [["n1", "n2"]]);
    shuffled.nodes[0].unconfirmed = true;
    expect(structureKey(shuffled)).toBe(structureKey(a));
  });

  it("structure key changes when a node or edge is added", () => {
    const a = makeLineage(["n1", "n2"], [["n1", "n2"]]);
    const withNode = makeLineage(["n1", "n2", "n3"], [["n1", "n2"]]);
    const withEdge = makeLineage(["n1", "n2"], [["n1", "n2"], ["n2", "n1"]]);
    expect(structureKey(withNode)).not.toBe(structureKey(a));
    expect(structureKey(withEdge)).not.toBe(structureKey(a));
  });

  it("mulberry32 is a stable function of its seed", () => {
    const seq = (seed: number) => {
      const rng = mulberry32(seed);
      return Array.from({ length: 5 }, () => rng());
    };
    expect(seq(42)).toEqual(seq(42));
    expect(seq(42)).not.toEqual(seq(43));
  });
});

describe("separateCollisions (pure geometry)", () => {
  it("separates stacked identical positions to >= MIN_GAP", () => {
    const stacked = Array.from({ length: 10 }, () => ({ x: 700, y: 410 }));
    const out = separateCollisions(stacked, DEFAULT_NODE_SIZE);
    expect(minPairGap(Object.fromEntries(out.map((p, i) => [`n${i}`, p])))).toBeGreaterThanOrEqual(
      MIN_GAP
    );
  });

  it("does not mutate its input", () => {
    const input = [
      { x: 100, y: 100 },
      { x: 110, y: 100 },
    ];
    const snapshot = input.map((p) => ({ ...p }));
    separateCollisions(input, DEFAULT_NODE_SIZE);
    expect(input).toEqual(snapshot);
  });
});

describe("forceLayout determinism (fixed seed)", () => {
  it("same input twice yields identical coordinates (①)", () => {
    const g = makeLineage(DENSE_IDS.slice(0, 7), [
      ["d_auth", "d_channel"],
      ["d_channel", "d_cust"],
      ["d_cust", "d_order"],
      ["d_order", "d_auth"],
    ]);
    clearLayoutCache();
    const first = forceLayout(g, W, H);
    clearLayoutCache(); // bypass the cache: recompute must land on the same coords
    const second = forceLayout(g, W, H);
    expect(second).toEqual(first);
    // same holds for the pure compute path
    expect(computeForceLayout(g, W, H)).toEqual(first);
  });

  it("node payload order and badge flags do not move nodes", () => {
    const g = makeLineage(DENSE_IDS.slice(0, 7), [["d_auth", "d_channel"]]);
    const reordered = makeLineage(
      [...g.nodes].reverse().map((n) => n.id),
      [["d_auth", "d_channel"]]
    );
    reordered.nodes.forEach((n) => {
      n.unconfirmed = true;
    });
    clearLayoutCache();
    expect(forceLayout(reordered, W, H)).toEqual(forceLayout(g, W, H));
  });
});

describe("forceLayout collision guarantee (qc5_no_overlap)", () => {
  it("all bounding-box gaps >= 8px on a dense 10-node graph (②)", () => {
    const g = makeLineage(DENSE_IDS, DENSE_EDGES);
    clearLayoutCache();
    const pos = forceLayout(g, W, H);
    expect(Object.keys(pos)).toHaveLength(10);
    expect(minPairGap(pos)).toBeGreaterThanOrEqual(MIN_GAP);
  });

  it("still holds on a tight canvas with an overlapping start cluster", () => {
    const g = makeLineage(DENSE_IDS, DENSE_EDGES);
    clearLayoutCache();
    const pos = forceLayout(g, 900, 600);
    expect(minPairGap(pos)).toBeGreaterThanOrEqual(MIN_GAP);
  });
});

describe("forceLayout result cache", () => {
  it("unchanged structure hits the cache: compute runs once (③)", () => {
    const g = makeLineage(DENSE_IDS.slice(0, 8), [["d_auth", "d_channel"]]);
    clearLayoutCache();
    forceLayout(g, W, H);
    expect(layoutCacheStats.computes).toBe(1);
    const again = forceLayout(g, W, H);
    expect(layoutCacheStats.computes).toBe(1);
    expect(layoutCacheStats.hits).toBe(1);
    expect(again).toEqual(forceLayout(g, W, H));
  });

  it("badge-only change (unconfirmed) does not trigger recompute", () => {
    const g = makeLineage(DENSE_IDS.slice(0, 8), [["d_auth", "d_channel"]]);
    const flagged = makeLineage(
      DENSE_IDS.slice(0, 8),
      [["d_auth", "d_channel"]]
    );
    flagged.nodes[2].unconfirmed = true;
    flagged.edges[0].unconfirmed = true;
    clearLayoutCache();
    const base = forceLayout(g, W, H);
    expect(forceLayout(flagged, W, H)).toEqual(base);
    expect(layoutCacheStats.computes).toBe(1);
  });
});

describe("forceLayout re-layout on structure change", () => {
  it("adding a node or an edge recomputes and stays deterministic + collision-free (④)", () => {
    const base = makeLineage(DENSE_IDS.slice(0, 8), [
      ["d_auth", "d_channel"],
      ["d_channel", "d_cust"],
    ]);
    const withNode = makeLineage(
      DENSE_IDS.slice(0, 9),
      base.edges.map((e) => [e.source, e.target] as [string, string])
    );
    const withEdge = makeLineage(DENSE_IDS.slice(0, 8), [
      ["d_auth", "d_channel"],
      ["d_channel", "d_cust"],
      ["d_cust", "d_payment"],
    ]);

    clearLayoutCache();
    forceLayout(base, W, H);
    expect(layoutCacheStats.computes).toBe(1);
    expect(Object.keys(forceLayout(withNode, W, H))).toHaveLength(9);
    expect(layoutCacheStats.computes).toBe(2);
    forceLayout(withEdge, W, H);
    expect(layoutCacheStats.computes).toBe(3);

    // re-layout results satisfy the same guarantees
    clearLayoutCache();
    const posNode = forceLayout(withNode, W, H);
    expect(forceLayout(withNode, W, H)).toEqual(posNode);
    expect(minPairGap(posNode)).toBeGreaterThanOrEqual(MIN_GAP);
    clearLayoutCache();
    const posEdge = forceLayout(withEdge, W, H);
    expect(forceLayout(withEdge, W, H)).toEqual(posEdge);
    expect(minPairGap(posEdge)).toBeGreaterThanOrEqual(MIN_GAP);
  });
});
