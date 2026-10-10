from pathlib import Path
import json, html, math, re, shutil
from urllib.parse import urlparse
from enhancements import enhance
from presentation import home_layout, brand_card, topic_cards
from guide_depth import EXTRAS, extra_guide, brand_brief
from comparison import public_brands, render_comparison, render_updates
from editorial import evidence_panel, focused_guide
from measurements import report_panel, coverage, entry_card
from content_revision import revise, price_panel, audit_table

ROOT=Path(__file__).parent
DIST=ROOT/'dist'
DOMAIN='https://fanqiangpaihang.wiki'
DATE='2026-10-09'
E=lambda x:html.escape(str(x),quote=True)
source=json.loads((ROOT/'data/reference-data.json').read_text(encoding='utf-8-sig'))
order='breezenet flycat twilight dalaocloud firefly civet flashleap worryfree kuajie 2mao sogo yuzhou 1fly edgenova kosing sujie kuaili stardream lightspeed v2yun u1s1 jilian globalcloud guangnianti flyv laddercloud wavenet lingdong invisible'.split()
coupons=dict(breezenet='weifeng90',flycat='flycat888',worryfree='wuyou666',flashleap='shanyue',firefly='firefly',stardream='nmw888',lightspeed='jichangcha09',v2yun='rabbit',u1s1='U1S1',globalcloud='tt88',yuzhou='YUZHOU553')
byid={b['id']:b for b in source['brands']}
verification={v['id']:v for v in json.loads((ROOT/'data/verification.json').read_text(encoding='utf-8'))}
test_records={v['id']:v for v in json.loads((ROOT/'data/third-party-tests.json').read_text(encoding='utf-8'))}
price_audit={v['id']:v for v in json.loads((ROOT/'data/price-audit.json').read_text(encoding='utf-8'))}
brands=[byid[x] for x in order]
for i,b in enumerate(brands):
    b['rank']=i+1
    b['coupon']=coupons.get(b['id'])
    b['couponStatus']='站长提供，尚未结算验证' if b['coupon'] else '本次未提供优惠码'
    b['importedAt']=DATE
    b['measurementStatus']='未进行独立实测'
    b['verification']=verification[b['id']]
    b['thirdPartyTest']=test_records[b['id']]
    b['priceAudit']=price_audit[b['id']]
    b.pop('couponTerms',None)
excluded={'firefly','jilian','kosing'}

def money(n):return f'{n:g}'
def quota(p):
    if p.get('gb') is None:
        vals=p.get('capacityValues')
        raw='/'.join(str(v) for v in vals) if vals else p.get('quotedGb')
        return f'{raw}GB，口径待确认' if raw else '容量未明确'
    period={'month':'月','year':'年总量','total':'总额度','unknown':'周期未知'}.get(p.get('quotaPeriod'),'周期待确认')
    return f"{p['gb']:g} GB / {period}"
def monthly(b):return sorted([p for p in b['plans'] if p['cycle']=='月付' and p.get('gb') and not p.get('capacityConflict') and p.get('quotaPeriod')=='month'],key=lambda p:p['price'])
def price(b):
    ps=monthly(b)
    if b['id'] in excluded:return '套餐归属或运营待核实'
    if not ps:return '月付资料待确认'
    return f"¥{money(ps[0]['price'])} / 月 · {quota(ps[0])}"
def para(s):return '<p>'+E(s)+'</p>'
def section(t,s):return '<h2>'+E(t)+'</h2>'+para(s)
def table(b,plans=None):
    rows=[]
    for p in plans if plans is not None else b['plans']:
        notes=[p.get('quotaNote','')]
        if p.get('capacityConflict'):notes.append('容量存在冲突，未参与计算')
        if p.get('promotional'):notes.append('活动版本，当前资格及在售情况需确认')
        if b['id'] in excluded:notes.append('历史参考：归属或运营状态未独立核实')
        cost=f"{p['price']/p['gb']:.3f} 元/GB" if p.get('gb') and p.get('quotaPeriod')=='month' and p['cycle']=='月付' and b['id'] not in excluded and not p.get('capacityConflict') else '不计算'
        rows.append(f"<tr><td>{E(p['name'])}</td><td>¥{money(p['price'])}<br>{E(p['cycle'])}</td><td>{E(quota(p))}</td><td>{cost}</td><td>{E(p.get('sourceDate','未注明'))}<br>{E('；'.join(filter(None,notes)))}</td></tr>")
    return '<div class="table-wrap"><table><thead><tr><th>套餐记录</th><th>总付款 / 周期</th><th>容量口径</th><th>标称成本</th><th>资料日期 / 差异</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'

pages=[]
favicon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><rect width="40" height="40" rx="4" fill="#182e36"/><path d="M9 29V22H14V29M18 29V15H23V29M27 29V8H32V29" fill="#e5c997"/></svg>'
(DIST/'assets/favicon.svg').write_text(favicon,encoding='utf-8')
for asset in ('app.js','style.css','editorial.css','test-record-template.txt','compare.mjs','comparison-core.mjs'):
    shutil.copyfile(ROOT/'assets'/asset,DIST/'assets'/asset)
nav='<a href="#site-search">搜索</a><a href="/topics/">严选专题</a><a href="/brands/">品牌库</a><a href="/compare/">比较</a><a href="/articles/">文章</a><a href="/coupons/">优惠码</a>'
def page(path,title,desc,body,kind='WebPage',article=None):
    if path.startswith('/brands/') and path!='/brands/':
        b=byid[path.split('/')[2]]
        marker='<section class="section"><h2>套餐与流量档案</h2>'
        body=body.replace(marker,'<nav class="brand-tabs" aria-label="品牌资料导航"><a href="#packages">套餐档案</a><a href="#public-test">测速资料</a><a href="#price-check">价格核对</a></nav><section class="section" id="packages"><h2>套餐与流量档案</h2>',1)
        panels=report_panel(b,test_records[b['id']])+price_panel(b,price_audit[b['id']])+'<details class="evidence-disclosure"><summary>展开入口与资料核对记录</summary>'+evidence_panel(b,verification[b['id']])+'</details>'
        body=body.replace('</section><div class="article">','</section>'+panels+'<div class="article">',1)
        if test_records[b['id']]['status']!='not_collected':
            body=body.replace('以下为套餐资料与分析。','下方包含套餐分析与有出处的第三方测速摘录。')
    if article and article['cat']=='测评研究':
        b=byid[article['brands'][0]]
        body=body.replace('<h2>已知资料与需要确认的内容</h2>',evidence_panel(b,verification[b['id']])+report_panel(b,test_records[b['id']])+'<h2>已知资料与需要确认的内容</h2>',1)
    if path=='/methodology/':
        body=body.replace('</article>',coverage(brands,test_records)+audit_table(brands,price_audit)+'</article>',1)
    if path in ('/','/brands/'):
        body+=entry_card() if path=='/brands/' else ''
    body=enhance(body,path,bool(article))
    nav_current='/brands/' if path.startswith('/brands/') else '/articles/' if path.startswith('/articles/') else '/topics/' if path.startswith('/topics/') else path
    page_nav=nav.replace('href="'+nav_current+'"','href="'+nav_current+'" aria-current="page"')
    route_class='route-home' if path=='/' else 'route-brand' if path.startswith('/brands/') and path!='/brands/' else 'route-journal' if path=='/articles/' or path.startswith('/articles/page/') else 'route-content'
    canonical=DOMAIN+path
    schema={'@context':'https://schema.org','@type':kind,'name':title,'description':desc,'url':canonical,'inLanguage':'zh-CN'}
    record_id=article['brands'][0] if article and article['cat']=='测评研究' else path.split('/')[2] if path.startswith('/brands/') and path!='/brands/' else None
    if record_id and test_records[record_id].get('sourceUrl'):
        schema['citation']=test_records[record_id]['sourceUrl']
    if article:
        schema.update(headline=title,datePublished=DATE,dateModified=DATE,author={'@type':'Organization','name':'翻墙排行编辑资料组','url':DOMAIN+'/about/'},publisher={'@type':'Organization','name':'翻墙排行','url':DOMAIN},mainEntityOfPage=canonical)
    schema2={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'翻墙排行','item':DOMAIN+'/'},{'@type':'ListItem','position':2,'name':title,'item':canonical}]} if path!='/' else {'@context':'https://schema.org','@type':'WebSite','name':'翻墙排行','url':DOMAIN,'inLanguage':'zh-CN'}
    document=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)}｜翻墙排行</title><meta name="description" content="{E(desc)}"><meta name="keywords" content="梯子推荐,机场推荐,{E(title.split('：')[0])}"><meta name="robots" content="index,follow"><link rel="canonical" href="{canonical}"><meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:site_name" content="翻墙排行"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canonical}"><meta property="og:locale" content="zh_CN"><meta name="theme-color" content="#f6f4ee"><link rel="icon" type="image/svg+xml" href="/assets/favicon.svg"><link rel="stylesheet" href="/assets/style.css"><link rel="stylesheet" href="/assets/editorial.css"><script src="/assets/app.js" defer></script><script type="application/ld+json">{json.dumps([schema,schema2],ensure_ascii=False).replace('</','<\\/')}</script></head><body class="{route_class}"><a class="skip" href="#main">跳到正文</a><header><div class="shell"><a class="logo" href="/" aria-label="翻墙排行首页"><span class="logo-mark" aria-hidden="true"><i></i><i></i><i></i></span><span>翻墙<b>排行</b><small>FANQIANGPAIHANG</small></span></a><nav aria-label="主导航">{page_nav}</nav></div></header><main id="main" class="shell">{body}</main><footer><div class="shell"><a class="logo" href="/" aria-label="翻墙排行首页"><span class="logo-mark" aria-hidden="true"><i></i><i></i><i></i></span><span>翻墙<b>排行</b><small>FANQIANGPAIHANG</small></span></a><p>读懂套餐，再做选择。价格资料有日期，测试结论有依据。</p><div class="footer-links"><a href="/about/">关于本站</a><a href="/methodology/">排行与测评方法</a><a href="/disclosure/">推广关系说明</a><a href="/sitemap/">网站地图</a></div><p>© 2026 翻墙排行 · fanqiangpaihang.wiki · 资料整理于 {DATE}</p><button id="motion-toggle" class="motion-button" type="button" aria-pressed="false">暂停背景动画</button></div></footer><a class="top-link" href="#main" aria-label="返回页面顶部">↑ 顶部</a></body></html>'''
    target=DIST/path.lstrip('/')/'index.html' if path.endswith('/') else DIST/path.lstrip('/')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(document,encoding='utf-8')
    pages.append({'path':path,'title':title,'description':desc})
def card(url,title,desc,label='选购研究'):return f'<a class="card" href="{url}"><span class="label">{E(label)}</span><h3>{E(title)}</h3><p>{E(desc)}</p></a>'
def brandcard(b):return brand_card(b,price)
def sources(bs):
    return '<h2>资料来源与范围</h2>'+para('本页套餐摘自站长指定参考博客，读取于2026-10-09；原记录日期见表。来源记录的检查日期不等于本站已实测或已核验当前在售状态。计算基于已记录金额与明确容量，优惠不计入价格。')+'<ul>'+''.join(f'<li><a href="https://jichangnetwork.blog/brands/{b["id"]}/" target="_blank" rel="noopener noreferrer">机场网络 · {E(b["name"])}资料页</a>；原页列示来源：<a href="{E(b["source"])}" target="_blank" rel="noopener noreferrer">{E(b["sourceLabel"])}</a>（原来源未由本站逐一重新验证）</li>' for b in bs)+'</ul>'
def article_page(a):
    toc='<p class="article-deck">'+E(a['desc'])+'</p>'
    related=''.join(card('/articles/'+x['slug']+'/',x['title'],x['desc'],x['cat']) for x in articles if x['slug']!=a['slug'] and set(x.get('brands',[]))&set(a.get('brands',[])))
    if not related:related=''.join(card('/articles/'+x['slug']+'/',x['title'],x['desc'],x['cat']) for x in articles[:3])
    else:
        # Use a bounded related set, preserving whole card markup.
        xs=[x for x in articles if x['slug']!=a['slug'] and set(x.get('brands',[]))&set(a.get('brands',[]))][:3]
        related=''.join(card('/articles/'+x['slug']+'/',x['title'],x['desc'],x['cat']) for x in xs)
    if a['slug'] in EXTRAS:
        xs=[x for x in articles if x['slug'] in EXTRAS[a['slug']]['related']]
        related=''.join(card('/articles/'+x['slug']+'/',x['title'],x['desc'],x['cat']) for x in xs)
    body=f'<div class="crumb"><a href="/articles/">文章</a> / {E(a["cat"])}</div><article class="article"><span class="eyebrow">{E(a["cat"])}</span><h1>{E(a["title"])}</h1><div class="meta">翻墙排行编辑资料组 · {DATE} · {a["read"]} 分钟阅读 · 资料分析</div>{toc}{a["body"]}<h2>本页结论的使用边界</h2>{para("本文为套餐资料分析或测评方法指南。本站未开展独立账户测速，不对稳定性、解锁率、运营持续性作实测保证。购买时请核对当前套餐与结算条件。")}</article><section class="section"><h2>继续阅读</h2><div class="grid">{related}</div></section>'
    page('/articles/'+a['slug']+'/',a['title'],a['desc'],body,'Article',a)

articles=[]
def add(slug,title,desc,body,cat,bs=[]):
    title=title.replace('机场机场','机场')
    text=re.sub('<[^>]+>','',body)
    articles.append(dict(slug=slug,title=title,desc=desc,body=body,cat=cat,brands=[b['id'] for b in bs],read=max(3,math.ceil(len(text)/450))))

for b in brands:
    n=b['name']; ps=monthly(b); profile=b['profile']; valid=b['id'] not in excluded
    body=section('先读懂这个品牌的容量阶梯',f'{n}的套餐资料覆盖'+ '、'.join(f"{p['gb']:g}GB" for p in ps)+'等月额度。本文把付款金额、明确流量和升级差额列在同一口径下；它们只描述套餐成本，不是速度和稳定性的证据。')+table(b,[p for p in b['plans'] if p['cycle']=='月付'])
    if ps and valid:
        p=ps[0]; body+=section('入门档的成本与适用边界',f"已记录的明确容量入门档为{money(p['price'])}元、{p['gb']:g}GB，标称成本约{p['price']/p['gb']:.3f}元/GB。若一个周期只消耗额度的一半，实际消耗成本约{p['price']/(p['gb']/2):.3f}元/GB。两者差别来自未使用的额度，而不是另一种报价。选择时先看总付款是否在预算内，再看容量能否覆盖真实任务。")
        for lo,hi in zip(ps,ps[1:]):
            delta=hi['gb']-lo['gb']
            if delta>0:body+=section(f"从{lo['gb']:g}GB到{hi['gb']:g}GB的升级代价",f"按参考金额比较，从{money(lo['price'])}元升级到{money(hi['price'])}元，多付{money(hi['price']-lo['price'])}元取得{delta:g}GB新增额度，边际成本约{(hi['price']-lo['price'])/delta:.3f}元/GB。若原档已经足够，这笔新增付款不会仅因平均单价更低而变成必要。此计算不代表面板支持当期补差价，升级结算方式需另行确认。")
    else:body+=section('为什么不输出购买起价',f"{n}的套餐归属或运营资料存在未解决的问题。这里保留参考价目供核对，但不把它们转成当前可购买报价，也不参与便宜榜。确认面板名称、对应套餐与当前服务状态后，才恢复成本比较。")
    body+=section('这个品牌需要优先确认的字段',profile['tradeoff']+' '+b['note'])+section('把计算落实到选择',profile['verifyInsight']+' 记录完整周期消耗与临时加购，再判断是否需要上档。规则不明确时先保存问题，而不要从套餐名称推断权益。')+sources([b])
    add(b['id']+'-monthly',n+'月付套餐分析：容量阶梯与升级成本',f'逐项对照{n}月付金额、流量口径与新增容量成本，保留套餐资料差异。',body,'套餐成本',[b])

    other=[p for p in b['plans'] if p['cycle']!='月付']
    body=section('付款频率与流量周期是两个字段',f'{n}的非月付记录有{len(other)}项。年付描述一次支付的周期，一次性包描述独立付款；是否刷新、如何计量，需要读每一项的容量口径。不能把年付金额折算成可以逐月购买的低价。')+table(b,other)
    for p in other:
        if p['cycle']=='年付':
            meaning=f"{money(p['price'])}元是一次年付总额，按十二个月资金分摊约{p['price']/12:.2f}元/月；如果只实际使用三个月，付款摊到使用月份约{p['price']/3:.2f}元/月。"
            meaning+= '额度周期尚未明确，不将记录容量当作每月额度，也不参与单位价格计算。' if p.get('quotaPeriod')=='unknown' else f"资料容量口径是{quota(p)}。只有明确每月重置时，才按月需求检验容量；年度总量需要按累计消耗理解。"
        else:meaning=f"参考总付款{money(p['price'])}元，容量口径为{quota(p)}。"+(f"若每月实际消耗20GB，固定消耗情景约需{p['gb']/20:.1f}个月用完。这只是额度除以用量的计算，不是有效期或服务持续时间保证。" if p.get('gb') else '容量未明确，无法推算消耗时间。')
        body+=section(p['name']+'的付款含义',meaning+' '+p.get('quotaNote','')+' 购买前同时核对活动资格、续费价格与剩余余额的处理方式。')
    body+=section('如何在周期包与按量之间选择',profile['cycleInsight']+' 先写明预计使用的月份与累计消耗；分别计算所需付款次数和按量包是否覆盖用量。权益不一致时，保留差异，不把两者视为等价替代。')+section('仍需核对的版本边界',profile['tradeoff'])+sources([b])
    add(b['id']+'-cycles',n+'付款周期解析：年付、按量与额度重置',f'分析{n}的非月付记录，区分总付款、资金分摊与实际流量周期。',body,'付款周期',[b])

    body=section('这是一份资料评估',f'{n}在本站品牌库按站长顺序收录为第{b["rank"]}项。这个序号描述收录顺序，不是实测评分。参考资料列示线路为“{b["line"]}”，该字段是来源口径，本站没有通过独立账户验证线路、速度或可用性。')+section('已知资料与需要确认的内容',profile['verifyInsight']+' '+b['note'])+section('容量和预算能回答哪些问题',profile['monthlyInsight']+' 成本分析可以用于缩小候选范围，但不能回答晚高峰是否稳定、能否完成具体平台任务或客服实际响应速度。')
    body+=section('针对这个品牌的测试记录设计',f"如果准备测试{n}，先记录购买套餐、容量版本、节点、客户端、运营商与接入方式。在常用时段对同一个真实任务多次观察，记录日期、任务次数、失败次数及恢复时间。{profile['tradeoff']} 测试前先解决这个资料问题，避免用不一致的版本比较。")
    body+=section('不同宣传需要对应的证据','速度描述需要测量工具、服务器和单位；稳定性需要多个日期的任务记录；平台支持需要具体平台、节点地区和操作结果。只打开首页不能证明所有内容可用，单次峰值也不能代表整个周期。没有对应记录的字段统一保留未测。')+section('优惠与入口状态',f"本次{'收录优惠码 '+b['coupon'] if b['coupon'] else '未提供该品牌优惠码'}。代码未进行结算验证，不在测评中加分，不从代码名称推断折扣。品牌入口由站长提供，带推荐代码，可能产生推广收益。")+section('资料评估结论',f"{n}可作为需要进一步核对的候选。当前能支持的结论是套餐结构与版本差异，无法支持稳定率、解锁率或实测速率排名。{'归属或运营状态问题解决之前，不将参考价目作为购买建议。' if not valid else '先确认当前套餐，再用短周期观察自身任务是否满足需求。'}")+sources([b])
    has_report=test_records[b['id']]['status']!='not_collected'
    if has_report:
        body=body.replace('当前能支持的结论是套餐结构与版本差异，无法支持稳定率、解锁率或实测速率排名。','本页新增有出处的第三方测速摘录，反映原报告测试条件下的观测；仍无法支持长期稳定率、解锁率或跨品牌速度排名。')
    add(b['id']+'-review',n+('机场测评：第三方测速记录与套餐核对' if has_report else '机场测评资料评估：证据边界与测试清单'),f'整理{n}的'+('公开第三方测速、测试条件、图片来源与局限；本站未亲测。' if has_report else '套餐疑点、线路资料与测试方法；明确当前没有独立测速记录。'),body,'测评研究',[b])

for idx,a in enumerate(brands):
    b=brands[(idx+1)%len(brands)]; ap=monthly(a); bp=monthly(b)
    body=section('对照范围与版本',f"本页对照{a['name']}与{b['name']}已记录的明确容量月付套餐。不同品牌的名称、线路描述和推荐名次不参与金额计算。参考资料读取于{DATE}，当前在售金额、节点权限和设备条款需购买前确认。")+f'<h2>{E(a["name"])}月付记录</h2>'+table(a,[p for p in a['plans'] if p['cycle']=='月付'])+f'<h2>{E(b["name"])}月付记录</h2>'+table(b,[p for p in b['plans'] if p['cycle']=='月付'])
    if a['id'] not in excluded and b['id'] not in excluded:
        aa=ap[0]; bb=bp[0]
        body+=section('入门付款与容量关系',f"{a['name']}明确容量入门档{money(aa['price'])}元、{aa['gb']:g}GB；{b['name']}对应参考入门档{money(bb['price'])}元、{bb['gb']:g}GB。两者付款差额的绝对值为{abs(aa['price']-bb['price']):g}元，容量差额的绝对值为{abs(aa['gb']-bb['gb']):g}GB。标称成本分别约{aa['price']/aa['gb']:.3f}与{bb['price']/bb['gb']:.3f}元/GB。总付款较低与单位成本较低可能是不同结果，选择应先满足自己的容量需求。")
        for need in [80,200,500]:
            ax=next((p for p in ap if p['gb']>=need),None); bx=next((p for p in bp if p['gb']>=need),None)
            text=f"假设每周期需求为{need}GB，且两品牌流量倍率和权益已经核对为可比："
            text+=f"{a['name']}已记录最低满足容量的档位为{money(ax['price'])}元、{ax['gb']:g}GB；" if ax else f"{a['name']}没有可直接匹配的明确容量记录；"
            text+=f"{b['name']}对应为{money(bx['price'])}元、{bx['gb']:g}GB。" if bx else f"{b['name']}没有可直接匹配的明确容量记录。"
            if ax and bx:text+=f"按这个用量计算，实际消耗成本分别约{ax['price']/need:.3f}与{bx['price']/need:.3f}元/GB。该情景未计优惠，也不说明任务体验相同。"
            body+=section(f'{need}GB需求情景',text)
    else:body+=section('为什么暂停价格胜负结论',f"{a['name']}或{b['name']}存在品牌归属、运营状态待确认项。参考表可以用于询问服务方，但不应据此判断谁是当前可购买的低价选择。先解决身份与版本，再恢复成本对照。")
    body+=section('需要分别确认的关键问题',f"{a['name']}：{a['profile']['tradeoff']} {b['name']}：{b['profile']['tradeoff']}")+section('如何把对照变成决定','确定你的预算上限、每周期用量和设备需求，先排除不满足硬条件的档位。对剩余候选采用一致任务与本地网络观察，记录失败和重试。金额表只能支持预算选择，不能代替稳定性与兼容性验证。')+sources([a,b])
    add(a['id']+'-vs-'+b['id'],a['name']+'与'+b['name']+'对比：入门成本与三种用量',f'按80GB、200GB、500GB情景对照{a["name"]}与{b["name"]}月付档位，保留证据差异。',body,'品牌对比',[a,b])

guides=json.loads((ROOT/'guides.json').read_text(encoding='utf-8'))
assert len(guides)==34,len(guides)
for g in guides:
    body=''.join(section(t,s) for t,s in g['sections'])
    body+=focused_guide(g['slug'],brands,monthly,excluded)
    body+=extra_guide(g['slug'],{x['slug']:x['title'] for x in guides})
    if g['slug']=='latency-throughput':body+='<p>方法参考：<a href="https://blog.cloudflare.com/how-does-cloudflares-speed-test-really-work/" target="_blank" rel="noopener noreferrer">Cloudflare · 网络质量测试方法</a></p>'
    add(g['slug'],g['title'],g['sections'][0][1][:110],body,'选购指南')
assert len(articles)==150
revise(articles,brands,monthly,excluded,test_records,price_audit)

for b in brands:
    links=''.join(card('/articles/'+a['slug']+'/',a['title'],a['desc'],a['cat']) for a in articles if b['id'] in a['brands'] and a['cat']!='品牌对比')
    coupon=f'<p>站长提供优惠码：<strong>{E(b["coupon"])}</strong> <button data-copy="{E(b["coupon"])}" type="button">复制优惠码</button></p><p id="copy-status" aria-live="polite"></p>' if b['coupon'] else '<p>本次未提供优惠码。</p>'
    features=''
    for p in b['plans']:
        if p.get('features'):features+='<details><summary>'+E(p['name'])+' · 来源列示的服务说明</summary><ul>'+''.join('<li>'+E(s)+'</li>' for s in p['features'])+'</ul><p class="meta">以上为来源描述，未由本站独立实测验证。</p></details>'
    body=f'<div class="crumb"><a href="/brands/">品牌库</a> / {E(b["name"])}</div><section class="hero"><div><div class="eyebrow">BRAND {b["rank"]:02} / {E(b["english"])}</div><h1>{E(b["name"])}</h1><p>{E(b["profile"]["headline"])}</p><a class="button" href="{E(b["url"])}" target="_blank" rel="sponsored noopener noreferrer">前往站长提供的官网入口</a></div><aside><strong>{E(price(b))}</strong><p>参考价目 · 非当前报价保证</p>{coupon}<p class="meta">优惠码尚未结算验证；链接带推荐代码，可能产生推广收益。</p></aside></section><div class="notice">{E(b["note"])} 本站未进行独立测速，以下为套餐资料与分析。</div><section class="section"><h2>套餐与流量档案</h2>{table(b)}{features}</section><div class="article">{section("付款方式与容量含义",b["profile"]["cycleInsight"])}{section("月付成本观察",b["profile"]["monthlyInsight"])}{section("版本差异与购买核对",b["profile"]["tradeoff"]+" "+b["profile"]["verifyInsight"])}{section("线路与测评状态","参考线路描述："+b["line"]+"。本站没有独立账户测试记录，延迟、吞吐、晚高峰任务成功率与平台可用性均未测。不使用虚构评分或测速数字。")}{sources([b])}</div><section class="section"><h2>品牌专题阅读</h2><div class="grid">{links}</div></section>'
    body=body.replace('<section class="section"><h2>套餐与流量档案</h2>',brand_brief(b,monthly,excluded)+'<section class="section"><h2>套餐与流量档案</h2>',1)
    page('/brands/'+b['id']+'/',b['name']+'套餐价格、流量与测评资料',f'{b["name"]}品牌档案：完整套餐记录、付款周期、流量口径、优惠信息与版本核对说明。',body)

topicdefs=[('recommended','机场推荐排行 1–10','站长给定顺序','按站长提供的前十名排列，代表站长推荐顺序，不是独立测速排名。',brands[:10]),('budget','便宜机场严选排行 1–10','参考月付金额排序','按每品牌明确容量的最低参考月付金额升序；同价按站长收录顺序。排除Firefly、极连云的套餐归属疑点及可信云的运营待核实记录。历史活动和小包仍需确认在售。',sorted([b for b in brands if b['id'] not in excluded and monthly(b)],key=lambda b:(monthly(b)[0]['price'],b['rank']))[:10]),('stable','稳定机场严选候选 1–10','待测名单 · 非稳定性实测排名','目前没有一致条件的独立测试记录，因此按站长前十推荐顺序展示待测候选。序号不代表稳定性优劣；完成多日任务、失败记录与恢复时间观察后才能发布实测排名。',brands[:10])]
for slug,title,label,intro,bs in topicdefs:
    rows=''.join(f'<div class="row"><span class="rank">{i+1:02}</span><div><h3><a href="/brands/{b["id"]}/">{E(b["name"])} {E(b["english"])}</a></h3><span class="meta">{E(b["profile"]["headline"])}</span></div><div>{E(price(b))}<br><span class="meta">{"稳定性证据待补充" if slug=="stable" else "参考资料 · 当前在售需复核"}</span></div><a class="button" href="/brands/{b["id"]}/">查看档案</a></div>' for i,b in enumerate(bs))
    related=[a for a in articles if a['slug'] in ('ranking-method','stable-shortlist','test-design','gb-cost','monthly-budget','comparison-workflow')]
    body=f'<div class="crumb"><a href="/topics/">严选专题</a> / {E(title)}</div><section class="hero"><div><div class="eyebrow">{E(label)}</div><h1>{E(title)}</h1><p>{E(intro)}</p></div><aside><strong>01–10</strong><p>读懂名次的依据，再核对自己的需求。</p><a href="/methodology/">查看完整排行方法</a></aside></section><section>{rows}</section><section class="section"><h2>专题阅读</h2><div class="grid">'+''.join(card('/articles/'+a['slug']+'/',a['title'],a['desc'],a['cat']) for a in related)+'</div></section>'
    page('/topics/'+slug+'/',title,title+'。'+intro,body,'CollectionPage')
topiccards=topic_cards()
page('/topics/','机场推荐专题：推荐、便宜与稳定严选','三个排行专题，分别公开站长推荐、参考价格与待测候选的编排依据。','<section class="section"><div class="eyebrow">THE SHORTLIST</div><h1>严选专题</h1><div class="grid">'+topiccards+'</div></section>','CollectionPage')
page('/brands/','29个机场品牌库：套餐价格与流量档案','按站长给定顺序收录29个品牌，查看套餐、流量周期、优惠码与测评资料。','<section class="section"><div class="eyebrow">BRAND DIRECTORY</div><h1>品牌库</h1><p>29个品牌，按站长给定顺序收录。每个入口都有独立套餐档案。</p><div class="brand-list">'+''.join(brandcard(b) for b in brands)+'</div></section>','CollectionPage')
for a in articles:article_page(a)
for pnum in range(1,11):
    path='/articles/' if pnum==1 else f'/articles/page/{pnum}/'
    selected=articles[(pnum-1)*15:pnum*15]
    pagination='<nav class="pagination" aria-label="文章分页">'+''.join(f'<a class="{"active" if n==pnum else ""}" '+('aria-current="page" ' if n==pnum else '')+f'href="{"/articles/" if n==1 else f"/articles/page/{n}/"}">{n:02}</a>' for n in range(1,11))+'</nav>'
    page(path,f'机场推荐与梯子选购文章 · 第{pnum}页',f'第{pnum}页收录15篇套餐研究、付款分析、品牌对比与选购指南，全文静态可读取。','<section class="section"><div class="eyebrow">THE JOURNAL</div><h1>文章 · 深入读懂选择</h1><p>150篇资料研究与指南 · 套餐成本 29 / 付款周期 29 / 测评研究 29 / 品牌对比 29 / 选购指南 34</p><div class="grid">'+''.join(card('/articles/'+a['slug']+'/',a['title'],a['desc'],a['cat']+' / '+str(a['read'])+'分钟') for a in selected)+'</div>'+pagination+'</section>','CollectionPage')
page('/coupons/','机场优惠码汇总：11个品牌的站长提供代码','收录11个品牌优惠码，支持复制；适用套餐、资格与有效期以结算为准。','<section class="section"><div class="eyebrow">COUPON NOTES</div><h1>优惠码</h1><div class="notice">以下代码由站长提供，未逐一结算验证。未确认有效期、折扣与适用范围，不将代码计入榜单价格。</div><p id="copy-status" aria-live="polite"></p><div class="grid">'+''.join(f'<article class="card"><h2><a href="/brands/{b["id"]}/">{E(b["name"])}</a></h2><p><strong>{E(b["coupon"])}</strong></p><button type="button" data-copy="{E(b["coupon"])}">复制优惠码</button><p>输入后核对最终订单金额，首购与续费规则分别确认。</p></article>' for b in brands if b['coupon'])+'</div></section>')
page('/about/','关于翻墙排行：资料整理与编辑原则','了解翻墙排行的内容范围、编辑方式与资料边界。','<article class="article"><h1>关于翻墙排行</h1>'+section('内容范围','本站围绕梯子推荐与机场推荐整理品牌套餐、流量周期、预算计算与测评方法。品牌顺序和推广入口由站长提供，套餐参考资料来自站长指定博客机场网络。')+section('内容如何制作','文章由AI辅助完成资料整理和计算，采用公开来源、明确公式与证据边界，不虚构专家身份、账户体验或测速记录。每页提供适用范围，站长可在获得新价目与原始测试记录后修订。')+section('资料时间','本次读取参考资料的日期为2026-10-09。套餐原记录日期保留在各表中。读取旧资料不等于当前报价核验，本站不以新的页面日期掩盖原数据时间。')+'</article>')
page('/methodology/','排行与机场测评方法：价格、排序和证据口径','公开推荐榜、便宜榜与稳定候选名单的规则，以及成本计算与未知字段处理方式。','<article class="article"><h1>排行与测评方法</h1>'+''.join(section(title,intro) for slug,title,label,intro,bs in topicdefs)+section('金额与容量计算','标称每GB成本等于周期总付款除以同周期明确GB；实际消耗成本等于付款除以实际用量；升级边际成本等于价差除以新增容量。年付除以十二仅为资金分摊，不能写成可购买月付价。容量不明、内部冲突、身份或运营待核实项不参与计算。')+section('测评证据','本站当前没有独立账户测试，所有品牌实测速率、延迟、稳定性与平台可用性均为未测。来源服务宣传只作为来源描述。未来实测需记录环境、任务、日期、样本次数、失败事件与恢复时间。')+section('版本控制','原始参考资料保存在项目data目录，展示资料保留容量冲突与活动提示。新数据应更新来源日期、文章与榜单，不静默合并不同版本最低字段。')+'</article>')
page('/disclosure/','推广关系说明：品牌链接与推荐码','公开本站跳转链接的推荐关系及其与测评结论的区别。','<article class="article"><h1>推广关系说明</h1>'+section('链接关系','品牌库使用站长提供的带推荐代码链接。通过这些链接注册或购买，站长可能取得推广收益。链接按原始提供值保存，本站不声称已认证全部入口身份。')+section('排序关系','机场推荐与品牌库按站长给定顺序排列。便宜榜按公开参考金额规则排列。稳定严选展示待测候选，不是已完成的实测结果。推广收益不构成服务质量证据。')+section('优惠与价格','优惠码由站长提供，未完成结算验证。套餐价格采用参考资料，当前在售、资格和条款请在付款前确认。本站不把宣传内容变成实测结论。')+'</article>')
home=home_layout(brands,articles,price)
home=home.replace('<div class="facts-strip">','<div class="compare-promo"><div><span class="eyebrow">COMPARE / 同需求比较</span><h2>把两个品牌放在一起看。</h2><p>按预算和月用量对照完整付款、容量余量与资料依据。</p></div><a class="button" href="/compare/">打开品牌比较 →</a><a class="text-link" href="/updates/">查看资料更新记录 →</a></div><div class="facts-strip">',1)
page('/compare/','机场品牌比较工具：按预算、流量与证据对照','选择最多三个机场品牌，按月用量和预算比较历史套餐付款、剩余额度与第三方报告范围。',render_comparison(brands,monthly,excluded),'CollectionPage')
page('/updates/','资料更新与纠错：29个品牌入口核对记录','公开2026-10-10的29个品牌入口读取结果、价格未确认事项、内容更新与资料纠错方式。',render_updates(brands))
(DIST/'assets/compare-data.json').write_text(json.dumps(public_brands(brands,monthly,excluded),ensure_ascii=False),encoding='utf-8')
page('/','梯子推荐与机场推荐：品牌库、严选排行与选购指南','翻墙排行整理29个机场品牌、150篇套餐研究与选购指南，提供机场推荐前十、便宜机场严选和稳定性待测候选。',home)
mapbody='<article class="article"><h1>网站地图</h1><ul>'+''.join(f'<li><a href="{p["path"]}">{E(p["title"])}</a></li>' for p in pages)+'</ul></article>'
page('/sitemap/','翻墙排行网站地图','浏览品牌详情、排行专题与全部150篇文章的链接。',mapbody)
(DIST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{DOMAIN}{p["path"]}</loc><lastmod>{"2026-10-10" if p["path"] in ("/compare/","/updates/","/","/sitemap/","/methodology/") or p["path"].startswith("/brands/") else DATE}</lastmod></url>' for p in pages)+'</urlset>',encoding='utf-8')
(DIST/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+DOMAIN+'/sitemap.xml\n',encoding='utf-8')
(DIST/'404.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>页面未找到｜翻墙排行</title><link rel="stylesheet" href="/assets/style.css"><link rel="stylesheet" href="/assets/editorial.css"><main class="shell"><h1>页面未找到</h1><p>请从品牌库、专题或文章目录继续阅读。</p><a href="/">返回首页</a></main></html>',encoding='utf-8')
(ROOT/'data/brands.json').write_text(json.dumps(brands,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'data/articles.json').write_text(json.dumps(articles,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'data/pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'brands':len(brands),'coupons':len(coupons),'articles':len(articles),'pages':len(pages),'plans':sum(len(b['plans']) for b in brands)},ensure_ascii=True))

article_categories={'/articles/'+a['slug']+'/':a['cat'] for a in articles}
brand_keywords={'/brands/'+b['id']+'/':b['name']+' '+b['english']+' '+b['id'] for b in brands}
search_index=[]
for p in pages:
    category=article_categories.get(p['path'],'品牌资料' if p['path'] in brand_keywords else '排行专题' if p['path'].startswith('/topics/') else '网站栏目')
    search_index.append(dict(p,category=category,keywords=brand_keywords.get(p['path'],'')+' '+next((' '.join(byid[b]['english']+' '+b for b in a['brands']) for a in articles if '/articles/'+a['slug']+'/'==p['path']),'' )))
(DIST/'assets/search.json').write_text(json.dumps(search_index,ensure_ascii=False),encoding='utf-8')
