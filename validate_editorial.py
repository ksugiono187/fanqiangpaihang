from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
import json,re

root=Path(__file__).parent
articles=json.loads((root/'data/articles.json').read_text(encoding='utf-8'))
brands=json.loads((root/'data/brands.json').read_text(encoding='utf-8'))
audit=json.loads((root/'data/price-audit.json').read_text(encoding='utf-8'))
assert len(audit)==29 and sum(bool(r['reviewedAt']) for r in audit)==3
assert all('尚未取得当前购买页' in r['currentPriceStatus'] for r in audit)
byid={b['id']:b for b in brands}
byarticle={a['slug']:a for a in articles}
excluded={'firefly','jilian','kosing'}
for b in brands:
    document=(root/'dist/brands'/b['id']/'index.html').read_text(encoding='utf-8')
    assert 'id="price-check"' in document and '历史参考' in document
    for need in (80,200,500):
        eligible=[p for p in b['plans'] if p['cycle']=='月付' and p.get('gb') and p.get('quotaPeriod')=='month' and not p.get('capacityConflict') and p['gb']>=need]
        body=byarticle[b['id']+'-monthly']['body']
        assert f'{need}GB/月' in body
        if eligible and b['id'] not in excluded:
            p=min(eligible,key=lambda x:x['price'])
            assert f"{p['price']/need:.3f}元/实际使用GB" in body
        elif b['id'] in excluded:
            assert '暂不进入预算匹配' in body
    assert '<h2>已知资料与需要确认的内容</h2>' in byarticle[b['id']+'-review']['body']

def repetitions(rows):
    c=Counter(re.sub('<[^>]+>','',p) for a in rows for p in re.findall('<p>(.*?)</p>',a['body']) if len(re.sub('<[^>]+>','',p))>45)
    return sum(n-1 for n in c.values() if n>1),max(c.values(),default=0)

current=repetitions(articles)
baseline=root.parent.parent/'work/articles-before-quality.json'
if baseline.exists():
    old=repetitions(json.loads(baseline.read_text(encoding='utf-8')))
    assert current[0]<old[0],(current,old)
else:old=None

class Ids(HTMLParser):
    def __init__(self):super().__init__();self.ids=[]
    def handle_starttag(self,t,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
for p in (root/'dist').rglob('index.html'):
    parser=Ids();parser.feed(p.read_text(encoding='utf-8'))
    assert len(parser.ids)==len(set(parser.ids)),p
report={'brand_articles_revised':116,'before_repeated_paragraph_occurrences':old[0] if old else None,'after_repeated_paragraph_occurrences':current[0],'largest_repeated_paragraph_group':current[1],'price_checks':3,'current_price_confirmations':0,'scenario_calculations_and_anchors':'passed'}
print(json.dumps(report,ensure_ascii=False))
