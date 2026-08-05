import { isAccountStatus } from "./contracts.js";

export function serializeAccount(account) {
  if (!isAccountStatus(account.status)) {
    throw new TypeError("Unsupported account status");
  }
  return JSON.stringify(account);
}
