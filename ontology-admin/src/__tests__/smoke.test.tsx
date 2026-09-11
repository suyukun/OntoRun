// T0b smoke: verifies the vitest + jsdom + @testing-library pipeline
// by rendering an existing small component (RuleCard, readOnly mode,
// no API calls fired). M1 component tests (T203/T205) build on this.
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { CaliberRule } from "../api";
import RuleCard from "../components/RuleCard";

const smokeRule: CaliberRule = {
  id: "R1",
  description: "T0b smoke fixture",
  source_script: "smoke.py",
  status: "unverified",
  related_tables: [],
  last_record: null,
};

describe("smoke", () => {
  it("renders RuleCard in readOnly mode", () => {
    render(
      <RuleCard rule={smokeRule} confirmer="王工" onDone={() => {}} readOnly />
    );
    expect(screen.getByText(/R1/)).toBeTruthy();
    expect(screen.getByText("未确认")).toBeTruthy();
  });
});
