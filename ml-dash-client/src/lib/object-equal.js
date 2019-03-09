//this is not symmetric.
export function equal(a, b) {
  for (let k of Object.keys(a)) {
    if (a[k] !== b[k])
      return false;
  }
  return true;
}
