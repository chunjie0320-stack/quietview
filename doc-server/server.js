const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8899;
const DOCS_DIR = path.join(__dirname, '..', 'data');

// Simple markdown to HTML converter
function mdToHtml(md) {
  let html = md
    // Headers
    .replace(/^#### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Unordered lists
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    // Ordered lists
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // Paragraphs (double newline)
    .replace(/\n\n/g, '</p><p>')
    // Single newlines in non-list context
    .replace(/(?<!<\/li>)\n(?!<)/g, '<br>')
    // Wrap li groups in ul
    .replace(/(<li>.*?<\/li>(\s*<br>)?)+/g, (match) => '<ul>' + match.replace(/<br>/g, '') + '</ul>')
    // Tables
    .replace(/\|(.+)\|/g, (match) => {
      const cells = match.split('|').filter(c => c.trim()).map(c => `<td>${c.trim()}</td>`);
      return `<tr>${cells.join('')}</tr>`;
    });
  
  // Wrap in paragraphs
  html = '<p>' + html + '</p>';
  // Clean up empty paragraphs
  html = html.replace(/<p>\s*<\/p>/g, '');
  // Fix nested tags
  html = html.replace(/<p>(<h[1-6]>)/g, '$1');
  html = html.replace(/(<\/h[1-6]>)<\/p>/g, '$1');
  html = html.replace(/<p>(<ul>)/g, '$1');
  html = html.replace(/(<\/ul>)<\/p>/g, '$1');
  html = html.replace(/<p>(<tr>)/g, '<table>$1');
  html = html.replace(/(<\/tr>)<\/p>/g, '$1</table>');
  
  return html;
}

function getTemplate(title, content) {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${title} - 喵子文档预览</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif; background: #f5f5f5; color: #333; line-height: 1.8; }
  .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px 40px; display: flex; align-items: center; justify-content: space-between; }
  .header h1 { font-size: 20px; } .header .cat { font-size: 24px; }
  .nav { background: white; padding: 10px 40px; border-bottom: 1px solid #e0e0e0; }
  .nav a { color: #667eea; text-decoration: none; margin-right: 15px; font-size: 14px; }
  .nav a:hover { text-decoration: underline; }
  .container { max-width: 900px; margin: 30px auto; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); padding: 40px 50px; }
  h1 { font-size: 28px; margin: 25px 0 15px; color: #1a1a1a; border-bottom: 2px solid #667eea; padding-bottom: 8px; }
  h2 { font-size: 22px; margin: 22px 0 12px; color: #333; }
  h3 { font-size: 18px; margin: 18px 0 10px; color: #555; }
  h4 { font-size: 16px; margin: 15px 0 8px; color: #666; }
  p { margin: 10px 0; }
  ul, ol { margin: 10px 0 10px 25px; }
  li { margin: 4px 0; }
  table { width: 100%; border-collapse: collapse; margin: 15px 0; }
  th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
  th { background: #f0f0f0; font-weight: 600; }
  tr:nth-child(even) { background: #fafafa; }
  strong { color: #d63031; }
  code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 14px; }
  .file-list { list-style: none; padding: 0; }
  .file-list li { padding: 12px 15px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; }
  .file-list li:hover { background: #f8f8ff; }
  .file-list a { color: #333; text-decoration: none; flex: 1; }
  .file-list .date { color: #999; font-size: 13px; margin-left: 10px; }
  .file-list .icon { margin-right: 10px; font-size: 18px; }
  .footer { text-align: center; padding: 20px; color: #999; font-size: 13px; }
</style>
</head>
<body>
<div class="header"><h1>🐱 喵子文档预览</h1><div class="cat">📄</div></div>
<div class="nav"><a href="/">📁 文档列表</a></div>
<div class="container">${content}</div>
<div class="footer">喵子文档预览服务 | 沙箱本地运行</div>
</body></html>`;
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');
  
  if (url.pathname === '/' || url.pathname === '/index') {
    // List all .md files
    const files = [];
    try {
      const entries = fs.readdirSync(DOCS_DIR);
      for (const f of entries) {
        if (f.endsWith('.md')) {
          const stat = fs.statSync(path.join(DOCS_DIR, f));
          files.push({ name: f, mtime: stat.mtime });
        }
      }
    } catch(e) {}
    // Also check memory dir
    const memDir = path.join(__dirname, '..', 'memory');
    try {
      const entries = fs.readdirSync(memDir);
      for (const f of entries) {
        if (f.endsWith('.md')) {
          const stat = fs.statSync(path.join(memDir, f));
          files.push({ name: 'memory/' + f, mtime: stat.mtime });
        }
      }
    } catch(e) {}
    
    files.sort((a, b) => b.mtime - a.mtime);
    
    let listHtml = '<h1>📁 文档列表</h1><ul class="file-list">';
    for (const f of files) {
      const dateStr = f.mtime.toISOString().substring(0, 19).replace('T', ' ');
      listHtml += `<li><span class="icon">📄</span><a href="/doc/${encodeURIComponent(f.name)}">${f.name}</a><span class="date">${dateStr}</span></li>`;
    }
    listHtml += '</ul>';
    
    res.writeHead(200, {'Content-Type': 'text/html; charset=utf-8'});
    res.end(getTemplate('文档列表', listHtml));
    
  } else if (url.pathname.startsWith('/doc/')) {
    const fileName = decodeURIComponent(url.pathname.substring(5));
    let filePath;
    if (fileName.startsWith('memory/')) {
      filePath = path.join(__dirname, '..', fileName);
    } else {
      filePath = path.join(DOCS_DIR, fileName);
    }
    
    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      const html = mdToHtml(content);
      res.writeHead(200, {'Content-Type': 'text/html; charset=utf-8'});
      res.end(getTemplate(fileName, html));
    } catch(e) {
      res.writeHead(404, {'Content-Type': 'text/html; charset=utf-8'});
      res.end(getTemplate('404', '<h1>文档未找到</h1><p>' + fileName + '</p>'));
    }
    
  } else {
    res.writeHead(404);
    res.end('Not Found');
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`🐱 喵子文档预览服务已启动: http://localhost:${PORT}`);
});
