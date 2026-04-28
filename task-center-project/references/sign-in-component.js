/* ============================================================
 * renderSignInBlock(persona) — 签到日历组件
 *
 * 返回 HTML 字符串，插入到页面后自动绑定点击交互。
 * 依赖：sign-in-component.css 已加载
 *
 * persona 结构见 SKILL.md 中三个画像定义。
 * ============================================================ */

/**
 * 内联 SVG：白色勾号（已签到态）
 */
function _signSvgCheck() {
  return '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
    + '<path d="M5 12.5L9.5 17L19 7" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
    + '</svg>';
}

/**
 * 内联 SVG：锁形图标（锁定态）
 */
function _signSvgLock() {
  return '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
    + '<rect x="5" y="11" width="14" height="10" rx="2" fill="#CCCCCC"/>'
    + '<path d="M8 11V8a4 4 0 1 1 8 0v3" stroke="#CCCCCC" stroke-width="2" stroke-linecap="round"/>'
    + '</svg>';
}

/**
 * 显示 Toast 提示
 * @param {string} msg - 提示文字
 */
function _signShowToast(msg) {
  /* 复用已有 toast 或创建新的 */
  var toast = document.querySelector('.mu-sign-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.className = 'mu-sign-toast';
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.classList.add('mu-sign-toast--show');
  clearTimeout(toast._timer);
  toast._timer = setTimeout(function () {
    toast.classList.remove('mu-sign-toast--show');
  }, 1500);
}

/**
 * 渲染签到日历组件
 * @param {Object} persona - 画像配置对象
 * @returns {string} HTML 字符串
 */
function renderSignInBlock(persona) {
  var days = persona.signDays;
  var signed = persona.signedCount;
  var todayIdx = signed;           // 0-based：今日待签的索引
  var color = persona.themeColor;
  var uid = 'sign_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);

  /* ---------- 构建签到格 ---------- */
  var daysHtml = '';
  for (var i = 0; i < days; i++) {
    var reward = persona.rewards[i] || '';
    var dayLabel = 'Day' + (i + 1);

    if (i < signed) {
      /* ---- 已签到 ---- */
      daysHtml += ''
        + '<div class="mu-sign-day mu-sign-day--done" style="background:' + color + ';">'
        +   '<span class="mu-sign-day__label">' + dayLabel + '</span>'
        +   '<span class="mu-sign-day__icon">' + _signSvgCheck() + '</span>'
        +   '<span class="mu-sign-day__reward">' + reward + '</span>'
        + '</div>';
    } else if (i === todayIdx) {
      /* ---- 今日待签 ---- */
      daysHtml += ''
        + '<div class="mu-sign-day mu-sign-day--today" '
        +   'style="color:' + color + '; border-color:' + color + ';" '
        +   'data-sign-uid="' + uid + '" data-sign-idx="' + i + '">'
        +   '<span class="mu-sign-day__label">' + dayLabel + '</span>'
        +   '<span class="mu-sign-day__reward">' + reward + '</span>'
        +   '<span class="mu-sign-day__status">' + '今日' + '</span>'
        + '</div>';
    } else {
      /* ---- 未来/锁定 ---- */
      daysHtml += ''
        + '<div class="mu-sign-day mu-sign-day--locked">'
        +   '<span class="mu-sign-day__label">' + dayLabel + '</span>'
        +   '<span class="mu-sign-day__icon">' + _signSvgLock() + '</span>'
        +   '<span class="mu-sign-day__reward">' + reward + '</span>'
        + '</div>';
    }
  }

  /* ---------- 按钮状态 ---------- */
  var allDone = signed >= days;
  var todaySigned = false; // 初始为未签，点击后变更
  var btnClass = 'mu-sign-btn' + (allDone ? ' mu-sign-btn--disabled' : '');
  var btnText = allDone ? persona.btnDoneText : persona.btnText;
  var btnBg = allDone ? '#CCCCCC' : color;

  /* ---------- 组装 HTML ---------- */
  var html = ''
    + '<div class="mu-sign-wrap" style="background:' + persona.themeBg + ';" data-sign-uid="' + uid + '">'
    +   '<p class="mu-sign-title">' + persona.title + '</p>'
    +   '<p class="mu-sign-subtitle">' + persona.subtitle + '</p>'
    +   '<div class="mu-sign-days">' + daysHtml + '</div>'
    +   '<button class="' + btnClass + '" style="background:' + btnBg + ';" data-sign-btn="' + uid + '">'
    +     btnText
    +   '</button>'
    +   '<div class="mu-sign-streak">' + persona.streakText + '</div>'
    + '</div>';

  /* ---------- 延迟绑定交互 ---------- */
  setTimeout(function () {
    _signBindEvents(uid, persona);
  }, 0);

  return html;
}

/**
 * 绑定签到交互事件
 * @param {string} uid  - 组件唯一标识
 * @param {Object} persona - 画像配置
 */
function _signBindEvents(uid, persona) {
  var wrap = document.querySelector('.mu-sign-wrap[data-sign-uid="' + uid + '"]');
  if (!wrap) return;

  /* 今日待签格子 */
  var todayCell = wrap.querySelector('.mu-sign-day--today[data-sign-uid="' + uid + '"]');
  /* 按钮 */
  var btn = wrap.querySelector('[data-sign-btn="' + uid + '"]');

  if (!todayCell || !btn) return;

  /**
   * 执行签到动作
   */
  function doSign() {
    if (todayCell.classList.contains('mu-sign-day--done')) return;

    /* 读取索引（在 DOM 修改前） */
    var idx = persona.signedCount;
    var reward = persona.rewards[idx] || '';

    /* 格子 → 已签到态 */
    todayCell.className = 'mu-sign-day mu-sign-day--done';
    todayCell.style.background = persona.themeColor;
    todayCell.style.color = '#FFFFFF';
    todayCell.style.borderColor = 'transparent';
    todayCell.innerHTML = ''
      + '<span class="mu-sign-day__label">Day' + (persona.signedCount + 1) + '</span>'
      + '<span class="mu-sign-day__icon">' + _signSvgCheck() + '</span>'
      + '<span class="mu-sign-day__reward">' + reward + '</span>';

    /* 按钮 → 已签态 */
    btn.textContent = persona.btnDoneText;
    btn.style.background = '#CCCCCC';
    btn.classList.add('mu-sign-btn--disabled');

    /* 更新连续签到文字 */
    var streak = wrap.querySelector('.mu-sign-streak');
    if (streak) {
      var newCount = persona.signedCount + 1;
      streak.textContent = '\u5DF2\u8FDE\u7EED\u7B7E\u5230 ' + newCount + ' \u5929';
    }

    /* Toast */
    _signShowToast('\u7B7E\u5230\u6210\u529F');
  }

  /* 点击格子触发 */
  todayCell.addEventListener('click', doSign);

  /* 点击按钮也触发 */
  btn.addEventListener('click', function () {
    if (!btn.classList.contains('mu-sign-btn--disabled')) {
      doSign();
    }
  });
}
