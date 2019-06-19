export function between(a, b, c) {
  return Math.min(b, c) <= a && a <= Math.max(b, c);
}

export function nOr(a, b) {
  return (a === null || typeof a === "undefined") ? b : a
}


