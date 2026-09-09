"""Reproducible analytical figures. No measured performance is synthesized."""
import os
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/rea-matplotlib')
from pathlib import Path
import csv
import hashlib
import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parent
s = json.loads((ROOT / 'scenarios.json').read_text())
W = s['window_tokens']
parts = s['parts']['records'] * s['parts']['tokens_per_record']
manuals = s['manuals']['documents'] * s['manuals']['tokens_per_document']
rows = [('Single prompt', W), ('Operating manuals', manuals), ('Part specifications', parts), ('Combined corpus', parts + manuals)]
with (ROOT / 'capacity-data.csv').open('w') as f:
    w = csv.writer(f, lineterminator='\n')
    w.writerow(['scenario', 'tokens', 'window_equivalents', 'orders_above_window'])
    for name, tokens in rows:
        w.writerow([name, tokens, tokens / W, math.log10(tokens / W)])
with (ROOT / 'sensitivity-data.csv').open('w') as f:
    w = csv.writer(f, lineterminator='\n')
    w.writerow(['corpus', 'records', 'assumed_tokens_per_record', 'tokens', 'window_equivalents'])
    for name, count, densities in [('parts', s['parts']['records'], s['parts']['sensitivity_tokens_per_record']), ('manuals', s['manuals']['documents'], s['manuals']['sensitivity_tokens_per_document'])]:
        for density in densities:
            w.writerow([name, count, density, count*density, count*density/W])

import importlib.util
style_path = Path(os.environ.get('REA_FIGURE_STYLE', '/Users/ricfulop/voltivity/sci-viz-mcp/styles.py'))
if not style_path.is_file():
    raise SystemExit('Set REA_FIGURE_STYLE to your canonical sci-viz-mcp/styles.py')
spec = importlib.util.spec_from_file_location('rea_figure_style', style_path)
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)
apply_science_style, science_triple, OKABE_ITO = style.apply_science_style, style.science_triple, style.OKABE_ITO
apply_science_style()
# Size lettering for reduction from the Science canvas to ICLR text width.
plt.rcParams.update({'font.size': 9, 'axes.labelsize': 9,
                     'xtick.labelsize': 9, 'ytick.labelsize': 9,
                     'svg.fonttype': 'none'})
BLUE, ORANGE, GREEN, DARK = (OKABE_ITO[k] for k in ('blue', 'vermillion', 'purple', 'black'))

def save(fig, name):
    for ext in ['pdf', 'svg', 'png']:
        with plt.rc_context({'savefig.bbox': 'standard'}):
            fig.savefig(ROOT / f'{name}.{ext}', dpi=300, facecolor='white')
    svg = ROOT / f'{name}.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
    plt.close(fig)

fig = plt.figure(figsize=science_triple(height=4.6))
fig.text(.04, .915, 'Analytical scenario: 60 million parts + 1 million operating manuals', color=DARK)
ax = fig.add_axes([.27, .37, .66, .47])
colors = [DARK, GREEN, BLUE, ORANGE]
markers = ['s', '^', 'o', 'D']
for y, ((name, tokens), color, marker) in enumerate(zip(rows, colors, markers)):
    ax.scatter(tokens, 3-y, c=color, marker=marker, s=65, zorder=3)
    if y:
        ax.annotate(f'{tokens/1e9:,.0f}B tokens  |  {tokens/W:,.0f}×', (tokens, 3-y),
                    xytext=(-8, 12), textcoords='offset points', ha='right', color=DARK, fontsize=9)
    else:
        ax.annotate('1M tokens  |  1×', (tokens, 3-y), xytext=(8, 9), textcoords='offset points')
ax.axvline(W, color=DARK, linestyle='--', linewidth=1)
ax.set_xscale('log')
ax.set_xlim(5e5, 1e11)
ax.set_ylim(-.45, 3.55)
ax.set_yticks([3,2,1,0], [r[0] for r in rows])
ax.set_xticks([1e6,1e7,1e8,1e9,1e10,1e11], ['1M','10M','100M','1B','10B','100B'])
ax.set_xlabel('Corpus size (tokens; logarithmic scale, base 10)')
ax.grid(False)
ax.minorticks_off()
ax.tick_params(axis='y', length=0, pad=12)
for sp in ['top','right','left']: ax.spines[sp].set_visible(False)
fig.text(.04,.23, 'Explicit assumptions', weight='bold')
fig.text(.04,.185, 'Parts: 60M × 500 tokens = 30B. Manuals: 1M × 10,000 tokens = 10B.')
fig.text(.04,.14, 'Sensitivity: 100–2,000 tokens/part gives 6,000–120,000 prompt equivalents.')
fig.text(.04,.095, 'At 500 tokens/part, a 1M-token prompt holds at most 2,000 parts (0.0033%).')
fig.text(.04,.043, 'Capacity illustration, not measured REA throughput, accuracy, or exhaustive coverage.', fontsize=8, color=DARK)
save(fig, 'corpus-capacity')

fig, ax = plt.subplots(figsize=science_triple(height=6.0))
fig.subplots_adjust(left=.025,right=.975,bottom=.025,top=.975)
ax.set(xlim=(0,10),ylim=(0,10)); ax.axis('off')

def box(x,y,w,h,text,color=DARK,fill='#FFFFFF',style='solid',size=9):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.07,rounding_size=.08',
                              edgecolor=color,facecolor=fill,linestyle=style,linewidth=1.2))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=size,color=DARK)
def arrow(a,b,color=DARK,style='solid',rad=0):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=11,color=color,
                                linestyle=style,connectionstyle=f'arc3,rad={rad}',linewidth=1.1))
ax.text(.1,9.05,'1  Single-call prompt',weight='bold')
box(.2,7.9,2.3,.8,'Selected specifications\nand manual excerpts')
box(3.55,7.9,2.6,.8,'One model call\n≤1M tokens')
box(7.2,7.9,2.4,.8,'Engineering response')
arrow((2.6,8.3),(3.45,8.3));arrow((6.25,8.3),(7.1,8.3))
ax.text(.2,7.48,'Only supplied evidence is visible in this call; selection must happen upstream.',size=8)
ax.text(.1,6.91,'2  Retrieval-based agent',weight='bold')
box(.2,5.85,2.3,.8,'Large external corpus')
box(3.55,5.85,2.6,.8,'Retrieve excerpts\n+ bounded model call')
box(7.2,5.85,2.4,.8,'Response / next query')
arrow((2.6,6.25),(3.45,6.25));arrow((6.25,6.25),(7.1,6.25))
ax.text(.2,5.43,'Also accesses corpora larger than a prompt and can iterate across turns.',size=8)
ax.text(.1,4.86,'3  REA recursive investigation',weight='bold',color=DARK)
box(.2,3.25,2.3,1.15,'Versioned stores\nParts • tools • manuals\nDatasets • evidence',BLUE,'#FFFFFF')
box(3.55,3.25,2.6,1.15,'Root investigation\nPlan • inspect • recurse\nRevisit unresolved evidence',BLUE,'#FFFFFF',size=8.5)
box(7.2,3.25,2.4,1.15,'Integrate findings\nCheck constraints\nCite sources / abstain',BLUE,'#FFFFFF')
arrow((2.6,3.85),(3.45,3.85),BLUE);arrow((6.25,3.85),(7.1,3.85),BLUE)
box(3.2,1.45,1.9,.85,'Parts subcall\nFilter specifications',BLUE,size=8)
box(5.5,1.45,1.9,.85,'Procedure subcall\nInspect procedure\nReturn findings',BLUE,size=8)
arrow((4.05,3.15),(4.05,2.4),BLUE);arrow((5.6,3.15),(6.35,2.4),BLUE)
arrow((5.0,2.3),(4.85,3.15),BLUE,rad=-.12)
arrow((6.9,2.3),(6.05,3.15),BLUE,rad=.12)
box(.2,1.45,2.3,.85,'Paged access\n+ durable state\nNeeded for target scale',ORANGE,style='dashed',size=8)
arrow((1.35,2.38),(1.35,3.15),ORANGE,style='dashed')
ax.text(.2,.87,'Every model call remains bounded. Selective access does not imply reading every record.',size=8)
ax.text(.2,.43,'Current REA materializes a bounded corpus in RAM. 60M-part operation is a design target.',size=8)
save(fig, 'recursive-workflow')
manifest={'evidence_type':'analytical scenario and architecture diagram; no experimental outcomes',
          'inputs':{'scenarios.json':hashlib.sha256((ROOT/'scenarios.json').read_bytes()).hexdigest()},
          'matplotlib':matplotlib.__version__, 'exports':['pdf','svg','png'], 'png_dpi':300,
          'dimensions_inches':{'corpus-capacity':list(science_triple(4.6)),'recursive-workflow':list(science_triple(6.0))},
          'style':'Ric Fulop science-figure-style; external canonical styles.py',
          'style_sha256':hashlib.sha256(style_path.read_bytes()).hexdigest(),
          'transforms':['tokens=count*density','window_equivalents=tokens/1000000','log10 x-axis'],
          'missing_data':'No performance data available; none plotted',
          'randomness':'None', 'intervals':'Sensitivity scenarios, not confidence intervals'}
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
