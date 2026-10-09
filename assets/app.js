const make = (tag, text, cls) => { const el = document.createElement(tag); if (text) el.textContent = text; if (cls) el.className = cls; return el; };
document.querySelectorAll('[data-copy]').forEach(b => b.addEventListener('click', async () => { const s = document.getElementById('copy-status'); try { await navigator.clipboard.writeText(b.dataset.copy); s.textContent = '优惠码已复制：' + b.dataset.copy; } catch { s.textContent = '复制不可用，请手动选择优惠码：' + b.dataset.copy; } }));
const form = document.getElementById('search-form');
const searchPanel = document.getElementById('site-search');
const openSearch = () => {
  if (!searchPanel) return;
  searchPanel.open = true;
  document.getElementById('search-query')?.focus({preventScroll: true});
};
document.querySelectorAll('a[href="#site-search"]').forEach(link => link.addEventListener('click', openSearch));
window.addEventListener('hashchange', () => { if (location.hash === '#site-search') openSearch(); });
if (location.hash === '#site-search') openSearch();
const normalizeSearch = value => String(value).normalize('NFKC').toLocaleLowerCase().replace(/\s+/g, ' ').trim();
if (form) {
  const query = document.getElementById('search-query'), category = document.getElementById('search-category'), status = document.getElementById('search-status'), results = document.getElementById('search-results'), more = document.getElementById('search-more');
  let indexPromise, matches = [], visible = 12, revision = 0, timer;
  const render = () => { results.replaceChildren(); matches.slice(0, visible).forEach(p => { const a = make('a', '', 'card'); a.href = p.path; a.append(make('span', p.category, 'label'), make('h3', p.title), make('p', p.description)); results.append(a); }); more.hidden = matches.length <= visible; };
  const search = async () => {
    const current = ++revision;
    const q = normalizeSearch(query.value), cat = category.value;
    status.textContent = '正在查找…';
    try {
      indexPromise ||= fetch('/assets/search.json').then(r => { if (!r.ok) throw new Error('unavailable'); return r.json(); }).catch(e => { indexPromise = null; throw e; });
      const index = await indexPromise;
      if (current !== revision) return;
      const terms = q.split(/\s+/).filter(Boolean);
      matches = index.map(p => {
        const title = normalizeSearch(p.title), keywords = normalizeSearch(p.keywords), description = normalizeSearch(p.description);
        const score = terms.reduce((total, term) => total + (title.includes(term) ? 8 : 0) + (keywords.includes(term) ? 4 : 0) + (description.includes(term) ? 1 : 0), 0) + (q && title === q ? 20 : 0);
        return {page: p, score, matches: (cat === 'all' || cat === p.category) && terms.every(t => (title + ' ' + description + ' ' + keywords).includes(t))};
      }).filter(result => result.matches).sort((a, b) => b.score - a.score).map(result => result.page);
      visible = 12; render(); status.textContent = matches.length ? '找到 ' + matches.length + ' 条结果；当前显示 ' + Math.min(visible, matches.length) + ' 条。' : '没有找到匹配内容，请尝试品牌名、流量或付款周期等关键词。';
    } catch { if (current === revision) status.textContent = '搜索暂时不可用，请使用品牌库、文章分页或网站地图浏览，也可再次点击查找。'; }
  };
  form.addEventListener('submit', e => { e.preventDefault(); clearTimeout(timer); search(); });
  query.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(search, 200); });
  category.addEventListener('change', () => { clearTimeout(timer); search(); });
  more.addEventListener('click', () => { visible += 12; render(); status.textContent = '找到 ' + matches.length + ' 条结果；当前显示 ' + Math.min(visible, matches.length) + ' 条。'; });
}
const motion = document.getElementById('motion-toggle');
if (motion) {
  const apply = paused => { document.body.classList.toggle('motion-paused', paused); motion.setAttribute('aria-pressed', String(paused)); motion.textContent = paused ? '恢复背景动画' : '暂停背景动画'; };
  try { apply(localStorage.getItem('background-paused') === 'true'); } catch { apply(false); }
  motion.addEventListener('click', () => { const paused = motion.getAttribute('aria-pressed') !== 'true'; apply(paused); try { localStorage.setItem('background-paused', String(paused)); } catch {} });
}
