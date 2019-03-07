// Sigma Algebra for lists

export function unique(s) {
  return [...new Set(s)]
}

export function minus(s1, s2 = []) {
  return [...s1].filter(s => s2.indexOf(s) === -1)
}

export function match(s, query) {
  return s.filter(s => s.match(query))
}

export function intersect(s1, s2) {
  return s1.filter(s => s2.indexOf(s) > -1)
}
