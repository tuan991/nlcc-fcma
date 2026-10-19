import tempfile
import unittest
from pathlib import Path
from promptpilot.core import (build_prompt, clean_text, compact_text, compare_text, create_handoff,
    estimate_tokens, inspect_project, make_coding_prompt, prioritize_context, redact_secrets,
    compact_json_text, extract_relevant_snippets)

class CoreTests(unittest.TestCase):
    def test_clean_text(self): self.assertEqual(clean_text(' a  \r\n\r\n\r\nb \t'), 'a\n\nb')
    def test_compact_duplicate_lines(self): self.assertEqual(compact_text('a\nb\na'), 'a\nb')
    def test_compact_keeps_duplicates_when_disabled(self): self.assertEqual(compact_text('a\na', False), 'a\na')
    def test_estimate_has_range(self):
        result = estimate_tokens('hello world')
        self.assertLessEqual(result['estimated_tokens_low'], result['estimated_tokens_high'])
    def test_compare(self): self.assertEqual(compare_text('abcd', 'ab')['characters_saved'], 2)
    def test_build_prompt_requires_task(self):
        with self.assertRaises(ValueError): build_prompt(' ')
    def test_build_prompt_compact(self): self.assertIn('TASK:', build_prompt('Fix bug'))
    def test_handoff(self): self.assertIn('STATE:', create_handoff('working'))
    def test_prioritize_context(self):
        r = prioritize_context([{'text':'low','priority':0},{'text':'high','priority':2}], 4)
        self.assertEqual(r['included_indices'], [1])
        self.assertEqual(len(r['excluded_items']), 1)
    def test_redact_common_key(self):
        r = redact_secrets('api_key=sk-12345678901234567890')
        self.assertIn('REDACTED', r['text'])
        self.assertGreater(r['redactions'], 0)
    def test_coding_prompt_diff_first(self): self.assertIn('focused diff', make_coding_prompt('Fix a bug'))
    def test_inspect_project_selects_query_file_and_respects_budget(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, 'auth.py').write_text('def login():\n    return True\n', encoding='utf-8')
            Path(d, 'unrelated.py').write_text('print("hello")\n', encoding='utf-8')
            r = inspect_project(d, query='login', max_chars=1000)
            self.assertEqual(r['selected_files'][0]['path'], 'auth.py')
            self.assertLessEqual(r['selected_characters_approx'], 1000)
    def test_inspect_skips_env_file_contents(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, '.env').write_text('API_KEY=supersecretvalue', encoding='utf-8')
            r = inspect_project(d)
            self.assertEqual(r['selected_files'], [])

    def test_compact_json_preserves_parsed_data(self):
        import json
        original = '{\n  "name": "PromptPilot",\n  "items": [1, 2, 3]\n}'
        result = compact_json_text(original)
        self.assertTrue(result['compacted'])
        self.assertEqual(json.loads(result['text']), json.loads(original))
        self.assertLess(len(result['text']), len(original))

    def test_invalid_json_returns_original(self):
        original = '{not json}'
        result = compact_json_text(original)
        self.assertFalse(result['compacted'])
        self.assertEqual(result['text'], original)

    def test_extract_snippets_returns_relevant_exact_source(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, 'auth.py').write_text('def login(user):\n    # validate user\n    return authenticate(user)\n\ndef logout():\n    return True\n', encoding='utf-8')
            Path(d, 'other.py').write_text('def render_page():\n    return 1\n', encoding='utf-8')
            result = extract_relevant_snippets(d, 'authenticate', max_chars=1000, context_lines=1)
            self.assertTrue(result['snippets'])
            self.assertEqual(result['snippets'][0]['path'], 'auth.py')
            self.assertIn('authenticate(user)', result['snippets'][0]['text'])
            self.assertLessEqual(result['characters_used'], 1000)

    def test_extract_snippets_requires_query(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): extract_relevant_snippets(d, ' ')

    def test_empty_root_fails(self):
        with self.assertRaises(ValueError): inspect_project('/definitely/not/a/real/path')

if __name__ == '__main__': unittest.main()
