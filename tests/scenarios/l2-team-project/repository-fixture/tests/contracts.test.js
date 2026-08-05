import assert from "node:assert/strict";
import test from "node:test";

import { isAccountStatus } from "../src/contracts.js";

test("recognizes the executable account-status contract", () => {
  assert.equal(isAccountStatus("enabled"), true);
  assert.equal(isAccountStatus("active"), false);
});
