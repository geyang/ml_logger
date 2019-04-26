export function commonPrefix(array) {
  if (array.length === 0) return "";
  let _ = array.sort(strOrder);
  let s = _[0];
  let l = _[_.length - 1];
  for (let i = 0; i < s.length; i++) {
    if (s[i] !== l[i])
      return s.substr(0, i);
  }
  return "";
}

export function subPrefix(a, prefix) {
  return a.substring(prefix.length);
}

export function strOrder(a, b) {
  if (!a || !b) return 0;
  let a_ = a.toLowerCase();
  let b_ = b.toLowerCase();
  if (a_ < b_) //sort string ascending
    return -1;
  if (a_ > b_)
    return 1;
  return 0; //default return value (no sorting)
}

export function firstItem(a) {
  if (typeof a === 'object' && a.length)
    return a[0];
  else return a;
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
