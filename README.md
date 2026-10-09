# 翻墙排行 · fanqiangpaihang.wiki

静态博客首版：29 个品牌、188 条套餐资料、150 篇文章、3 个排行专题、11 个优惠码。全部资料和页面位于本目录。

## 使用

运行 `python build.py` 重新生成 `dist/`。以 `dist/` 为网站根目录部署，支持无需前端 JavaScript读取的静态正文。预览：`python -m http.server 4173 --directory dist`。

## 更新资料

`data/reference-data.json` 为参考站公开资料快照。`build.py` 内 `order` 保存站长品牌顺序，`coupons` 保存本次提供的优惠码。修改套餐源数据后运行生成器。`guides.json` 保存34篇指南原稿。生成后的 `data/brands.json`、`data/articles.json`、`data/pages.json` 是内容索引。

## 内容与证据

29篇套餐成本分析、29篇付款周期分析、29篇测评资料评估、29篇品牌对比、34篇选购指南，共150篇。内容由AI辅助整理，不冒充实测或专家经历。参考站： https://jichangnetwork.blog/ ，读取日期2026-10-09，原套餐记录日期单独保留。

推荐榜按站长顺序。便宜榜按明确容量的最低参考月付金额排序，同价按站长顺序；排除品牌归属或运营状态待核实项。稳定严选是待测候选清单，序号不代表稳定性优劣。当前没有实测账户和测速记录，不提供虚构指标。

## 搜索准备

所有内容页面具备独立TDK、canonical、Open Graph文字元数据、WebPage或Article结构化数据与面包屑。`dist/sitemap.xml` 覆盖200页，`dist/robots.txt` 引用域名下的sitemap。

域名生效且网站公开后，在Bing Webmaster Tools验证域名并提交sitemap。没有生成未经验证的站长验证码或IndexNow密钥。TDK与站点地图不保证搜索收录或关键词排名。

## 动画与可访问性

背景使用低频CSS光线流动。系统开启减少动态效果时自动停用动画。正文使用静态HTML，支持键盘、窄屏、跳到正文与优惠码复制失败提示。

## 部署

用户指定GitHub仓库： https://github.com/ksugiono187/fanqiangpaihang

GitHub Pages可使用 `.github/workflows/pages.yml`，需在仓库设置中选择GitHub Actions为Pages源。域名DNS按最终选择的托管平台设置；不要同时把同一域名指向不同平台。
