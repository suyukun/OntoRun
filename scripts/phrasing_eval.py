import json, sys, time
sys.path.insert(0, '.')
from src.semantic.llm_route import llm_route

cases = json.load(open('tests/fixtures/问法压力测试集_v0.1.json', encoding='utf-8'))
results = []
for c in cases:
    q, exp = c['q'], c.get('expect', {})
    t0 = time.time()
    try:
        r = llm_route(q)
        plan, raw = r.get('plan',''), r.get('raw','')
        ms = r.get('ms', 0)
    except Exception as e:
        plan, raw, ms = f'EXC:{e}', '', 0
    got_measure = None; got_dims = []; rejected = ('reject_domain=None' not in str(plan)) or ('"reject"' in str(raw) and 'true' in str(raw))
    if 'measure=' in str(plan) and 'None' not in str(plan).split('measure=')[1].split(',')[0]:
        got_measure = str(plan).split('measure=')[1].split(',')[0].strip().strip("'\"")
    if 'dimensions=' in str(plan):
        dimstr = str(plan).split('dimensions=')[1].split(')')[0]
        got_dims = [d.strip("' \"") for d in dimstr.replace('(','').replace(')','').split(',') if d.strip("' \"")]
    verdict = 'SKIP'
    if exp.get('reject'):
        verdict = 'PASS' if rejected else 'FAIL(应拒未拒)'
    elif exp.get('reject_or'):
        verdict = 'PASS' if (rejected or got_measure) else 'FAIL'
    elif exp.get('measure'):
        if rejected: verdict = 'FAIL(误拒)'
        elif got_measure != exp['measure']: verdict = f'FAIL(度量:{got_measure}≠{exp["measure"]})'
        else:
            want = [d.split('=')[0] for d in exp.get('dimensions', [])]
            have = [d.split('=')[0] for d in got_dims]
            missing = [w for w in want if w not in have]
            verdict = 'PASS' if not missing else f'FAIL(缺维度:{missing})'
    results.append({'q': q, 'verdict': verdict, 'ms': ms, 'plan': str(plan)[:80]})
    print(f"{verdict:22s} {ms:5.0f}ms  {q}")

ok = sum(1 for r in results if r['verdict']=='PASS')
core = [r for r in results if r['verdict'].startswith('FAIL')]
print(f'\n== 总计 {len(results)} 条: PASS {ok} / FAIL {len(core)} / SKIP {len(results)-ok-len(core)} ==')
for r in core: print(' FAIL:', r['verdict'], '|', r['q'], '|', r['plan'])