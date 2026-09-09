"""Generate the complete paper taxonomy from the runtime's pinned definitions."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent

def tex(s):
    replacements = {'&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}'}
    return ''.join(replacements.get(c, c) for c in str(s)).replace('–', '--').replace('—', '---')

t = json.loads((ROOT.parent / 'rlm_memex/data/engineering_taxonomy.json').read_text())
lines = [r'\section{Complete engineering taxonomy}',
         'These editorial categories support browsing and scoped retrieval. Membership does not establish tool qualification. Counts refer to the pinned catalog snapshot; overlapping memberships are allowed.']
md = ['# Complete engineering tool taxonomy', '', t['method'], '', 'Version: `' + t['version'] + '`', '']
for d in t['domains']:
    lines += [r'\subsection{' + tex(d['label']) + '}',
              r'\noindent Domain: \texttt{' + tex(d['id']) + '}. Primary tool records: ' + str(d['tool_records']) + '.',
              r'\begin{longtable}{p{0.37\linewidth}p{0.47\linewidth}r}', r'ID & Subcategory & Count\\\hline\endhead']
    md += ['## ' + d['label'] + ' (`' + d['id'] + '`)', '', '| ID | Subcategory | Memberships |', '| --- | --- | ---: |']
    for c in d['subcategories']:
        lines += [tex(c['id']) + ' & ' + tex(c['label']) + ' & ' + str(c['tool_memberships']) + r'\\']
        md += [f"| {c['id']} | {c['label']} | {c['tool_memberships']} |"]
    lines += [r'\end{longtable}']
    md += ['']
(ROOT / 'taxonomy.tex').write_text('\n'.join(lines) + '\n')
(ROOT.parent / 'docs/rlm/ENGINEERING_TAXONOMY.md').write_text('\n'.join(md) + '\n')
