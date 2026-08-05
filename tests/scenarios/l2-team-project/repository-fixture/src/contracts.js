export const ACCOUNT_STATUSES = Object.freeze(["enabled", "disabled"]);

export function isAccountStatus(value) {
  return ACCOUNT_STATUSES.includes(value);
}
