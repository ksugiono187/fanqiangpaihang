export function matchPlan(brand, usage, budget) {
  if (!Number.isFinite(usage) || usage <= 0 || !Number.isFinite(budget) || budget < 0) return {status:'invalid'};
  if (!brand.eligible) return {status:'excluded'};
  const plan = brand.plans.filter(p => p.gb >= usage && p.price >= 0).sort((a,b)=>a.price-b.price || a.gb-b.gb)[0];
  if (!plan) return {status:'uncovered'};
  return {status:'matched',plan,remaining:plan.gb-usage,cost:plan.price/usage,withinBudget:plan.price<=budget,difference:plan.price-budget};
}
export function candidatePool(brands,usage,budget,evidence,affordable) {
  return brands.filter(b => (!affordable || matchPlan(b,usage,budget).withinBudget === true) &&
    (evidence==='all' || (evidence==='report' && b.report.status!=='not_collected') || (evidence==='dated' && b.report.status==='dated_report')));
}
