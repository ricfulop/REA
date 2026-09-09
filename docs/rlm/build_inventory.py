"""Rebuild the discovery inventory from saved scite MCP responses."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
records = {}
searches = []
for path in sorted((ROOT / 'sources').glob('search-*.json')):
    data = json.loads(path.read_text())
    searches.append({'file': path.name, 'query': data['query'], 'total_matches': data['total'],
                     'retrieved': len(data['hits']), 'offset': data.get('offset', 0)})
    for hit in data['hits']:
        doi = hit['doi'].lower()
        record = records.setdefault(doi, {'doi': doi, 'title': hit['title'], 'year': hit.get('year'),
                                        'url': 'https://doi.org/' + doi, 'discovered_by': [],
                                        'status': 'candidate_not_fully_reviewed'})
        record['discovered_by'].append(path.name)
        record['abstract_available'] = bool(hit.get('abstract'))
        record['excerpts_available'] = bool(hit.get('fulltextExcerpts'))
        if hit.get('date', '') > '2026-09-09':
            record['status'] = 'publication_date_after_search_cutoff_check_online_date'
graph = json.loads((ROOT / 'sources/citation-graph.json').read_text())
for doi, paper in graph['papers'].items():
    record = records.setdefault(doi, {'doi': doi, **paper, 'url': 'https://doi.org/' + doi,
                                    'discovered_by': [], 'status': 'citation_neighbor_not_screened'})
    record['discovered_by'].append('citation-graph.json')
screen = ROOT / 'scite-screening.json'
if screen.exists():
    decisions = json.loads(screen.read_text())
    for decision in decisions['included']:
        records[decision['source_ref']]['status'] = 'priority_reading_not_fulltext_validated'
    for decision in decisions['excluded']:
        records[decision['source_ref']]['status'] = 'excluded_off_topic_title_screen'
inventory = sorted(records.values(), key=lambda r: (r['title'].lower(), r['doi']))
(ROOT / 'paper-inventory.json').write_text(json.dumps(inventory, indent=2))
with (ROOT / 'paper-inventory.csv').open('w', newline='') as stream:
    fields = ['title', 'year', 'doi', 'url', 'status', 'discovered_by']
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
    writer.writeheader()
    for record in inventory:
        writer.writerow({**record, 'discovered_by': ';'.join(record['discovered_by'])})
summary = {'searched_at_utc': '2026-09-09', 'provider': 'scite MCP', 'searches': searches,
           'unique_dois': len(records), 'citation_edges': graph['edge_count'],
           'graph_truncated': graph['truncated'], 'low_coverage_seeds': graph['low_coverage_seeds'],
           'limitations': ['Scoping discovery, not an exhaustive or PRISMA-complete systematic review.',
                          'Only the first page of each query was retrieved.',
                          'DOI deduplication retains preprint/published versions as separate records.',
                          'Citation neighbors are not automatically relevant or supporting evidence.',
                          'Some abstracts are truncated by the provider; full-text access varies.']}
(ROOT / 'search-log.json').write_text(json.dumps(summary, indent=2))
print(json.dumps({k: summary[k] for k in ('unique_dois', 'citation_edges', 'graph_truncated')}))
