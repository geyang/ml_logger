// Sigma Algebra for lists

// console.log('');
//
// function unique(s) {
//   return [...new Set(s)]
// }
//
// function add(s1, s2) {
//   return unique([...s1, ...s2]);
// }
//
// let res = add([], []);
// console.log(res);

export function unique(s) {
  return [...new Set(s)]
}

export function add(s1, s2) {
  return unique([...s1, ...s2]);
}

export const union = add;

export function minus(s1, s2 = []) {
  return [...s1].filter(s => s2.indexOf(s) === -1)
}

export function match(s, query) {
  return s.filter(s => s.match(query))
}

export function intersect(s1, s2) {
  return s1.filter(s => s2.indexOf(s) > -1)
}

