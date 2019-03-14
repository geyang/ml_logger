export function strOrder(a, b) {
  a = a.toLowerCase();
  b = b.toLowerCase();
  if (a < b) //sort string ascending
    return -1;
  if (a > b)
    return 1;
  return 0; //default return value (no sorting)
}

export function by(orderFn, key) {
  return function (a, b) {
    return orderFn(a[key], b[key]);
  }
}


export function toTitle(key) {
  if (!key) return key;
  return key.replace(/\./g, ' ').replace(/_/g, ' ')
}

// export function prettify(value) {
//   switch(typeof)
// }
