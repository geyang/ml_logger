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
