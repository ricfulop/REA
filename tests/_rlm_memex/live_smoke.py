import json
from rlm import RLM
from rlm_memex import MemexStore
from rlm_memex.engine import run

calls = []
def factory(**kwargs):
    kwargs['on_subcall_start'] = lambda depth, model, prompt: calls.append({'depth': depth, 'model': model})
    kwargs['sampling_args'] = {'max_tokens': 4096}
    return RLM(**kwargs)

store = MemexStore(':memory:')
store.put('parts', 'fixture-a', '1', 'Fixture A', 'Test-only rated load: 17 N.', 'fixture')
store.put('parts', 'fixture-b', '1', 'Fixture B', 'Test-only rated load: 29 N.', 'fixture')
result = run(store, 'Read the two parts records using the REPL. Make one rlm_query call with their two numerical loads asking it to add them. Return their sum in N and the record IDs. This is a synthetic arithmetic check, not a physical assembly rating.', 'openai/gpt-5-nano', backend='openrouter', factory=factory)
output = {'response': result.response, 'subcalls': calls, 'seconds': result.execution_time, 'usage': result.usage_summary.to_dict()}
print(json.dumps(output, indent=2))
open('.local/live-smoke.json', 'w').write(json.dumps(output, indent=2))
assert calls, 'No recursive subcall observed'
assert '46' in result.response, 'Expected synthetic sum not returned'
