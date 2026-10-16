// Structured decode result -> the exact text the Python CLI prints.

export function titleLine(res) {
  return `  << ${res.title} >>  ${res.mode === 1 ? res.raw : ''}`;
}

export function renderText(res) {
  const lines = [];
  if (res.title) lines.push(titleLine(res));
  for (const l of res.lines) lines.push(l.text);
  if (res.pbf) lines.push('PBF: 1');
  if (res.end) lines.push('#end');
  return lines.join('\n') + '\n';
}
