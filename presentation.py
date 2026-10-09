"""Editorial presentation; content, ranking and evidence remain data driven."""
import html
E=lambda value:html.escape(str(value),quote=True)

def brand_card(b, price):
    return f'<a class="brand-card" href="/brands/{b["id"]}/"><span class="brand-number">{b["rank"]:02}</span><span class="brand-name"><strong>{E(b["name"])}</strong><small>{E(b["english"])}</small></span><span class="brand-price">{E(price(b))}<small>参考套餐</small></span><span class="link-arrow" aria-hidden="true">↗</span></a>'

def topic_cards():
    specs=[
        ('recommended','01','机场推荐','从站长推荐的前十品牌开始，逐项查看套餐与资料。','站长推荐顺序'),
        ('budget','02','便宜机场严选','按明确月付记录比较入门支出，先看预算，再看额度。','历史参考价格'),
        ('stable','03','稳定机场候选','查看待测名单与证据缺口，了解稳定性该怎样验证。','候选名单 · 非实测排名'),
    ]
    return ''.join(f'<a class="topic-card" href="/topics/{slug}/"><span class="topic-top"><span>专题 / {number}</span><span aria-hidden="true">↗</span></span><h3>{title}<span>排行 1—10</span></h3><p>{desc}</p><span class="topic-foot">{label}</span></a>' for slug,number,title,desc,label in specs)

def home_layout(brands, articles, price):
    picks=''.join(f'<a class="cover-pick" href="/brands/{b["id"]}/"><span>{b["rank"]:02}</span><div><strong>{E(b["name"])}</strong><small>{E(price(b))}</small></div><i aria-hidden="true">↗</i></a>' for b in brands[:3])
    globe='<svg class="cover-globe" viewBox="0 0 500 500" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width=".7"><circle cx="250" cy="250" r="220"/><ellipse cx="250" cy="250" rx="130" ry="220"/><ellipse cx="250" cy="250" rx="55" ry="220"/><ellipse cx="250" cy="250" rx="220" ry="100"/><ellipse cx="250" cy="250" rx="220" ry="170"/><path d="M30 250H470M250 30V470"/></g></svg>'
    cover=f'<section class="cover">{globe}<div class="cover-copy"><div class="eyebrow">网络选择 · 套餐研究 · 公开资料</div><h1>机场推荐，<br>读懂每一个<span>选择。</span></h1><p>从价格、流量到测评依据。<br>在纷繁的信息中，找到适合自己的梯子。</p><div class="cover-actions"><a class="button" href="/topics/recommended/">查看推荐排行 <span aria-hidden="true">↗</span></a><a class="quiet-link" href="/articles/first-choice/">第一次选购？从这里读起 →</a></div></div><aside class="cover-shortlist"><div class="cover-caption"><span>站长推荐 / 前三</span><small>THE SHORTLIST</small></div>{picks}<p>按站长给定顺序 · 套餐为历史参考</p><a class="cover-all" href="/topics/recommended/">完整推荐榜 <span aria-hidden="true">→</span></a></aside></section>'
    facts='<div class="facts-strip"><div><strong>29</strong><span>品牌档案</span></div><div><strong>150</strong><span>研究与指南</span></div><div><strong>11</strong><span>第三方报告摘录</span></div><a href="/methodology/">公开排序与引用方法 <span aria-hidden="true">↗</span></a></div>'
    topic='<section class="section"><div class="section-head"><div><span class="eyebrow">01 / 严选专题</span><h2>从需求出发</h2></div><a class="text-link" href="/topics/">浏览全部专题 →</a></div><div class="topic-grid">'+topic_cards()+'</div></section>'
    directory='<section class="section"><div class="section-head"><div><span class="eyebrow">02 / 品牌索引</span><h2>推荐前十，逐项读懂</h2></div><a class="text-link" href="/brands/">查看 29 个品牌 →</a></div><p class="section-intro">按站长推荐顺序收录。价格用于理解套餐，当前在售情况请查看各品牌核对记录。</p><div class="brand-list">'+''.join(brand_card(b,price) for b in brands[:10])+'</div></section>'
    chosen=[next(a for a in articles if a['slug']==slug) for slug in ('first-choice','annual-payment','test-design')]
    teasers=[('01','选购入门','先确定需求，<br>再比较套餐。','从一次付款预算、实际用量和常用任务，建立自己的筛选标准。'),('02','付款方式','低月均价，<br>意味着低支出吗？','把年付总额与按月付款分开，理解资金分摊和实际使用成本。'),('03','测评方法','测速数字，<br>应该怎样读？','测试时间、网络条件与工具，都决定了一个数字能回答什么。')]
    cards=''.join(f'<a class="reading-card" href="/articles/{a["slug"]}/"><div class="reading-art"><span>{num}</span><small>{tag}</small><h3>{headline}</h3><i aria-hidden="true">↗</i></div><div class="reading-caption"><span>{E(a["cat"])} · {a["read"]} 分钟阅读</span><h3>{E(a["title"])}</h3><p>{desc}</p></div></a>' for a,(num,tag,headline,desc) in zip(chosen,teasers))
    reading='<section class="section"><div class="section-head"><div><span class="eyebrow">03 / 编辑选读</span><h2>值得读完的几篇</h2></div><a class="text-link" href="/articles/">浏览 150 篇文章 →</a></div><div class="reading-grid">'+cards+'</div></section>'
    scope='<div class="home-scope"><span>资料说明</span><p>本站整理公开资料，未开展独立账户测速。推荐顺序由站长提供，品牌链接可能产生推广收益。<a href="/disclosure/">查看推广关系说明 ↗</a></p></div>'
    groups=[
        ('预算与容量','把套餐金额放回实际用量中比较。','first-choice monthly-budget gb-cost upgrade-cost idle-quota light-usage medium-usage heavy-usage traffic-multiplier'),
        ('付款与购买','理解付款周期、额度和结算条件。','annual-payment payg-basics quota-period low-frequency coupon-validation renewal-price refund-terms purchase-record three-month-budget'),
        ('设备与任务','把设备需求与日常任务写进选择标准。','device-limit client-compatibility peak-hours latency-throughput packet-loss streaming-evidence meeting-tasks backup-plan'),
        ('测评与证据','读懂来源、样本和排名的使用范围。','test-design line-labels source-conflict brand-identity ranking-method review-transparency comparison-workflow stable-shortlist'),
    ]
    lookup={a['slug']:a for a in articles}
    panels=[]
    for i,(name,desc,slugs) in enumerate(groups,1):
        links=''.join(f'<li><a href="/articles/{slug}/"><span>{E(lookup[slug]["title"])}</span><small>{lookup[slug]["read"]} 分钟 <i aria-hidden="true">↗</i></small></a></li>' for slug in slugs.split())
        panels.append(f'<section class="knowledge-group"><div class="knowledge-heading"><span>0{i}</span><div><h3>{name}</h3><p>{desc}</p></div><small>{len(slugs.split())} 篇</small></div><ul>{links}</ul></section>')
    knowledge='<section class="section" id="guide-library"><div class="section-head"><div><span class="eyebrow">04 / 选购知识库</span><h2>把问题读清楚</h2></div><a class="text-link" href="/articles/first-choice/">从选购流程开始 →</a></div><p class="section-intro">34 篇指南，包含情景算例、条件对照与操作清单。按你正在面对的问题进入。</p><div class="knowledge-grid">'+''.join(panels)+'</div></section>'
    studies=[]
    for i,slug in enumerate(('breezenet-monthly','flycat-cycles','twilight-review','breezenet-vs-flycat','worryfree-monthly','stardream-review'),1):
        a=lookup[slug]
        studies.append(f'<a class="research-entry" href="/articles/{slug}/"><span>0{i}</span><div><small>{E(a["cat"])} · {a["read"]} 分钟</small><h3>{E(a["title"])}</h3><p>{E(a["desc"])}</p></div><i aria-hidden="true">↗</i></a>')
    research='<section class="section"><div class="section-head"><div><span class="eyebrow">05 / 品牌研究</span><h2>从档案走到具体分析</h2></div><a class="text-link" href="/articles/">查看全部研究 →</a></div><div class="research-grid">'+''.join(studies)+'</div></section>'
    return '<div class="edition-line"><span>翻墙排行 / 选购与评测资料</span><span>资料整理 · 2026.10</span></div>'+cover+facts+topic+directory+reading+knowledge+research+scope
