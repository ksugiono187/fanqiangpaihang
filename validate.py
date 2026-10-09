from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
import json, xml.etree.ElementTree as ET

root=Path(__file__).parent
dist=root/'dist'
class Parse(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.titles=[];self.descriptions=[];self.canonical=[];self.in_title=False;self.structured=[];self.in_json=False
    def handle_starttag(self,t,attrs):
        a=dict(attrs)
        if t=='title':self.in_title=True
        if t=='meta' and a.get('name')=='description':self.descriptions.append(a.get('content'))
        if t=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
        if t=='script' and a.get('type')=='application/ld+json':self.in_json=True
        if t in ('a','link','script'):
            u=a.get('href',a.get('src',''))
            if u.startswith('/'):self.links.append(u)
    def handle_endtag(self,t):
        if t=='title':self.in_title=False
        if t=='script':self.in_json=False
    def handle_data(self,s):
        if self.in_title:self.titles.append(s)
        if self.in_json:self.structured.append(json.loads(s))
pages=json.loads((root/'data/pages.json').read_text(encoding='utf-8'))
articles=json.loads((root/'data/articles.json').read_text(encoding='utf-8'))
brands=json.loads((root/'data/brands.json').read_text(encoding='utf-8'))
assert len(articles)==150 and len(brands)==29
assert len({a['slug'] for a in articles})==150
assert len({a['title'] for a in articles})==150
assert [b['id'] for b in brands[:10]]==['breezenet','flycat','twilight','dalaocloud','firefly','civet','flashleap','worryfree','kuajie','2mao']
assert sum(bool(b['coupon']) for b in brands)==11
titles=[];descs=[];broken=[]
for record in pages:
    target=dist/record['path'].lstrip('/')/'index.html'
    text=target.read_text(encoding='utf-8');assert '\ufffd' not in text,target
    p=Parse();p.feed(text)
    assert len(p.titles)==1 and len(p.descriptions)==1 and len(p.canonical)==1,target
    assert p.canonical[0]=='https://fanqiangpaihang.wiki'+record['path']
    assert p.structured,target
    titles.extend(p.titles);descs.extend(p.descriptions)
    for u in p.links:
        url=urlparse(u);t=dist/url.path.lstrip('/')
        if url.path.endswith('/'):t=t/'index.html'
        if not t.exists():broken.append((record['path'],u))
assert not broken,broken
assert len(titles)==len(set(titles)), 'Duplicate titles'
assert len(descs)==len(set(descs)), 'Duplicate descriptions'
sitemap=ET.parse(dist/'sitemap.xml')
locs=[e.text for e in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(locs)==len(pages)==200
assert set(locs)=={'https://fanqiangpaihang.wiki'+p['path'] for p in pages}
print(json.dumps({'pages':len(pages),'articles':len(articles),'brands':len(brands),'plans':sum(len(b['plans']) for b in brands),'coupons':11,'broken_internal_links':len(broken),'unique_tdk':True,'sitemap_verified':True},ensure_ascii=True))
