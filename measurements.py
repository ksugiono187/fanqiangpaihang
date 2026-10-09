"""Attributed excerpts of public third-party reports, never first-party tests."""
import html

E=lambda value:html.escape(str(value),quote=True)

def link(url,label):
    return '<a href="'+E(url)+'" target="_blank" rel="noopener noreferrer">'+E(label)+' ↗</a>'

def table(headers,rows):
    return '<div class="table-wrap"><table><thead><tr>'+''.join('<th scope="col">'+E(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'

def report_panel(b,r):
    opening='<section class="section third-party-report" id="public-test"><span class="eyebrow">PUBLIC TEST RECORD</span><h2>第三方测速资料</h2>'
    if r['status']=='not_collected':
        return opening+'<p>本轮未收录可核对的测速数值，速度、延迟与长期稳定性保持未知。'+E(r['scope'])+'</p><p class="meta">整理日期：'+E(r['checkedAt'])+' · <a href="/methodology/#third-party-tests">查看全品牌资料覆盖与引用方法</a></p></section>'
    time=r['testedAt'] or '日期、时段未明确（降低证据完整度）'
    rows=[]
    for v in r['results']:
        rows.append([E(v['region']),E(v['resultNodes']),E(v['tlsMs'])+' ms',f"{v['downloadMBps']:.2f} MB/s",f"{v['downloadMBps']*8:.2f} Mbps"])
    text=opening+'<p class="notice">公开第三方报告摘录 · 来源自称实测，翻墙排行未亲测。测试发生时间与本页整理时间分开记录。</p>'
    text+='<p><strong>测试时间：</strong>'+E(time)+'<br><strong>报告条件：</strong>'+E(r['environment'])+' · '+E(r['tool'])+' · '+str(r['threads'])+'线程 · '+str(r['testedNodes'])+'个地区节点</p>'
    text+='<p>仅摘录香港、美国两组用于观察同次测试内的地区差异。下载和延迟是原报告的地区均值，节点数为取得非零速度 / 参与测试；平均值的分母和异常处理以原报告为准。</p>'
    text+=table(['地区','有数值 / 测试节点','平均 TLS RTT','平均下载（原单位）','单位换算'],rows)
    text+='<p><strong>记录解读：</strong>'+E(r['note'])+'</p>'
    text+='<p>'+link(r['sourceUrl'],r['sourceName']+' · '+b['name']+'原报告')+' · '+link(r['evidenceUrl'],'查看来源测速图片')+'</p>'
    if r.get('sourceConflictUrl'):
        text+='<p class="meta">节点统计口径不同的另一页面：'+link(r['sourceConflictUrl'],'查看59行的另一种表述')+'。同一截图只算一份测试证据。</p>'
    text+='<p class="meta">来源作者：'+E(r['author'])+' · 本站整理：'+E(r['checkedAt'])+'。'+E(r['evidenceReview'])+' '+E(r['affiliation'])+'</p>'
    text+='<p>1 MB/s = 8 Mbps，换算值按原报告已舍入的MB/s计算。没有上传、丢包和连续监控数据；不能推算长期稳定率、物理专线类型、平台解锁或所有用户的实际速度。<a href="/methodology/#third-party-tests">查看引用方法与全部资料覆盖</a>。</p></section>'
    return text

def coverage(brands,records):
    rows=[]
    for b in brands:
        r=records[b['id']]
        state={'dated_report':'有日期的公开报告','undated_report':'图片有数值，日期不明','not_collected':'本轮未收录可核对数值'}[r['status']]
        rows.append(['<a href="/brands/'+b['id']+'/#public-test">'+E(b['name'])+'</a>',E(state),E(r.get('testedAt') or '—'),link(r['sourceUrl'],'原报告') if r.get('sourceUrl') else '待补充'])
    return '<section class="section" id="third-party-tests"><span class="eyebrow">THIRD-PARTY SOURCES</span><h2>公开测速资料覆盖：29个品牌</h2><p>整理于2026-10-09：10个品牌收录有日期的报告，1个品牌收录日期不明的图片报告，其余18个本轮未收录可核对数值。已引用的11份报告来自同一个发布方，不能视为11个独立机构交叉验证。</p><p>引用条件包括对应品牌、可访问报告、工具和网络条件、数值单位及图片出处。来源自称亲测不等于本站认证；仅整理少量数据并链接完整报告。来源的评分、推广判断和长周期承诺不进入本站排行。截图归属和真实性仍有独立核验的局限。</p>'+table(['品牌','证据完整度','原测试时间','来源'],rows)+'<h2>怎样阅读这些数字</h2><p>日期、时段、线程数、套餐和运营商不同，会影响吞吐。9Gbps服务器结果不能当作家庭宽带保证；单线程与32线程不能直接排名。非零结果数不是长期在线率，零速也不证明永久故障。报告中提到的专线和解锁宣传，不能从下载速度反推验证。</p><p>本轮只补充测速参考，保留原有站长推荐顺序与待测稳定候选。新的独立测试取得连续记录后，再按公开方法讨论排行。</p></section>'

def entry_card():
    return '<section class="section"><span class="eyebrow">PUBLIC TEST RECORDS</span><h2>查看有出处的测速资料</h2><p>11个品牌有公开第三方报告摘录：10份标明测试日期，1份日期不明。每份保留测试环境、单位、图片出处和局限。</p><a class="button" href="/methodology/#third-party-tests">查看29个品牌的测速资料覆盖</a></section>'
