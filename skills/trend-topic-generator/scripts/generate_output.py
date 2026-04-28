#!/usr/bin/env python3
"""
trend-topic-generator — Phase 3: Output Generator
读取分析结果，生成 HTML 可视化 + Markdown 选题卡

逆向保障（输出层）：
  - div depth 自查，depth≠0 自动报错并提示
  - Markdown / HTML 各自独立校验，一个失败不影响另一个
  - 选题数量 <3 时输出警示 banner
  - data_quality 字段透传到输出层，用户可见

Usage:
  python3 generate_output.py --data ~/.openclaw/logs/trends_analysis_xxx.json
  python3 generate_output.py --data <json> --out-dir /path/to/output

Output:
  <out-dir>/topic_report_<industry>_<timestamp>.html
  <out-dir>/topic_cards_<industry>_<timestamp>.md
"""

import argparse
import json
import os
import sys
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--data",    required=True)
parser.add_argument("--out-dir", default=os.path.expanduser("~/.openclaw/workspace"))
args = parser.parse_args()

# ── 读取数据 ──────────────────────────────────────────────────────
with open(args.data, "r", encoding="utf-8") as f:
    data = json.load(f)

meta          = data.get("meta", {})
topics        = data.get("topics", [])
insights      = data.get("insights", {})
data_quality  = data.get("data_quality", {})

industry   = meta.get("industry", "未知行业")
goal       = meta.get("goal", "commercial")
goal_label = "商业化" if goal == "commercial" else "内容型"
ts         = datetime.now().strftime("%Y%m%d_%H%M%S")
safe_ind   = industry.replace(" ", "_").replace("/", "_")

os.makedirs(args.out_dir, exist_ok=True)
html_out = os.path.join(args.out_dir, f"topic_report_{safe_ind}_{ts}.html")
md_out   = os.path.join(args.out_dir, f"topic_cards_{safe_ind}_{ts}.md")

# ── 数据质量摘要（供输出层展示）─────────────────────────────────
dq_total         = data_quality.get("total", "?")
dq_completeness  = data_quality.get("data_completeness", "未知")
dq_has_deep      = data_quality.get("has_deep_content", False)
dq_warnings      = data_quality.get("warnings", [])
dq_retry         = data_quality.get("retry", {})
dq_xhs_status    = data_quality.get("xhs_search", {}).get("status", "unknown")

sources_used = []
cs = data_quality.get("catclaw_search", {})
if cs.get("count", 0) > 0:
    sources_used.append(f"搜索引擎 {cs['count']} 条")
xs = data_quality.get("xhs_search", {})
if xs.get("count", 0) > 0:
    sources_used.append(f"小红书搜索 {xs['count']} 条")
if dq_retry.get("added", 0) > 0:
    sources_used.append(f"扩词补充 {dq_retry['added']} 条")
if dq_has_deep:
    xd = data_quality.get("xhs_deep", {})
    sources_used.append(f"深度帖子 {xd.get('count',0)} 篇（含正文+评论）")

dq_summary_line = "、".join(sources_used) if sources_used else "数据来源未知"

# ── 选题数量检查 ──────────────────────────────────────────────────
low_topic_warning = ""
if len(topics) < 3:
    low_topic_warning = f"⚠️ 选题数量仅 {len(topics)} 个，建议补充「品类方向」或「受众」参数以扩大数据面。"
    print(f"[generate_output] ⚠️ {low_topic_warning}", file=sys.stderr)

# ── Markdown 生成 ─────────────────────────────────────────────────
exit_code_md = 0
try:
    def gen_markdown():
        lines = []
        lines.append(f"# {industry} 热点选题报告 · {goal_label}")
        lines.append(f"\n> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
        if meta.get("season"):    lines.append(f"> 时节：{meta['season']}  ")
        if meta.get("audience"):  lines.append(f"> 受众：{meta['audience']}  ")
        lines.append("")

        # 数据质量说明
        lines.append("## 📊 数据质量")
        lines.append(f"- **数据量**：{dq_total} 条原始数据 — {dq_completeness}")
        lines.append(f"- **来源**：{dq_summary_line}")
        lines.append(f"- **深度内容**：{'有（正文+评论）' if dq_has_deep else '无（仅搜索列表）'}")
        if dq_xhs_status == "cookie_expired":
            lines.append(f"- ⚠️ **注意**：小红书 Cookie 已过期，结果仅来自搜索引擎")
        if dq_retry.get("triggered"):
            lines.append(f"- 🔄 **重试**：{dq_retry.get('reason','')}，补充 {dq_retry.get('added',0)} 条")
        if dq_warnings:
            for w in dq_warnings:
                lines.append(f"- ⚠️ {w}")
        if low_topic_warning:
            lines.append(f"- {low_topic_warning}")
        lines.append("")

        if insights.get("summary"):
            lines.append("## 🔍 整体洞察")
            lines.append(insights["summary"])
            lines.append("")

        lines.append("## 📌 热点选题卡")
        for i, topic in enumerate(topics, 1):
            lines.append(f"\n### {i}. {topic.get('title', '未命名选题')}")
            lines.append(f"**热度信号**：{topic.get('heat_signal', '-')}  ")
            lines.append(f"**数据支撑**：{topic.get('data_support', '-')}  ")
            if goal == "commercial":
                lines.append(f"**商业化方向**：{topic.get('commercial_angle', '-')}  ")
            else:
                lines.append(f"**内容方向**：{topic.get('content_angle', '-')}  ")
            lines.append("**示例标题**：")
            for ex in topic.get("examples", []):
                lines.append(f"- {ex}")

        lines.append("\n---")
        lines.append(f"*数据来源：{dq_summary_line} | 行业：{industry}*")
        return "\n".join(lines)

    md_content = gen_markdown()
    with open(md_out, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[generate_output] ✅ Markdown → {md_out}")
except Exception as e:
    print(f"[generate_output] ❌ Markdown 生成失败: {e}", file=sys.stderr)
    exit_code_md = 1
    md_out = ""

# ── HTML 生成 ─────────────────────────────────────────────────────
exit_code_html = 0
try:
    def topic_to_js(topics):
        items = []
        for i, t in enumerate(topics):
            heat  = t.get("heat_score", 50 + i * 5)
            comm  = t.get("commercial_score", 50)
            diff  = t.get("content_difficulty", 50)
            label = t.get("title", f"话题{i+1}")
            group = t.get("group", "默认")
            items.append(
                f'{{x:{comm},y:{100-diff},r:{max(heat//10,4)},label:{json.dumps(label,ensure_ascii=False)},group:{json.dumps(group,ensure_ascii=False)},heat:{heat}}}'
            )
        return "[" + ",".join(items) + "]"

    topics_js  = topic_to_js(topics)
    cards_json = json.dumps(topics, ensure_ascii=False)
    insight_html = (
        f"<div class='section'><div class='section-title'>💡 整体洞察</div>"
        f"<div class='insight-box'>{insights.get('summary','').replace(chr(10),'<br>')}</div></div>"
        if insights.get("summary") else ""
    )

    # 数据质量 banner HTML
    dq_badge_color = (
        "#e8f5e9" if "充足" in dq_completeness else
        "#fff8e1" if "一般" in dq_completeness else
        "#fce4ec"
    )
    dq_badge_border = (
        "#4caf50" if "充足" in dq_completeness else
        "#ff9800" if "一般" in dq_completeness else
        "#e91e63"
    )
    warning_items_html = "".join(
        f"<li style='color:#c62828'>⚠️ {w}</li>" for w in dq_warnings
    )
    retry_html = (
        f"<li style='color:#1565c0'>🔄 {dq_retry.get('reason','')}，补充 {dq_retry.get('added',0)} 条</li>"
        if dq_retry.get("triggered") else ""
    )
    xhs_expire_html = (
        "<li style='color:#e65100'>⚠️ 小红书 Cookie 已过期，结果仅来自搜索引擎</li>"
        if dq_xhs_status == "cookie_expired" else ""
    )
    low_topic_html = (
        f"<li style='color:#e65100'>{low_topic_warning}</li>" if low_topic_warning else ""
    )

    dq_banner = f"""
    <div class="section" style="background:{dq_badge_color};border-left:4px solid {dq_badge_border}">
      <div class="section-title" style="margin-bottom:8px">📊 数据质量</div>
      <div style="font-size:13px;color:#444;line-height:1.8">
        <strong>数据量</strong>：{dq_total} 条原始数据 &nbsp;·&nbsp; {dq_completeness}<br>
        <strong>来源</strong>：{dq_summary_line}<br>
        <strong>深度内容</strong>：{'有（正文+评论，洞察更准）' if dq_has_deep else '无（仅搜索列表标题）'}
      </div>
      {"<ul style='margin-top:8px;padding-left:0;list-style:none;font-size:12px'>" + xhs_expire_html + retry_html + warning_items_html + low_topic_html + "</ul>" if (xhs_expire_html or retry_html or warning_items_html or low_topic_html) else ""}
    </div>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{industry} 热点选题 · {goal_label}</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'PingFang SC','Noto Sans SC',sans-serif;background:#f7f8fa;color:#1a1a2e}}
  .header{{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:32px 40px}}
  .header h1{{font-size:26px;font-weight:700;margin-bottom:6px}}
  .header p{{opacity:.8;font-size:14px}}
  .container{{max-width:1100px;margin:0 auto;padding:24px 20px}}
  .section{{background:#fff;border-radius:16px;padding:24px;margin-bottom:24px;box-shadow:0 2px 12px rgba(0,0,0,.06)}}
  .section-title{{font-size:16px;font-weight:700;margin-bottom:16px;color:#333;display:flex;align-items:center;gap:8px}}
  #bubble-canvas{{width:100%;height:420px;border-radius:12px;background:#fafbff;border:1px solid #eee}}
  .cards-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}}
  .card{{border:1px solid #eef0f5;border-radius:12px;padding:18px;transition:box-shadow .2s}}
  .card:hover{{box-shadow:0 4px 20px rgba(102,126,234,.15);border-color:#c5caff}}
  .card-num{{font-size:11px;font-weight:700;color:#8b8fa8;margin-bottom:6px;letter-spacing:.5px}}
  .card-title{{font-size:15px;font-weight:700;color:#1a1a2e;margin-bottom:10px;line-height:1.4}}
  .card-tag{{display:inline-block;font-size:11px;padding:2px 8px;border-radius:20px;margin-right:4px;margin-bottom:6px}}
  .tag-heat{{background:#fff0f0;color:#e05555}}
  .tag-data{{background:#f0f7ff;color:#4477cc}}
  .card-desc{{font-size:13px;color:#555;line-height:1.6;margin-bottom:10px}}
  .card-examples{{font-size:12px;color:#888}}
  .card-examples li{{margin-bottom:4px;list-style:none;padding-left:12px;position:relative}}
  .card-examples li::before{{content:"·";position:absolute;left:0;color:#667eea}}
  .insight-box{{background:linear-gradient(135deg,#f8f9ff,#f0f4ff);border-left:4px solid #667eea;padding:16px 20px;border-radius:8px;font-size:14px;line-height:1.7;color:#444}}
  .meta-pills{{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}}
  .pill{{font-size:12px;padding:4px 12px;border-radius:20px;background:rgba(255,255,255,.2);color:#fff;font-weight:600}}
</style>
</head>
<body>
<div class="header">
  <h1>🔥 {industry} 热点选题报告</h1>
  <p>会场目标：{goal_label} &nbsp;·&nbsp; 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
  <div class="meta-pills">
    {"".join(f'<span class="pill">{meta[k]}</span>' for k in ["season","category","audience"] if meta.get(k))}
  </div>
</div>
<div class="container">
  {dq_banner}
  {insight_html}
  <div class="section">
    <div class="section-title">📊 选题热力分布 <span style="font-size:12px;font-weight:400;color:#999">X轴=商业化潜力 / Y轴=传播力 / 气泡大小=热度</span></div>
    <canvas id="bubble-canvas"></canvas>
  </div>
  <div class="section">
    <div class="section-title">📌 热点选题卡（共 {len(topics)} 个）</div>
    <div class="cards-grid" id="cards-grid"></div>
  </div>
</div>
<script>
const TOPICS = {topics_js};
const CARDS  = {cards_json};
const COLORS = ["#667eea","#f093fb","#4facfe","#43e97b","#fa709a","#f6d365"];
(function(){{
  const canvas = document.getElementById('bubble-canvas');
  const dpr = window.devicePixelRatio||1;
  canvas.width  = canvas.offsetWidth*dpr;
  canvas.height = canvas.offsetHeight*dpr;
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr,dpr);
  const W=canvas.offsetWidth,H=canvas.offsetHeight,PAD=50;
  const plotW=W-PAD*2,plotH=H-PAD*2;
  ctx.strokeStyle='#eee';ctx.lineWidth=1;
  for(let i=0;i<=4;i++){{
    const x=PAD+i/4*plotW,y=PAD+i/4*plotH;
    ctx.beginPath();ctx.moveTo(x,PAD);ctx.lineTo(x,H-PAD);ctx.stroke();
    ctx.beginPath();ctx.moveTo(PAD,y);ctx.lineTo(W-PAD,y);ctx.stroke();
  }}
  ctx.fillStyle='#bbb';ctx.font='11px sans-serif';ctx.textAlign='center';
  ctx.fillText('低商业化潜力',PAD,H-10);ctx.fillText('高商业化潜力',W-PAD,H-10);
  ctx.save();ctx.translate(14,H/2);ctx.rotate(-Math.PI/2);ctx.fillText('传播力',0,0);ctx.restore();
  TOPICS.forEach((t,i)=>{{
    const cx=PAD+t.x/100*plotW,cy=PAD+(1-t.y/100)*plotH,r=t.r*6+10;
    const col=COLORS[i%COLORS.length];
    ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);
    ctx.fillStyle=col+'55';ctx.fill();
    ctx.strokeStyle=col;ctx.lineWidth=2;ctx.stroke();
    ctx.fillStyle='#333';ctx.font=`bold ${{Math.min(11,r/1.2)}}px sans-serif`;
    ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(t.label.length>8?t.label.slice(0,8)+'…':t.label,cx,cy);
  }});
}})();
const grid=document.getElementById('cards-grid');
CARDS.forEach((c,i)=>{{
  const col=COLORS[i%COLORS.length];
  const examples=(c.examples||[]).map(e=>`<li>${{e}}</li>`).join('');
  const angle=c.commercial_angle||c.content_angle||'';
  grid.innerHTML+=`
    <div class="card">
      <div class="card-num">选题 ${{String(i+1).padStart(2,'0')}}</div>
      <div class="card-title">${{c.title||'未命名'}}</div>
      <span class="card-tag tag-heat">🔥 ${{c.heat_signal||'热度中'}}</span>
      ${{c.data_support?`<span class="card-tag tag-data">📊 ${{c.data_support}}</span>`:''}}
      ${{angle?`<div class="card-desc" style="margin-top:8px">${{angle}}</div>`:''}}
      ${{examples?`<ul class="card-examples">${{examples}}</ul>`:''}}
    </div>`;
}});
</script>
</body>
</html>"""

    with open(html_out, "w", encoding="utf-8") as f:
        f.write(html)

    # div depth 自查
    depth = 0; max_depth = 0
    for line in html.splitlines():
        depth += line.count('<div') - line.count('</div') - line.count('/>')
        max_depth = max(max_depth, depth)
    print(f"[generate_output] HTML div 自查: max_depth={max_depth}, final_depth={depth}")
    if depth != 0:
        print(f"[generate_output] ❌ div 不平衡 (final_depth={depth})，请检查 HTML", file=sys.stderr)
        exit_code_html = 2
    else:
        print(f"[generate_output] ✅ HTML → {html_out}")

except Exception as e:
    print(f"[generate_output] ❌ HTML 生成失败: {e}", file=sys.stderr)
    exit_code_html = 1
    html_out = ""

# ── 汇报结果 ─────────────────────────────────────────────────────
print(f"\n[generate_output] 输出结果:")
print(f"  HTML: {html_out or '❌ 生成失败'}")
print(f"  MD:   {md_out or '❌ 生成失败'}")
if html_out: print(f"HTML_FILE={html_out}")
if md_out:   print(f"MD_FILE={md_out}")

# 任意一个失败都以非0退出（便于调用方检测）
sys.exit(max(exit_code_html, exit_code_md))
