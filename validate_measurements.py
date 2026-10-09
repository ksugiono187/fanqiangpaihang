from pathlib import Path
from datetime import datetime
import json

root=Path(__file__).parent
records=json.loads((root/'data/third-party-tests.json').read_text(encoding='utf-8'))
brands=json.loads((root/'data/brands.json').read_text(encoding='utf-8'))
assert len(records)==29 and {r['id'] for r in records}=={b['id'] for b in brands}
counts={s:sum(r['status']==s for r in records) for s in ('dated_report','undated_report','not_collected')}
assert counts=={'dated_report':10,'undated_report':1,'not_collected':18}
for r in records:
    for prefix,suffix in [('brands',''),('articles','-review')]:
        document=(root/'dist'/prefix/(r['id']+suffix)/'index.html').read_text(encoding='utf-8')
        assert '第三方测速资料' in document
        if r['status']=='not_collected':
            assert not r.get('results') and '本轮未收录可核对' in document
        else:
            assert r['sourceUrl'] in document and r['evidenceUrl'] in document
            assert '翻墙排行未亲测' in document and '1 MB/s = 8 Mbps' in document
            assert r['threads'] in (1,32)
            assert len(r['results'])==2 and {v['region'] for v in r['results']}=={'香港','美国'}
            for v in r['results']:
                assert f"{v['downloadMBps']*8:.2f} Mbps" in document
                success,total=map(int,v['resultNodes'].split('/'))
                assert 0<=success<=total==v['testedNodes']
            if r['status']=='dated_report':
                assert datetime.strptime(r['testedAt'][:10],'%Y-%m-%d')<=datetime(2026,10,9)
            else:
                assert r['testedAt'] is None and '日期、时段未明确' in document
assert next(r for r in records if r['id']=='flycat')['testedNodes']==57
assert next(r for r in records if r['id']=='u1s1')['testedNodes']==61
assert next(r for r in records if r['id']=='u1s1')['threads']==1
print(json.dumps({'coverage':29,'reports':11,'date_known':10,'date_unknown':1,'unfilled':18,'provenance_and_units':'passed'},ensure_ascii=False))
