"""Public comparison data and server-rendered fallbacks."""
import html,json
E=lambda s:html.escape(str(s),quote=True)

def public_brands(brands,monthly,excluded):
    return [dict(id=b['id'],name=b['name'],english=b['english'],rank=b['rank'],eligible=b['id'] not in excluded,
        plans=[{k:p[k] for k in ('name','price','gb','sourceDate')} for p in monthly(b)],
        dates=b['priceAudit']['referenceDates'],issue=b['profile']['tradeoff'],coupon=b['coupon'],
        checked=b['priceAudit']['reviewedAt'],finding=b['priceAudit']['finding'],
        report={k:b['thirdPartyTest'].get(k) for k in ('status','sourceName','sourceUrl','testedAt')}) for b in brands]

def render_comparison(brands,monthly,excluded):
    options='<option value="">暂不选择</option>'+''.join('<option value="'+b['id']+'">'+E(f"{b['rank']:02} · {b['name']} {b['english']}")+'</option>' for b in brands)
    picks=''.join('<label>品牌 '+str(i+1)+'<select name="brand'+str(i)+'" id="compare-brand-'+str(i)+'">'+options.replace('value="'+bid+'"','value="'+bid+'" selected')+'</select></label>' for i,bid in enumerate(('breezenet','flycat','twilight')))
    rows=[]
    for b in brands[:3]:
        ps=[p for p in monthly(b) if p['gb']>=200]
        value=f"¥{ps[0]['price']:g} / 月 · {ps[0]['gb']:g}GB" if ps else '未找到覆盖需求的明确档位'
        rows.append('<tr><th scope="row"><a href="/brands/'+b['id']+'/">'+E(b['name'])+'</a></th><td>'+E(value)+'</td><td>'+('预算内' if ps and ps[0]['price']<=30 else '超出预算或待核对')+'</td><td>'+E(b['profile']['tradeoff'])+'</td></tr>')
    fallback='<div class="table-wrap"><table><caption>默认情景：200GB / 月，预算30元；历史参考，不计优惠</caption><thead><tr><th>品牌</th><th>可覆盖需求的最低参考月付</th><th>预算判断</th><th>版本重点</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'
    return '<section class="hero"><div><span class="eyebrow">COMPARE / 品牌比较</span><h1>同一需求，放在一起看。</h1><p>选择最多三个品牌，比较完整付款、容量余量与证据状态。先判断套餐是否匹配，再决定需要补查什么。</p></div><aside><strong>02—03</strong><p>同用量比较 · 保留未知项</p><a href="/updates/">查看最新资料核对记录 →</a></aside></section><section class="section"><form id="compare-form" class="compare-controls"><div class="compare-demand"><label>每月预计使用量（GB）<input id="compare-usage" name="usage" type="number" min="1" max="100000" step="1" value="200" required></label><label>月付预算上限（元）<input id="compare-budget" name="budget" type="number" min="0" max="100000" step="0.01" value="30" required></label><label>候选证据范围<select id="compare-evidence"><option value="all">全部品牌</option><option value="report">已收录第三方报告</option><option value="dated">有日期的第三方报告</option></select></label></div><label class="compare-filter"><input id="compare-affordable" type="checkbox">只在候选列表中显示满足用量、且参考月付不超预算的品牌</label><div class="compare-pickers">'+picks+'</div><div class="compare-actions"><button class="button" type="submit">更新比较</button><button type="reset">恢复默认</button><button id="compare-share" type="button" hidden>复制这组比较链接</button></div></form><p id="compare-status" role="status" aria-live="polite">默认比较微风网络、飞猫云与暮光网络；动态比较加载中。</p><div id="compare-result">'+fallback+'</div><noscript><p>浏览器未启用脚本，已显示默认情景。可进入品牌档案查看完整记录。</p></noscript></section><article class="article"><h2>这些金额怎样得到</h2><p>只选择容量明确、每月刷新的月付记录，按完整付款由低到高找出覆盖需求的档位。Firefly、极连云、可信云因套餐归属或运营疑点不参与金额匹配。剩余额度等于标称月容量减预计使用量；实际使用成本等于该档付款除以预计使用量。</p><p>计算假设倍率为1、权益可比且整月有效，不计优惠、不默认补差升级、也不拼接不同版本。资料原日期保留在结果中，公开入口可达不能确认现价。设备限制和续费条款目前仍需在购买页核对。</p><h2>怎样使用证据筛选</h2><p>“有第三方报告”表示资料已经收录，不表示本站亲测，也不表示报告能证明长期稳定性。无日期的报告与有日期的报告分开；同一来源的多品牌报道不能当成多个独立来源交叉验证。</p><h2>比较之后怎么做</h2><ol><li>先排除不满足用量或预算的档位；没有明确记录的品牌保持待核对。</li><li>进入品牌档案查看原价目日期、容量冲突、报告条件与缺失指标。</li><li>付款前确认当前金额、设备权限、倍率、刷新日及优惠结算；实际体验用自己的任务观察。</li></ol></article><script type="module" src="/assets/compare.mjs"></script>'

def render_updates(brands):
    rows=[]
    for b in brands:
        r=b['priceAudit'];c=r.get('publicCheck',{})
        status='取得公开入口HTML' if c.get('status')==200 else '本次未取得可用响应'
        rows.append('<tr><th scope="row"><a href="/brands/'+b['id']+'/#price-check">'+E(b['name'])+'</a></th><td>'+E(r['reviewedAt'] or '未检查')+'</td><td>'+E(status)+'</td><td>'+E(r['finding'])+'</td><td>尚未确认</td></tr>')
    return '<article class="article"><span class="eyebrow">RESEARCH LOG / 资料更新</span><h1>哪些信息更新了，哪些还未知。</h1><p class="article-deck">2026-10-10 检查了29个站长提供的公开入口。本页按实际检查范围记录结果，历史套餐不因入口检查而变成今日报价。</p><h2>2026-10-10 · 比较工具与入口复查</h2><ul><li>新增最多三个品牌的同用量比较、预算筛选、报告日期筛选和可分享链接。</li><li>29个入口完成HTTP读取尝试；27个返回检测或跳转页面，2个本次未取得可用响应。</li><li>另外通过浏览器查看微风网络、飞猫云与灵动云入口；实际可见页面见下表。</li><li>没有取得当前购买页及结算证据，29个品牌仍不标为现价已确认，11个优惠码仍未结算验证。</li></ul><h2>2026-10-09 · 内容与资料整理</h2><p>扩充34篇选购指南，为29个品牌增加选购摘要；保留150篇文章、188条套餐记录及11份有出处的第三方报告。10份报告有日期，1份未注明日期，未替换为本站实测。</p><h2>本轮29品牌检查记录</h2><p>HTTP读取只观察服务器返回的公开HTML，不执行页面脚本，也没有登录。检测页的“延迟”针对入口目标，不是品牌节点性能测评。一次访问失败不能据此认定停运。</p><div class="table-wrap"><table><thead><tr><th>品牌</th><th>尝试日期</th><th>读取结果</th><th>可确认的范围</th><th>当前价格</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div><h2>怎样补充或纠正资料</h2><p>有效补充应包含品牌名称、公开来源链接、资料日期、完整套餐周期与容量口径；优惠需要结算后的最终金额与资格说明。提交截图前遮挡账户、订阅链接、订单号和付款信息。</p><p><a href="https://github.com/ksugiono187/fanqiangpaihang/issues/new" target="_blank" rel="noopener noreferrer">在公开仓库提交资料纠错 →</a>（需要GitHub账号，反馈会公开）</p><p><a href="/compare/">进入品牌比较工具 →</a> · <a href="/methodology/#price-audit">查看完整价格计算方法 →</a></p></article>'
