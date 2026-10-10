import html
E=lambda s:html.escape(str(s),quote=True)

def identity_panel(record):
    if not record:return ''
    sources=''.join('<li><a href="'+E(s['url'])+'" target="_blank" rel="noopener noreferrer">'+E(s['label'])+'</a> · '+E(s['kind'])+' · '+E(s['date'])+'<br>'+E(s['note'])+'</li>' for s in record['sources'])
    return '<section class="identity-panel section" id="identity-review"><span class="eyebrow">IDENTITY &amp; TERMS / 入口与条款证据</span><h2>'+E(record['headline'])+'</h2><p class="meta">复查日期：'+E(record['checkedAt'])+' · 页面观察与来源陈述分开记录</p><h3>直接观察</h3><p>'+E(record['observation'])+'</p><h3>来源对照与结论</h3><p>'+E(record['finding'])+'</p><ul class="identity-sources">'+sources+'</ul><h3>未解决的购买条件</h3><ul>'+''.join('<li>'+E(x)+'</li>' for x in record['unknown'])+'</ul><p class="identity-next">'+E(record['next'])+'</p><a class="text-link" href="/verification/">查看四项复查与真实测试记录要求 →</a></section>'

def evidence_page(records,brands):
    byid={b['id']:b for b in brands}
    index='<nav class="verification-index" aria-label="证据复查导航">'+''.join('<a href="#case-'+r['id']+'">'+E(byid[r['id']]['name'])+'</a>' for r in records)+'</nav>'
    cases=''.join('<div id="case-'+r['id']+'"><h2 class="case-brand"><a href="/brands/'+r['id']+'/#identity-review">'+E(byid[r['id']]['name'])+' →</a></h2>'+identity_panel(r).replace('id="identity-review"','').replace('<a class="text-link" href="/verification/">查看四项复查与真实测试记录要求 →</a>','')+'</div>' for r in records)
    testing='<section class="section" id="first-party-plan"><span class="eyebrow">FIRST-PARTY RECORDS / 独立测试</span><h2>独立测试状态：尚未执行</h2><p>当前没有可用测试账号或该品牌节点连接，因此没有第一方速度、丢包、任务成功率或恢复时间结果。下方是空白采集计划，不能当作已经完成的21组测试。</p><p><a class="button" href="/assets/seven-day-test-plan.csv" download>下载七天空白记录表 ↓</a></p><div class="table-wrap"><table><thead><tr><th>阶段</th><th>实际记录</th><th>可报告的范围</th></tr></thead><tbody><tr><td>测试前</td><td>套餐版本、倍率、运营商、接入、客户端、节点、任务定义</td><td>哪些条件相同，哪些不能直接比较</td></tr><tr><td>七天观察</td><td>每日本地常用、晚高峰、复查窗口；执行次数、失败及恢复</td><td>实际日期与任务样本的结果，缺测单列</td></tr><tr><td>来源保存</td><td>工具、单位、原始文件与脱敏后的证据编号</td><td>可追溯的结果及未覆盖的指标</td></tr></tbody></table></div><p>表中每行均标为“计划未执行”。实际完成后再填真实日期、任务计数与观察结果；未测字段留空。任务失败比例不等同于网络丢包率，七天任务记录也不直接推出全年在线率。</p><p>公开原始资料前遮挡订阅链接、账号、支付信息与订单号；以脱敏文件编号关联证据，不公开账户凭证。</p><p><a href="/articles/test-design/">阅读测评设计指南 →</a> · <a href="/articles/stable-shortlist/">查看稳定性证据要求 →</a></p></section>'
    return '<article class="article"><span class="eyebrow">EVIDENCE REVIEW / 专项复查</span><h1>入口、套餐和体验，需要不同证据。</h1><p class="article-deck">2026-10-10专项复查四个品牌。名称相似、第三方转述和公开注册页分别只能证明有限事实，不合并成当前价格或实测结论。</p>'+index+cases+testing+'</article>'
