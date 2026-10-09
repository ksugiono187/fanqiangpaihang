import html

E = lambda value: html.escape(str(value), quote=True)

def grid_table(headers, rows):
    return '<div class="table-wrap"><table><thead><tr>' + ''.join('<th scope="col">' + E(h) + '</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + cell + '</td>' for cell in row) + '</tr>' for row in rows) + '</tbody></table></div>'

def evidence_panel(b, check):
    dates = sorted({p.get('sourceDate', '未注明') for p in b['plans']})
    http = '取得 HTTP 200 响应' if check.get('status') == 200 else '本次未取得可用响应'
    page = check.get('browserObservation', '公开入口为线路检测页；没有取得可核对的完整套餐页。')
    rows = [
        ['入口核对', E(check.get('checkedAt','未检查')) + ' · ' + http],
        ['公开页面观察', E(page)],
        ['套餐原记录日期', E('、'.join(dates))],
        ['当前售价与额度', '尚未逐项核验；下表保留参考记录，不代表今日可购买报价。'],
        ['优惠码', '站长提供，未进行结算验证。' if b.get('coupon') else '本次未提供。'],
        ['速度与稳定性', '没有独立账户测试记录，不能形成实测排名。'],
    ]
    return '<section class="section evidence-panel"><span class="eyebrow">EVIDENCE RECORD</span><h2>本次核对与证据状态</h2>' + grid_table(['核对项目','结果与边界'],rows) + '<p class="meta">入口核对只说明本次网络访问结果。跳转页的 favicon 探测延迟不等于代理节点测速；无法访问也不能单独证明品牌停运。</p></section>'

def candidates(brands, monthly, excluded, need):
    found=[]
    for b in brands:
        if b['id'] in excluded: continue
        eligible=[p for p in monthly(b) if p['gb'] >= need]
        if eligible:
            p=min(eligible,key=lambda p:p['price'])
            found.append((b,p))
    return sorted(found,key=lambda item:(item[1]['price'],item[0]['rank']))

def budget_matrix(brands, monthly, excluded):
    rows=[]
    for need in (80,200,500):
        for b,p in candidates(brands,monthly,excluded,need)[:3]:
            rows.append([str(need)+'GB', '<a href="/brands/'+b['id']+'/">'+E(b['name'])+'</a>', E(p['name']), '¥'+str(p['price'])+' / 月', str(p['gb'])+'GB', E(p.get('sourceDate','未注明'))])
    return '<h2>按标称用量缩小范围：三种需求的资料对照</h2><p>下面每种需求列出参考资料中最低付款的三个候选。条件为明确月付、明确每月额度且标称容量满足需求；同价按站长收录顺序。未纳入优惠、倍率差异、节点权限或未核实的现价，Firefly、极连云、可信云仍因资料疑点排除。这是计算示例，不是服务质量排名。</p>' + grid_table(['每月需求','品牌资料','参考套餐','总付款','标称月额度','原记录日期'], rows) + '<p>使用步骤：先核对当前套餐与倍率，再将满足条件的候选用于同一任务观察。若需要200GB但常用节点按2倍计量，应先估算约400GB面板扣费需求，不能直接套用200GB行。</p>'

def focused_guide(slug, brands, monthly, excluded):
    if slug == 'first-choice':
        return budget_matrix(brands,monthly,excluded) + '<h2>用三个问题完成第一次筛选</h2><ol><li>每次能支付多少？把月付总额与年付总额分开，先排除超出一次付款上限的方案。</li><li>面板实际扣费用量是多少？记录完整周期，并核对倍率、流量刷新时间和是否结转。</li><li>真实任务能否完成？选两个满足预算和额度的候选，用相同设备和接入方式记录任务成功、失败与恢复。</li></ol><p>读完这一页，应得到两项候选和一份待确认事项，而不是仅凭名次下单。</p>'
    if slug == 'monthly-budget':
        rows=[]
        for budget in (15,30,50):
            pool=[(b,p) for b in brands if b['id'] not in excluded for p in monthly(b) if p['price']<=budget]
            if pool:
                b,p=max(pool,key=lambda item:(item[1]['gb'],-item[1]['price'],-item[0]['rank']))
                rows.append(['¥'+str(budget),'<a href="/brands/'+b['id']+'/">'+E(b['name'])+'</a>','¥'+str(p['price'])+' / '+str(p['gb'])+'GB',E(p.get('sourceDate','未注明'))])
        return '<h2>预算上限内的标称容量示例</h2><p>按现有参考记录，在15、30、50元月付上限内分别选出标称额度最大的一个档位；同额度先取低金额，再按站长顺序。仅说明资金与容量关系，不纳入优惠，不代表现价、测速或体验。排除资料归属和运营疑点品牌。</p>'+grid_table(['月付上限','品牌资料','记录金额 / 月额度','原记录日期'],rows)+'<h2>避免为闲置容量增加支出</h2><p>若实际用量只有80GB，预算内最大的容量未必是最合适档位。先选满足80GB且规则清楚的低付款候选，再估计新增任务余量；只有额度持续不足时才提高预算。把每周期付款、消耗、剩余与临时加购四项保存下来。</p>'
    if slug == 'comparison-workflow':
        a=next(b for b in brands if b['id']=='breezenet'); b=next(b for b in brands if b['id']=='flycat'); rows=[]
        for need in (80,200,500):
            row=[str(need)+'GB']
            for brand in (a,b):
                eligible=[p for p in monthly(brand) if p['gb']>=need]
                p=min(eligible,key=lambda p:p['price']) if eligible else None
                row.append(('¥'+str(p['price'])+' / '+str(p['gb'])+'GB；原记录 '+E(p.get('sourceDate','未注明'))) if p else '无明确匹配记录')
            rows.append(row)
        return '<h2>完整示例：微风网络与飞猫云如何逐项对照</h2><p>只比较明确月额度下满足需求的最低参考月付档，假设倍率和权益已核对为可比。金额表不包含优惠，也不能证明任何一个品牌更稳定。</p>'+grid_table(['每月需求','微风网络参考档','飞猫云参考档'],rows)+'<h2>从价目表到两项候选的交付清单</h2><ul><li>预算：一次付款上限、预计使用期限、最低满足额度的档位。</li><li>条款：倍率、重置起点、设备与节点权限，以及退款条件的原文出处。</li><li>观察：相同任务、相同本地条件、样本次数、失败次数、恢复耗时。</li><li>决定：满足了什么条件、额外支付了多少、还有什么未知信息。</li></ul><p>先查看<a href="/brands/breezenet/">微风网络档案</a>与<a href="/brands/flycat/">飞猫云档案</a>的原记录日期；新价目取得后重新计算，而不是沿用旧表决定。</p>'
    if slug == 'ranking-method':
        return '<h2>三张榜单能回答什么</h2>'+grid_table(['榜单','可支持的判断','不能支持的判断'],[['推荐榜','站长指定的推荐阅读顺序。','品牌身份认证、测速分数或实际稳定性优劣。'],['便宜榜','符合筛选条件的历史参考月付金额顺序。','今日可购买最低价、同等权益或所有优惠后的价格。'],['稳定候选','需要进一步测试的候选清单。','已完成稳定性测试或长期服务承诺。']])+'<h2>名次改变需要留下什么记录</h2><p>价格榜至少保存原套餐、旧值、新值、原资料日期和变更依据；稳定榜需要同条件测试记录与事先定义的排序规则。无法核实的新资料先列为待确认，不静默将未知字段转为优势。</p>'
    if slug == 'stable-shortlist':
        return '<h2>稳定性观察记录：先写次数，再写比例</h2>'+grid_table(['字段','记录方式'],[['任务与成功标准','例如完整传输指定测试文件；事先定义超时或中断如何计为失败。'],['日期与窗口','记录每次起止时间，覆盖你实际需要的多个使用日和时段。'],['网络和节点','记录运营商、接入方式、客户端版本与节点；条件改变时另分组。'],['样本与失败','记录总任务数 n 和失败数 f；样本失败比例为 f ÷ n，不外推为全年故障率。'],['恢复耗时','记录异常发生到同一任务恢复的时间；没有恢复样本则保持未记录。']])+'<h2>哪些结果不足以发布稳定排名</h2><p>一次峰值下载、favicon 探测延迟、无日期的截图或只有主观星级，都不足以支持稳定性比较。零失败也应标注样本数和时间范围。候选存在不同测试条件时，先保留分组，不计算统一总分。</p><p><a class="button" href="/assets/test-record-template.txt" download>下载空白测评记录模板</a></p>'
    if slug == 'test-design':
        return '<h2>可以直接执行的三阶段流程</h2><ol><li>准备：保存套餐版本与日期，定义任务和失败标准，记录网络、节点及客户端；不要公开订阅密钥或账户资料。</li><li>观察：在实际使用时段执行同一任务，记录每次起止、结果及异常；换网络或节点时单独标记。</li><li>复盘：按相同条件汇总总次数、失败次数和任务耗时范围，说明观察期限、未知原因和适用边界。</li></ol><h2>发布结论的填写模板</h2><p>“在【日期范围】、【运营商/接入方式】与【套餐/节点】条件下，执行【定义明确的任务】共【n】次，成功【s】次，失败【f】次。结果只适用于上述观察条件；套餐、节点或本地网络变化后需要重新观察。”方括号必须用真实记录替换，未测字段保留未测。</p><p><a class="button" href="/assets/test-record-template.txt" download>下载空白测评记录模板</a></p>'
    return ''
