(function() {
    const editor = document.querySelector('.ProseMirror');
    if (!editor) return 'no editor';
    editor.focus();
    
    const htmlContent = `<h2>一、需求背景</h2>
<h3>1.1 问题描述</h3>
<p>在高达（美团App首页）中，定位组件和Tab组件均具备吸顶功能。当用户向下滑动页面时，两个组件同时进入吸顶状态，导致定位组件与Tab组件在视觉上产生重叠，严重影响用户浏览体验。</p>

<h3>1.2 影响范围</h3>
<ul>
<li>影响线上所有用户的首页浏览体验</li>
<li>活动ID：1013845</li>
<li>优先级：<strong>紧急</strong>（线上BUG）</li>
</ul>

<h2>二、需求详情</h2>
<h3>2.1 现状分析</h3>
<table>
<thead><tr><th>状态</th><th>定位组件</th><th>Tab组件</th><th>表现</th></tr></thead>
<tbody>
<tr><td>正常滚动（未吸顶）</td><td>正常展示</td><td>正常展示</td><td>✅ 无问题</td></tr>
<tr><td>仅Tab吸顶</td><td>正常展示或已滚出视口</td><td>吸顶展示</td><td>✅ 无问题</td></tr>
<tr><td><strong>二者同时吸顶</strong></td><td>吸顶展示</td><td>吸顶展示</td><td>❌ <strong>重叠遮挡</strong></td></tr>
</tbody>
</table>

<h3>2.2 目标方案</h3>
<p><strong>当定位组件和Tab组件同时处于吸顶状态时，隐藏定位组件，仅展示Tab组件。</strong></p>

<h3>2.3 交互逻辑</h3>
<h4>核心规则</h4>
<ol>
<li>页面滚动过程中，实时检测定位组件和Tab组件的吸顶状态</li>
<li><strong>当二者同时吸顶时</strong>：定位组件隐藏（display:none 或 visibility:hidden + height:0），Tab组件正常吸顶展示</li>
<li><strong>当Tab组件退出吸顶状态时</strong>：定位组件恢复展示（如果此时定位组件仍在吸顶区域内）</li>
<li>定位组件的隐藏/显示切换需要平滑过渡，避免页面跳动</li>
</ol>

<h4>状态流转</h4>
<ul>
<li>用户向下滚动 → 定位组件进入吸顶 → 正常展示 → Tab组件也进入吸顶 → 检测到二者同时吸顶 → 隐藏定位组件</li>
<li>用户向上滚动 → Tab组件退出吸顶 → 恢复定位组件展示 → 定位组件退出吸顶 → 恢复正常布局</li>
</ul>

<h3>2.4 边界条件</h3>
<ol>
<li><strong>快速滚动场景</strong>：需确保状态切换不闪烁，建议使用 IntersectionObserver 或 scroll 事件节流处理</li>
<li><strong>定位组件点击态</strong>：如果用户正在操作定位组件（如展开定位选择面板），此时Tab吸顶不应强制隐藏定位组件</li>
<li><strong>不同机型适配</strong>：需在iOS和Android上均验证吸顶状态检测的准确性</li>
</ol>

<h2>三、验收标准</h2>
<table>
<thead><tr><th>#</th><th>验收项</th><th>预期结果</th></tr></thead>
<tbody>
<tr><td>1</td><td>正常滚动（未吸顶）</td><td>定位组件和Tab组件均正常展示</td></tr>
<tr><td>2</td><td>二者同时吸顶</td><td>定位组件隐藏，仅Tab组件吸顶展示</td></tr>
<tr><td>3</td><td>Tab退出吸顶</td><td>定位组件恢复展示</td></tr>
<tr><td>4</td><td>快速滚动</td><td>无闪烁、无跳动</td></tr>
<tr><td>5</td><td>活动ID 1013845</td><td>该活动页面验证通过</td></tr>
</tbody>
</table>

<h2>四、排期建议</h2>
<ul>
<li>预估工作量：0.5-1人日（前端）</li>
<li>建议优先级：P0（线上BUG，影响用户体验）</li>
<li>建议上线时间：本周内hotfix</li>
</ul>`;

    const clipboardData = new DataTransfer();
    clipboardData.setData('text/html', htmlContent);
    
    const pasteEvent = new ClipboardEvent('paste', {
        bubbles: true,
        cancelable: true,
        clipboardData: clipboardData
    });
    
    editor.dispatchEvent(pasteEvent);
    return 'pasted';
})()
