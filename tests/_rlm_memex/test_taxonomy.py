import json
import tempfile
import unittest
from pathlib import Path

from rlm_memex.taxonomy import load_taxonomy, specialists, scope_context


class TaxonomyTests(unittest.TestCase):
    def test_complete_published_taxonomy(self):
        taxonomy = load_taxonomy()
        self.assertEqual(taxonomy['counts'], {
            'domains': 71, 'subcategories': 609, 'tool_records': 4795, 'memberships': 5658})
        registry = specialists(taxonomy)
        self.assertEqual(len(registry), 71)
        self.assertEqual(sum(len(p['subcategories']) for p in registry.values()), 609)
        self.assertEqual(sum(c['tool_memberships'] for p in registry.values()
                             for c in p['subcategories']), 5658)

    def test_duplicate_and_misparented_definitions_rejected(self):
        for mutate in ('duplicate', 'parent'):
            taxonomy = load_taxonomy()
            if mutate == 'duplicate':
                taxonomy['domains'].append(taxonomy['domains'][0])
            else:
                taxonomy['domains'][0]['subcategories'][0]['domain'] = 'wrong'
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'taxonomy.json'
                path.write_text(json.dumps(taxonomy))
                with self.assertRaises(ValueError):
                    load_taxonomy(path)

    def test_membership_not_keyword_routes_tools(self):
        registry = specialists()
        domain = 'cad'
        category = registry[domain]['subcategories'][0]['id']
        context = {'tools': {
            'in': {'id': 'in', 'body': json.dumps({'description': 'irrelevant words',
                     'subcategories': [{'id': category}], 'description_source_id': 'src-in'})},
            'out': {'id': 'out', 'body': json.dumps({'description': 'CAD mechanical design',
                      'subcategories': [], 'description_source_id': 'src-out'})}},
            'evidence': {'a': {'id': 'src-in'}, 'b': {'id': 'src-out'}}}
        scoped = scope_context(context, domain, category)
        self.assertEqual(set(scoped['tools']), {'in'})
        self.assertEqual(set(scoped['evidence']), {'a'})
        self.assertEqual(set(context['tools']), {'in', 'out'})

    def test_unknown_or_cross_domain_scope_rejected(self):
        with self.assertRaises(ValueError):
            scope_context({}, 'not-a-domain')
        with self.assertRaises(ValueError):
            scope_context({}, 'optics', 'cad-mechanical')

    def test_empty_scope_and_missing_sources_are_explicit(self):
        scoped = scope_context({}, 'optics')
        self.assertEqual(scoped['specialist']['tool_records_in_scope'], 0)
        category = specialists()['cad']['subcategories'][0]['id']
        scoped = scope_context({'tools': {'a': {'body': json.dumps({
            'subcategories': [{'id': category}], 'source_id': 'missing'})}}}, 'cad')
        self.assertEqual(scoped['specialist']['missing_evidence_ids'], ['missing'])

    def test_profiles_all_retain_scope_caveat(self):
        for profile in specialists().values():
            self.assertIn('membership as qualification', profile['instructions'])
            self.assertTrue(profile['subcategories'])


if __name__ == '__main__':
    unittest.main()
