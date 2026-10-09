import re, html

def enhance(body, path, is_article):
    esc = lambda s: html.escape(s, quote=True)
    body = body.replace('<div class="table-wrap">', '<div class="table-wrap" tabindex="0" role="region" aria-label="横向数据表，可用左右方向键查看完整列">')
    if is_article:
        headings = []
        def heading(m):
            anchor = 'section-' + str(len(headings) + 1)
            headings.append((anchor, re.sub('<[^>]+>', '', m[1])))
            return '<h2 id="' + anchor + '">' + m[1] + '</h2>'
        body = re.sub(r'<h2>(.*?)</h2>', heading, body, flags=re.S)
        toc = '<details class="article-toc" open><summary>本页目录 · ' + str(len(headings)) + ' 节</summary><nav aria-label="文章目录"><ol>' + ''.join('<li><a href="#' + a + '">' + t + '</a></li>' for a, t in headings) + '</ol></nav></details>'
        body = body.replace('<h2 id="section-1">', toc + '<h2 id="section-1">', 1)
    options = [('all','全部内容'),('品牌资料','品牌资料'),('排行专题','排行专题'),('套餐成本','套餐成本'),('付款周期','付款周期'),('测评研究','测评研究'),('品牌对比','品牌对比'),('选购指南','选购指南')]
    selected = '品牌资料' if path == '/brands/' else 'all'
    opened = ' open' if path == '/brands/' or path == '/articles/' else ''
    search = '<details id="site-search" class="search-panel"' + opened + '><summary>搜索品牌、文章与专题</summary><form id="search-form" role="search"><div class="search-fields"><label for="search-query">关键词<input id="search-query" type="search" placeholder="例如：微风、年付、流量" autocomplete="off"></label><label for="search-category">内容分类<select id="search-category">' + ''.join('<option value="' + esc(v) + '"' + (' selected' if v == selected else '') + '>' + esc(t) + '</option>' for v,t in options) + '</select></label><button type="submit">查找</button></div><p id="search-status" role="status">输入关键词，或选择分类查看内容。结果覆盖全部文章与品牌。</p><div id="search-results" class="grid"></div><button id="search-more" type="button" hidden>显示更多结果</button></form><noscript><p>请使用下方静态目录浏览；搜索需要启用 JavaScript。</p></noscript></details>'
    return search + body
