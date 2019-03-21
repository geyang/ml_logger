export function strOrder(a, b) {
  let a_ = a.toLowerCase();
  let b_ = b.toLowerCase();
  if (a_ < b_) //sort string ascending
    return -1;
  if (a_ > b_)
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
