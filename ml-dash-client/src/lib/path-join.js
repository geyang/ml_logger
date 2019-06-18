export function realPath(path) {
  let stack = path.split("/");
  let pathPieces = [];
  let p = stack.shift();
  while (stack.length) {
    if (p === '.') {
    } else if (p === "..") {
      pathPieces.pop();
    } else
      pathPieces.push(p);
    p = stack.shift();

  }
  return pathPieces.join("/");
}

export function pathJoin(...parts) {
  const separator = '/';
  parts = parts.map((part, index) => {
    if (index) {
      part = part.replace(new RegExp('^' + separator), '');
    }
    if (index !== parts.length - 1) {
      part = part.replace(new RegExp(separator + '$'), '');
    }
    return part;
  });
  return parts.join(separator);
}

export function relPath(root, path) {
  let _root = root.split('/');
  let _path = path.split('/');
  return _path.slice(_root.length).join('/');
}

export function basename(path) {
  return path.split('/').slice(-1)[0];
}
