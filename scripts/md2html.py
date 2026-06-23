import sys

md_path = sys.argv[1]
html_path = sys.argv[2]

with open(md_path, 'r', encoding='utf-8') as f:
    md_text = f.read()

import markdown

extensions = ['tables', 'fenced_code', 'codehilite', 'extra', 'sane_lists']
body = markdown.markdown(md_text, extensions=extensions)

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Agent 入门：Skills、MCP、规则检查 三大组件</title>
<style>
  :root {{
    --bg: #f8f7f4;
    --card: #ffffff;
    --text: #2c2c2a;
    --muted: #888780;
    --border: #e0ded8;
    --accent: #378ADD;
    --accent-bg: #E6F1FB;
    --green: #1D9E75;
    --green-bg: #E1F5EE;
    --amber: #BA7517;
    --amber-bg: #FAEEDA;
    --purple: #7F77DD;
    --purple-bg: #EEEDFE;
    --red: #E24B4A;
    --red-bg: #FCEBEB;
    --code-bg: #f1efe8;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.8;
    font-size: 15px;
  }}
  .container {{
    max-width: 800px;
    margin: 0 auto;
    padding: 40px 32px 80px;
  }}
  h1 {{
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 8px;
    line-height: 1.4;
  }}
  h2 {{
    font-size: 20px;
    font-weight: 600;
    margin-top: 48px;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1.5px solid var(--border);
  }}
  h3 {{
    font-size: 17px;
    font-weight: 600;
    margin-top: 32px;
    margin-bottom: 12px;
  }}
  h4 {{
    font-size: 15px;
    font-weight: 600;
    margin-top: 24px;
    margin-bottom: 8px;
  }}
  p {{ margin-bottom: 14px; }}
  blockquote {{
    background: var(--card);
    border-left: 3px solid var(--accent);
    padding: 12px 18px;
    margin: 16px 0;
    border-radius: 0 8px 8px 0;
    color: #444441;
  }}
  blockquote p {{ margin-bottom: 6px; }}
  blockquote p:last-child {{ margin-bottom: 0; }}
  strong {{ font-weight: 600; }}
  code {{
    background: var(--code-bg);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 13px;
    font-family: "SF Mono", "Fira Code", "Consolas", monospace;
  }}
  pre {{
    background: #2c2c2a;
    color: #e0ded8;
    padding: 16px 20px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 14px 0;
    font-size: 13px;
    line-height: 1.6;
  }}
  pre code {{
    background: none;
    padding: 0;
    color: inherit;
    font-size: inherit;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 14px;
  }}
  th, td {{
    padding: 10px 14px;
    text-align: left;
    border: 1px solid var(--border);
  }}
  th {{
    background: var(--code-bg);
    font-weight: 600;
    white-space: nowrap;
  }}
  td {{ vertical-align: top; }}
  hr {{
    border: none;
    border-top: 1px solid var(--border);
    margin: 32px 0;
  }}
  ul, ol {{ margin: 10px 0 14px 24px; }}
  li {{ margin-bottom: 4px; }}
  .subtitle {{
    color: var(--muted);
    font-size: 15px;
    margin-bottom: 4px;
  }}
  /* Print */
  @media print {{
    body {{ background: white; font-size: 12px; }}
    .container {{ max-width: 100%; padding: 0 24px; }}
    h2 {{ page-break-before: always; }}
    h2:first-of-type {{ page-break-before: avoid; }}
    pre, code {{ font-size: 10px; }}
    blockquote {{ background: none; }}
  }}
</style>
</head>
<body>
<div class="container">
{body}
</div>
</body>
</html>'''

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Done: {html_path}")
