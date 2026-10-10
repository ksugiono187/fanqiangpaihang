"""Replace generic brand prose with calculations and brand-specific questions."""
import html, math, re

E=lambda x:html.escape(str(x),quote=True)
N=lambda x:f'{x:g}'
P=lambda x:'<p>'+E(x)+'</p>'
S=lambda title,text:'<h2>'+E(title)+'</h2>'+P(text)

def grid(headers,rows):
    return '<div class="table-wrap"><table><thead><tr>'+''.join('<th scope="col">'+E(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+E(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'

def source_note(bs,purpose):
    return '<h2>本页资料出处</h2><ul>'+''.join('<li><a href="https://jichangnetwork.blog/brands/'+b['id']+'/" target="_blank" rel="noopener noreferrer">机场网络 · '+E(b['name'])+'</a>；'+E(purpose)+'所用原记录日期：'+E('、'.join(sorted({p.get('sourceDate','未注明') for p in b['plans']})))+'。</li>' for b in bs)+'</ul><p class="meta"><a href="/methodology/">计算方法及现价核验边界</a> · <a href="/methodology/#price-audit">套餐核对记录</a></p>'

def select(b,monthly,excluded,need):
    if b['id'] in excluded:return None
    return next((p for p in monthly(b) if p['gb']>=need),None)

def monthly_body(b,monthly,excluded):
    name=b['name'];ps=monthly(b);pr=b['profile']
    body=S(pr['monthlyTitle'],pr['monthlyInsight'])
    rows=[]
    for need in (80,200,500):
        p=select(b,monthly,excluded,need)
        rows.append([f'{need}GB/月',p['name'] if p else '暂不匹配',f"¥{N(p['price'])}" if p else '—',f"{N(p['gb']-need)}GB" if p else '—',f"{p['price']/need:.3f}元/实际使用GB" if p else '归属或容量待确认'])
    body+='<h2>80、200、500GB需求的最低参考付款</h2>'+grid(['假设用量','满足额度的参考档','每月总付款','未使用额度','按假设用量摊分'],rows)
    if b['id'] in excluded:
        body+=S(name+'暂不进入预算匹配的原因',pr['tradeoff'])
    elif ps:
        low,high=ps[0],ps[-1]
        body+=S(name+'的起步与上限',f"明确月付记录从{N(low['price'])}元/{N(low['gb'])}GB到{N(high['price'])}元/{N(high['gb'])}GB。表中每一行选的是满足假设用量的最低总付款，不是容量最大的档位；没有满足档时保持空值。")
    changes=[]
    if b['id'] not in excluded:
        for lo,hi in zip(ps,ps[1:]):
            delta=hi['gb']-lo['gb']
            if delta>0:changes.append([f"{N(lo['gb'])} → {N(hi['gb'])}GB",f"¥{N(hi['price']-lo['price'])}",f'{N(delta)}GB',f"{(hi['price']-lo['price'])/delta:.3f}元/GB"])
    if changes:
        body+='<h2>相邻档位增加多少付款</h2>'+grid(['额度变化','新增月付款','新增标称月额度','新增额度成本'],changes)
    body+=S(name+'的版本检查',b['note'])
    body+='<p class="meta">假设倍率1、权益可比；未计优惠。<a href="/methodology/#price-audit">查看计算前提</a>。</p>'
    return body+source_note([b],'月度情景计算')

def cycles_body(b,monthly,excluded):
    name=b['name'];other=[p for p in b['plans'] if p['cycle']!='月付']
    body=S(name+'的非月付方案',b['profile']['cycleInsight'])
    rows=[]
    for p in other:
        period=p.get('quotaPeriod');capacity=p.get('gb') or p.get('quotedGb')
        unit={'month':'每月重置','total':'总额度','year-total':'全年总量','unknown':'刷新口径未知'}.get(period,'待确认')
        rows.append([p['name'],f"¥{N(p['price'])} / {p['cycle']}",f'{N(capacity)}GB · {unit}' if isinstance(capacity,(int,float)) else '容量待确认',f"{p['price']/12:.2f}元/月资金分摊" if p['cycle']=='年付' else '一次付清'])
    body+='<h2>总付款与额度周期逐项记录</h2>'+grid(['参考套餐','一次需付金额','额度口径','付款含义'],rows)
    if not other:body+=P(name+'本轮没有非月付记录，不用其他品牌的年包规则补齐。')
    payg=[p for p in other if p.get('gb') and p.get('quotaPeriod')=='total']
    rows=[]
    for use in (20,50):
        m=select(b,monthly,excluded,use)
        candidates=[p for p in payg if p['gb']>=use*3] if b['id'] not in excluded else []
        q=min(candidates,key=lambda p:p['price']) if candidates else None
        rows.append([f'{use}GB/月 × 3个月',f"¥{N(m['price']*3)}（{m['name']}三次）" if m else '不能匹配',f"¥{N(q['price'])}（{q['name']}，剩{N(q['gb']-use*3)}GB）" if q else '没有可匹配的单包'])
    body+='<h2>只用三个月，实际要付多少</h2>'+grid(['用量情景','月付总额','满足累计用量的最低单包'],rows)
    yearly=[p for p in other if p['cycle']=='年付']
    if yearly:
        p=min(yearly,key=lambda p:p['price'])
        body+=S(name+'最低年付记录的付款含义',f"{p['name']}的参考年总付款是{N(p['price'])}元。若只用三个月，资金摊分是{p['price']/3:.2f}元/使用月；即使十二个月平均仅{p['price']/12:.2f}元，也不会减少这次必须支付的总额。")
    body+=S('这一品牌的周期疑点',b['profile']['tradeoff'])
    body+='<p class="meta">仅匹配单个总量包。<a href="/methodology/#price-audit">有效期与余额处理需确认</a>。</p>'
    return body+source_note([b],'非月付与短期支出计算')

def review_body(b,records,audit):
    name=b['name'];r=records[b['id']];a=audit[b['id']]
    body=S(name+'测评先回答的问题',b['profile']['verifyInsight'])
    # Kept as the insertion point for the attributed evidence panel.
    body+='<h2>已知资料与需要确认的内容</h2>'+P(b['note'])
    rows=[['套餐对应',b['profile']['tradeoff']],['当前现价',a['currentPriceStatus']],['优惠结算',b['couponStatus']],['本地兼容与任务',name+'没有本站账户任务记录；客户端、设备数和常用平台需分别确认。']]
    body+='<h2>'+E(name)+'的核对优先级</h2>'+grid(['核对项目','现有判断与下一项证据'],rows)
    if r['status']!='not_collected':
        body+=S('公开测速能补充哪些信息',f"{name}已经收录{r['testedNodes']}节点的第三方报告，条件为{r['threads']}线程；日期为{r.get('testedAt') or '不明'}。上方保留少量地区数值与出处。{r['note']}")
    else:
        body+=S('没有数值时如何继续核对',f"{name}暂没有本轮可引用的测速表。首先解决“{b['profile']['evidenceTitle']}”，取得对应套餐后，再记录真实使用的网络、节点、日期与任务结果。")
    body+=S('这份测评仍缺的证据',name+'还缺本站账户下的任务观察，以及当前购买页对“'+b['profile']['evidenceTitle']+'”的完整说明。即使公开报告有速度数值，也不能补足这些缺口。')
    body+='<p>下一步：<a href="/articles/'+b['id']+'-monthly/">查看'+E(name)+'月度用量情景</a>，或<a href="/articles/'+b['id']+'-cycles/">查看付款周期计算</a>；记录方法见<a href="/articles/test-design/">测试设计</a>。</p>'
    return body+source_note([b],'品牌测评资料核对')

def comparison_body(a,b,monthly,excluded,records):
    ap,bp=monthly(a),monthly(b)
    def span(x,ps):
        return x['name']+'有'+str(len(ps))+'档明确月付记录，标称月额度从'+N(ps[0]['gb'])+'到'+N(ps[-1]['gb'])+'GB' if ps else x['name']+'没有可计算的明确月付记录'
    body=S(a['name']+'与'+b['name']+'先比什么',span(a,ap)+'；'+span(b,bp)+'。下面把相同用量下需要支付的金额与剩余额度并排记录。')
    rows=[];differences=[]
    for need in (80,200,500):
        ap=select(a,monthly,excluded,need);bp=select(b,monthly,excluded,need)
        def value(p):return f"¥{N(p['price'])} / {N(p['gb'])}GB · 剩{N(p['gb']-need)}GB" if p else '容量或归属不足，暂不匹配'
        result='暂不能计算'
        if ap and bp:
            delta=abs(ap['price']-bp['price'])
            result='参考总额相同' if delta==0 else (a['name'] if ap['price']<bp['price'] else b['name'])+f'少付{N(delta)}元'
            if delta: differences.append(f'{need}GB需求时，{result}')
        rows.append([f'{need}GB/月',value(ap),value(bp),result])
    body+='<h2>满足同一用量的最低参考付款</h2>'+grid(['假设用量',a['name'],b['name'],'同口径金额差'],rows)
    if a['id'] in excluded or b['id'] in excluded:
        body+=S('这一对为什么不判定价格胜负','；'.join(x['name']+'：'+x['profile']['tradeoff'] for x in (a,b) if x['id'] in excluded))
    elif differences:
        body+=S('用量改变，会改变支出差额','；'.join(differences)+'。金额较低只说明这份历史记录下总付款较少，未计优惠与节点倍率。')
    else:
        body+=S('相同金额时，查看哪些差别',a['profile']['tradeoff']+' '+b['profile']['tradeoff'])
    body+='<h2>两项资料问题分别处理</h2>'+grid(['品牌','优先核对'],[[a['name'],a['profile']['verifyInsight']],[b['name'],b['profile']['verifyInsight']]])
    body+='<h2>测速资料的可比程度</h2>'
    for x in (a,b):
        r=records[x['id']]
        detail=(f"{r.get('testedAt') or '日期不明'}、{r['threads']}线程、{r['testedNodes']}节点的公开报告" if r.get('sourceUrl') else '本轮没有收录可核对数值')
        body+='<p>'+E(x['name']+'：'+detail)+'。<a href="/brands/'+x['id']+'/#public-test">查看来源和条件</a>。</p>'
    body+='<p class="meta">假设倍率1、权益可比；金额差不代表速度差。<a href="/methodology/">查看方法</a>。</p>'
    return body+source_note([a,b],'双品牌同用量比较')

def revise(articles,brands,monthly,excluded,records,audit):
    byid={b['id']:b for b in brands}
    for a in articles:
        bs=[byid[x] for x in a['brands']]
        if a['cat']=='套餐成本':a['body']=monthly_body(bs[0],monthly,excluded)
        elif a['cat']=='付款周期':a['body']=cycles_body(bs[0],monthly,excluded)
        elif a['cat']=='测评研究':a['body']=review_body(bs[0],records,audit)
        elif a['cat']=='品牌对比':a['body']=comparison_body(*bs,monthly,excluded,records)
        a['read']=max(2,math.ceil(len(re.sub('<[^>]+>','',a['body']))/450))

def price_panel(b,r):
    return '<section class="section" id="price-check"><span class="eyebrow">PRICE CHECK</span><h2>套餐核对记录</h2>'+grid(['项目','本轮状态'],[['现价',r['currentPriceStatus']],['原报价日期','、'.join(r['referenceDates'])],['公开入口检查日期',r['reviewedAt'] or '尚未检查'],['本轮检查',r['finding']],['优先待核对',b['profile']['evidenceTitle']]])+'<p class="meta"><a href="/updates/">查看29品牌最新检查记录</a> · <a href="/compare/">进入品牌比较工具</a></p></section>'

def audit_table(brands,audit):
    return '<section class="section" id="price-audit"><h2>套餐核对范围与未解决事项</h2><p>2026-10-10对29个公开入口进行HTTP读取尝试，另通过浏览器查看微风网络、飞猫云与灵动云入口。27个入口返回检测或跳转页面，2个本次未取得可用响应；没有获得当前购买页及结算证据，29品牌仍不标为现价已确认。原始报价日期保留，入口探测结果不作为性能测速。</p>'+grid(['品牌','原报价日期','本轮检查范围'],[[b['name'],'、'.join(audit[b['id']]['referenceDates']),audit[b['id']]['finding']] for b in brands])+'<h2>用量情景和短期付款的计算前提</h2><p>月付匹配只选额度满足需求的最低总付款，假设倍率1、权益可比且额度每月刷新；不计优惠，不默认面板允许补差升级。三个月方案仅匹配单个总量包，不默认可以叠加购买、续费保留余额或退款。有效期和节点权益尚未一致时，金额差不能解释为体验差。</p><p>优惠码需要输入结算页后的金额及适用周期才能确认有效。公开注册页、第三方价格表和入口响应均不替代订单证据。</p></section>'
