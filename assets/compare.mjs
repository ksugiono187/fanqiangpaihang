import {matchPlan,candidatePool} from './comparison-core.mjs';
const form=document.getElementById('compare-form'), status=document.getElementById('compare-status'), result=document.getElementById('compare-result');
const usage=document.getElementById('compare-usage'), budget=document.getElementById('compare-budget'), evidence=document.getElementById('compare-evidence'), affordable=document.getElementById('compare-affordable');
const selects=[0,1,2].map(i=>document.getElementById('compare-brand-'+i)),share=document.getElementById('compare-share');
const el=(tag,text)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;return node;};
let brands=[],loaded=false;
function values(){return{usage:Number(usage.value),budget:Number(budget.value)};}
function configure(){
  if(!loaded || !form.checkValidity())return;
  const v=values(),pool=candidatePool(brands,v.usage,v.budget,evidence.value,affordable.checked);
  selects.forEach(select=>{const prior=select.value;select.replaceChildren(new Option('暂不选择',''),...pool.map(b=>new Option(String(b.rank).padStart(2,'0')+' · '+b.name+' '+b.english,b.id)));select.value=pool.some(b=>b.id===prior)?prior:'';});
  return pool;
}
function draw(){
  if(!loaded || !form.reportValidity())return;
  const v=values(),ids=[...new Set(selects.map(s=>s.value).filter(Boolean))],chosen=ids.map(id=>brands.find(b=>b.id===id));
  result.replaceChildren();share.hidden=!chosen.length;
  if(!chosen.length){status.textContent='当前没有选择品牌；请调整筛选条件并选择两个或三个品牌。';return;}
  const matches=chosen.map(b=>matchPlan(b,v.usage,v.budget)),table=el('table'),caption=el('caption',`每月预计使用 ${v.usage}GB · 预算 ¥${v.budget} · 历史参考，不计优惠`);table.append(caption);
  const head=el('thead'),hr=el('tr'),label=el('th','比较项目');label.scope='col';hr.append(label);
  chosen.forEach(b=>{const th=el('th');th.scope='col';const a=el('a',b.name);a.href='/brands/'+b.id+'/';th.append(a);hr.append(th);});head.append(hr);table.append(head);
  const body=el('tbody');
  const rows=[
    ['最低完整月付款',(b,m)=>m.status==='matched'?`¥${m.plan.price} / 月 · ${m.plan.name}`:m.status==='excluded'?'归属或运营待核对，暂不计算':'现有明确月付记录未覆盖'],
    ['标称月容量',(b,m)=>m.plan?m.plan.gb+'GB / 月':'—'],
    ['预算判断',(b,m)=>m.plan?(m.withinBudget?'预算内 · 尚余 ¥'+(-m.difference).toFixed(2):'超出 ¥'+m.difference.toFixed(2)):'无法判断'],
    ['标称剩余额度',(b,m)=>m.plan?m.remaining+'GB':'—'],
    ['按预计用量的成本',(b,m)=>m.plan?'¥'+m.cost.toFixed(3)+' / 实际使用GB':'不计算'],
    ['所选套餐原日期',(b,m)=>m.plan?m.plan.sourceDate:'原记录：'+b.dates.join('、')],
    ['版本重点',b=>b.issue],
    ['当前价格状态',()=> '尚未取得购买页及结算证据；不是现价确认'],
    ['公开入口检查',b=>(b.checked||'未重新检查')+' · '+b.finding],
    ['设备与并发',()=> '尚未获得同版本可确认条款，购买前核对'],
    ['优惠码',b=>b.coupon?b.coupon+' · 尚未结算验证':'本次未提供；不代表品牌没有优惠'],
    ['第三方报告',b=>b.report.status==='not_collected'?'尚未收录':b.report.sourceName+' · '+(b.report.testedAt||'原报告未注明日期')],
    ['本站独立测试',()=> '尚未开展；不生成速度或稳定性评分']
  ];
  rows.forEach(([name,read])=>{const tr=el('tr'),th=el('th',name);th.scope='row';tr.append(th);chosen.forEach((b,i)=>tr.append(el('td',read(b,matches[i]))));body.append(tr);});
  const links=el('tr'),th=el('th','查看完整记录');th.scope='row';links.append(th);chosen.forEach(b=>{const td=el('td'),a=el('a','套餐档案 →');a.href='/brands/'+b.id+'/';td.append(a);if(b.report.sourceUrl){td.append(el('br'));const source=el('a','第三方报告原文 ↗');source.href=b.report.sourceUrl;source.target='_blank';source.rel='noopener noreferrer';td.append(source);}links.append(td);});body.append(links);table.append(body);
  const wrap=el('div');wrap.className='table-wrap compare-table';wrap.tabIndex=0;wrap.setAttribute('role','region');wrap.setAttribute('aria-label','品牌比较表，可用左右方向键查看完整列');wrap.append(table);result.append(wrap);
  const inBudget=matches.filter(m=>m.withinBudget).length;status.textContent=`已比较 ${chosen.length} 个品牌，${inBudget} 个参考档位符合当前用量与预算。`+(chosen.length===1?'可再选择一个品牌作对照。':'')+(selects.filter(s=>s.value).length!==ids.length?'重复选择已合并。':'');
  const query=new URLSearchParams({brands:ids.join(','),usage:String(v.usage),budget:String(v.budget),evidence:evidence.value,affordable:affordable.checked?'1':'0'});history.replaceState(null,'','?'+query.toString());
}
form.addEventListener('submit',e=>{e.preventDefault();draw();});
[usage,budget,evidence,affordable].forEach(control=>control.addEventListener('change',()=>{configure();draw();}));
selects.forEach(s=>s.addEventListener('change',draw));
form.addEventListener('reset',()=>{setTimeout(()=>{evidence.value='all';affordable.checked=false;configure();selects.forEach((s,i)=>s.value=['breezenet','flycat','twilight'][i]);draw();},0);});
share.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href);status.textContent='比较链接已复制，打开链接可恢复品牌、用量、预算与筛选条件。';}catch{status.textContent='复制暂不可用；可复制浏览器地址栏中的比较链接。';}});
try{
  const response=await fetch('/assets/compare-data.json');if(!response.ok)throw Error('data');brands=await response.json();loaded=true;
  const query=new URLSearchParams(location.search);
  const number=(key,input)=>{if(query.has(key)){const value=Number(query.get(key));if(Number.isFinite(value) && value>=Number(input.min) && value<=Number(input.max) && (key!=='usage'||Number.isInteger(value)))input.value=String(value);}};
  number('usage',usage);number('budget',budget);if(['all','report','dated'].includes(query.get('evidence')))evidence.value=query.get('evidence');affordable.checked=query.get('affordable')==='1';
  configure();if(query.has('brands')){const ids=query.get('brands').split(',').slice(0,3);selects.forEach((s,i)=>s.value=ids[i]||'');}draw();
}catch{status.textContent='动态比较暂时不可用，下面保留默认情景；可查看各品牌档案，刷新后重试。';}
