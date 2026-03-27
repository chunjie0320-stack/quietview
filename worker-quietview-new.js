// quietview Workers API
// 版本: 1.0.0 - 2026-03-26

const WRITE_TOKEN = 'quietview-write-2026';

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS, DELETE',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Content-Type': 'application/json',
  };
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: corsHeaders(),
  });
}

function checkAuth(request) {
  const auth = request.headers.get('Authorization');
  return auth === `Bearer ${WRITE_TOKEN}`;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // OPTIONS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders() });
    }

    try {
      // ========== GET /api/articles ==========
      if (path === '/api/articles' && request.method === 'GET') {
        const section = url.searchParams.get('section');
        const date = url.searchParams.get('date');

        if (!section || !date) {
          return jsonResponse({ error: 'Missing section or date' }, 400);
        }

        const result = await env.DB.prepare(
          'SELECT * FROM articles WHERE section = ? AND date = ? ORDER BY id ASC'
        ).bind(section, date).all();

        return jsonResponse({ items: result.results, count: result.results.length });
      }

      // ========== GET /api/dates ==========
      if (path === '/api/dates' && request.method === 'GET') {
        const section = url.searchParams.get('section');

        let sections = [];
        if (section === 'daily-brief') {
          sections = ['industry_news', 'industry_voice'];
        } else if (section === 'ai') {
          sections = ['ai_voice', 'ai_product'];
        } else {
          return jsonResponse({ error: 'Invalid section. Use daily-brief or ai' }, 400);
        }

        const placeholders = sections.map(() => '?').join(', ');
        const result = await env.DB.prepare(
          `SELECT DISTINCT date FROM articles WHERE section IN (${placeholders}) ORDER BY date DESC`
        ).bind(...sections).all();

        const dates = result.results.map(r => r.date);
        return jsonResponse({ dates });
      }

      // ========== GET /api/miao-notice ==========
      if (path === '/api/miao-notice' && request.method === 'GET') {
        const date = url.searchParams.get('date');

        if (!date) {
          return jsonResponse({ error: 'Missing date' }, 400);
        }

        const result = await env.DB.prepare(
          'SELECT * FROM miao_notice WHERE date = ? ORDER BY id ASC'
        ).bind(date).all();

        return jsonResponse({ items: result.results, count: result.results.length });
      }

      // ========== GET /api/diary ==========
      if (path === '/api/diary' && request.method === 'GET') {
        const section = url.searchParams.get('section');
        const date = url.searchParams.get('date');

        if (!section) {
          return jsonResponse({ error: 'Missing section' }, 400);
        }

        let query, params;
        if (date) {
          query = 'SELECT * FROM diary WHERE section = ? AND date = ? ORDER BY id ASC';
          params = [section, date];
        } else {
          query = 'SELECT * FROM diary WHERE section = ? ORDER BY date DESC, id ASC';
          params = [section];
        }

        const result = await env.DB.prepare(query).bind(...params).all();
        return jsonResponse({ items: result.results, count: result.results.length });
      }

      // ========== POST /api/articles ==========
      if (path === '/api/articles' && request.method === 'POST') {
        if (!checkAuth(request)) {
          return jsonResponse({ error: 'Unauthorized' }, 401);
        }

        const body = await request.json();
        const { section, date, time_label, tag, title, body: articleBody, source_url } = body;

        if (!section || !date || !title) {
          return jsonResponse({ error: 'Missing required fields: section, date, title' }, 400);
        }

        const result = await env.DB.prepare(
          'INSERT INTO articles (section, date, time_label, tag, title, body, source_url) VALUES (?, ?, ?, ?, ?, ?, ?)'
        ).bind(section, date, time_label || null, tag || null, title, articleBody || null, source_url || null).run();

        return jsonResponse({ success: true, id: result.meta.last_row_id }, 201);
      }

      // ========== POST /api/miao-notice ==========
      if (path === '/api/miao-notice' && request.method === 'POST') {
        if (!checkAuth(request)) {
          return jsonResponse({ error: 'Unauthorized' }, 401);
        }

        const body = await request.json();
        const { date, label, content } = body;

        if (!date || !content) {
          return jsonResponse({ error: 'Missing required fields: date, content' }, 400);
        }

        // Upsert: 同日期则更新
        const existing = await env.DB.prepare(
          'SELECT id FROM miao_notice WHERE date = ?'
        ).bind(date).first();

        if (existing) {
          await env.DB.prepare(
            'UPDATE miao_notice SET label = ?, content = ? WHERE date = ?'
          ).bind(label || null, content, date).run();
          return jsonResponse({ success: true, updated: true, id: existing.id });
        } else {
          const result = await env.DB.prepare(
            'INSERT INTO miao_notice (date, label, content) VALUES (?, ?, ?)'
          ).bind(date, label || null, content).run();
          return jsonResponse({ success: true, created: true, id: result.meta.last_row_id }, 201);
        }
      }

      // ========== POST /api/diary ==========
      if (path === '/api/diary' && request.method === 'POST') {
        if (!checkAuth(request)) {
          return jsonResponse({ error: 'Unauthorized' }, 401);
        }

        const body = await request.json();
        const { date, section, content } = body;

        if (!date || !section || !content) {
          return jsonResponse({ error: 'Missing required fields: date, section, content' }, 400);
        }

        const result = await env.DB.prepare(
          'INSERT INTO diary (date, section, content) VALUES (?, ?, ?)'
        ).bind(date, section, content).run();

        return jsonResponse({ success: true, id: result.meta.last_row_id }, 201);
      }

      // ========== DELETE /api/articles/:id (测试清理用) ==========
      if (path.startsWith('/api/articles/') && request.method === 'DELETE') {
        if (!checkAuth(request)) {
          return jsonResponse({ error: 'Unauthorized' }, 401);
        }

        const id = path.replace('/api/articles/', '');
        await env.DB.prepare('DELETE FROM articles WHERE id = ?').bind(parseInt(id)).run();
        return jsonResponse({ success: true, deleted_id: parseInt(id) });
      }

      // ========== DELETE /api/diary/:id (测试清理用) ==========
      if (path.startsWith('/api/diary/') && request.method === 'DELETE') {
        if (!checkAuth(request)) {
          return jsonResponse({ error: 'Unauthorized' }, 401);
        }

        const id = path.replace('/api/diary/', '');
        await env.DB.prepare('DELETE FROM diary WHERE id = ?').bind(parseInt(id)).run();
        return jsonResponse({ success: true, deleted_id: parseInt(id) });
      }

      // ========== GET / (health check) ==========
      if (path === '/' || path === '/health') {
        return jsonResponse({ status: 'ok', service: 'quietview-api', version: '1.0.0' });
      }

      return jsonResponse({ error: 'Not found' }, 404);

    } catch (err) {
      return jsonResponse({ error: err.message || 'Internal server error' }, 500);
    }
  },
};
