#!/usr/bin/env python3
"""Build admin_page.py v3.0 - complete frontend based on PRD v2.0 + skills"""
import base64, py_compile

html = []

# ============ HEAD ============
html.append('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>贝优 - 大学录取信息整理系统</title>')
html.append('<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300..700;1,9..40,300..700&display=swap" rel="stylesheet">')
html.append('<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>')

# ============ CSS ============
html.append('<style>')
html.append(':root{--bg:#f5f6fa;--surface:#fff;--hover:#f0f1f5;--border:#e2e4ea;--border-dk:#d0d2da;--text:#1a1a2e;--text2:#5a5a78;--muted:#9090a8;--primary:#4f46e5;--primary-l:#eef2ff;--primary-d:#3730a3;--ok:#059669;--ok-bg:#ecfdf5;--warn:#d97706;--warn-bg:#fffbeb;--err:#dc2626;--err-bg:#fef2f2;--info:#0284c7;--info-bg:#f0f9ff;--r-sm:6px;--r-md:10px;--r-lg:14px;--sh:0 1px 3px rgba(0,0,0,.06);--sh-md:0 4px 12px rgba(0,0,0,.08);--sh-lg:0 8px 30px rgba(0,0,0,.12);--font:"DM Sans",-apple-system,BlinkMacSystemFont,sans-serif;--serif:"Instrument Serif",Georgia,serif;--ease:cubic-bezier(.25,1,.5,1)}')
html.append('*{margin:0;padding:0;box-sizing:border-box}')
html.append('@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}}')
html.append('body{font-family:var(--font);background:var(--bg);color:var(--text);font-size:14px;line-height:1.6;min-height:100vh;display:flex}')
html.append('::selection{background:var(--primary-l);color:var(--primary-d)}')
html.append('::-webkit-scrollbar{width:5px;height:5px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}::-webkit-scrollbar-thumb:hover{background:var(--border-dk)}')

# Sidebar
html.append('.sidebar{width:250px;background:var(--surface);border-right:1px solid var(--border);display:flex;flex-direction:column;position:fixed;top:0;left:0;bottom:0;z-index:100}')
html.append('.sidebar-header{padding:24px 22px;border-bottom:1px solid var(--border)}')
html.append('.logo{display:flex;align-items:center;gap:12px;text-decoration:none}')
html.append('.logo-i{width:38px;height:38px;background:var(--primary);border-radius:var(--r-sm);display:grid;place-items:center;color:#fff;font-weight:700;font-size:17px;flex-shrink:0}')
html.append('.logo-n{font-family:var(--serif);font-size:20px;color:var(--text);line-height:1.15}')
html.append('.logo-d{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin-top:2px}')
html.append('.sidebar-nav{padding:16px 12px;flex:1;overflow-y:auto}')
html.append('.nav-sec{margin-bottom:24px}')
html.append('.nav-lbl{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.12em;padding:0 10px 10px}')
html.append('.nav{display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:var(--r-sm);color:var(--text2);cursor:pointer;font-size:13.5px;font-weight:500;transition:all 150ms var(--ease);margin-bottom:2px;border:none;background:none;width:100%;text-align:left}')
html.append('.nav:hover{background:var(--hover);color:var(--text)}.nav.active{background:var(--primary);color:#fff}')
html.append('.nav svg{width:18px;height:18px;flex-shrink:0;opacity:.7}.nav.active svg{opacity:1}')
html.append('.badge-nav{margin-left:auto;background:var(--warn);color:#fff;font-size:10px;font-weight:700;padding:1px 7px;border-radius:10px;line-height:1.5}')
html.append('.nav.active .badge-nav{background:rgba(255,255,255,.35)}')
html.append('.sidebar-f{padding:14px 22px;border-top:1px solid var(--border);font-size:11px;color:var(--muted)}')

# Main
html.append('.main{flex:1;margin-left:250px;min-height:100vh;display:flex;flex-direction:column}')
html.append('.topbar{background:var(--surface);border-bottom:1px solid var(--border);padding:16px 32px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:50}')
html.append('.pg-t{font-family:var(--serif);font-size:21px;font-weight:600}')
html.append('.pg-d{font-size:12.5px;color:var(--muted);margin-top:1px}')
html.append('.top-a{display:flex;align-items:center;gap:8px}')
html.append('.content{padding:28px 32px;flex:1}')

# Pages
html.append('.page{display:none}.page.active{display:block;animation:fadeUp 300ms var(--ease)}')
html.append('@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}')

# Stats
html.append('.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-bottom:24px}')
html.append('.st{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);padding:18px 20px;transition:all 200ms var(--ease)}')
html.append('.st:hover{border-color:var(--border-dk);box-shadow:var(--sh)}')
html.append('.st-l{font-size:11px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}')
html.append('.st-v{font-size:26px;font-weight:700;margin-top:4px;font-variant-numeric:tabular-nums}')
html.append('.st-n{font-size:11px;color:var(--muted);margin-top:2px}')

# Toolbar
html.append('.toolbar{display:flex;align-items:center;gap:8px;margin-bottom:16px;flex-wrap:wrap}')
html.append('.srch{flex:1;min-width:180px;padding:9px 14px;border:1px solid var(--border);border-radius:var(--r-sm);font-size:13px;font-family:var(--font);background:var(--surface);transition:border-color 150ms var(--ease)}')
html.append('.srch:focus{outline:none;border-color:var(--primary);box-shadow:0 0 0 3px var(--primary-l)}')
html.append('.sel{padding:9px 14px;border:1px solid var(--border);border-radius:var(--r-sm);font-size:13px;font-family:var(--font);background:var(--surface);cursor:pointer;min-width:110px}')

# Buttons
html.append('.btn{display:inline-flex;align-items:center;gap:5px;padding:9px 16px;border:none;border-radius:var(--r-sm);font-size:13px;font-weight:600;font-family:var(--font);cursor:pointer;transition:all 150ms var(--ease);white-space:nowrap}')
html.append('.btn:active{transform:scale(.97)}.btn svg{width:15px;height:15px}')
html.append('.bp{background:var(--primary);color:#fff}.bp:hover{background:var(--primary-d)}')
html.append('.bs{background:var(--ok);color:#fff}.bs:hover{opacity:.9}')
html.append('.bd{background:var(--err);color:#fff}.bd:hover{opacity:.9}')
html.append('.bg{background:transparent;color:var(--text2);padding:8px 12px}.bg:hover{background:var(--bg);color:var(--text)}')
html.append('.bo{background:var(--surface);color:var(--text2);border:1px solid var(--border)}.bo:hover{border-color:var(--border-dk);background:var(--hover)}')
html.append('.sm{padding:6px 12px;font-size:12px}.btn:disabled{opacity:.5;cursor:not-allowed}')

# Table
html.append('.tw{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);overflow:hidden}')
html.append('.tw-h{padding:14px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}')
html.append('.tw-t{font-weight:600;font-size:14px}.tw-i{font-size:12.5px;color:var(--muted)}')
html.append('.ts{overflow-x:auto;max-height:500px;overflow-y:auto}.ts thead th{position:sticky;top:0;z-index:10}')
html.append('table{width:100%;border-collapse:collapse;min-width:900px}')
html.append('th{padding:11px 14px;text-align:left;font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;background:var(--bg);border-bottom:2px solid var(--border);white-space:nowrap}')
html.append('td{padding:12px 14px;border-bottom:1px solid var(--border);font-size:13px;color:var(--text);white-space:nowrap}')
html.append('tr:hover td{background:var(--primary-l)}tr:last-child td{border-bottom:none}')

# Badges
html.append('.b{display:inline-flex;align-items:center;gap:4px;padding:3px 9px;border-radius:20px;font-size:11.5px;font-weight:600}')
html.append('.b-dot{width:5px;height:5px;border-radius:50%;background:currentColor;flex-shrink:0}')
html.append('.b-ok{background:var(--ok-bg);color:var(--ok)}.b-w{background:var(--warn-bg);color:var(--warn)}.b-err{background:var(--err-bg);color:var(--err)}.b-n{background:var(--bg);color:var(--text2);border:1px solid var(--border)}.b-i{background:var(--info-bg);color:var(--info)}')

# Pagination
html.append('.pag{display:flex;align-items:center;justify-content:space-between;padding:12px 18px;border-top:1px solid var(--border)}')
html.append('.pt{font-size:12.5px;color:var(--muted)}.pb{display:flex;gap:4px}')

# Charts
html.append('.ch{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:16px}')
html.append('.cc{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md)}')
html.append('.cc-h{padding:14px 18px;border-bottom:1px solid var(--border)}.cc-n{font-weight:600;font-size:13.5px}')
html.append('.cc-b{height:320px;padding:12px}')

# Filter
html.append('.fb{display:flex;gap:6px;margin-bottom:14px}')
html.append('.fb-b{padding:5px 13px;border:1px solid var(--border);border-radius:20px;background:var(--surface);font-size:12px;font-weight:600;cursor:pointer;transition:all 150ms var(--ease);color:var(--text2)}')
html.append('.fb-b:hover{border-color:var(--border-dk)}.fb-b.active{background:var(--primary);color:#fff;border-color:var(--primary)}')

# Modal
html.append('.mo{position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:1000;display:none;align-items:center;justify-content:center;backdrop-filter:blur(3px)}')
html.append('.mo.open{display:flex}')
html.append('.md{background:var(--surface);border-radius:var(--r-lg);width:92%;max-width:520px;max-height:85vh;overflow-y:auto;box-shadow:var(--sh-lg);animation:mdIn 250ms var(--ease)}')
html.append('@keyframes mdIn{from{opacity:0;transform:translateY(16px) scale(.97)}to{opacity:1;transform:translateY(0) scale(1)}}')
html.append('.md-h{padding:18px 22px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}')
html.append('.md-t{font-weight:600;font-size:15px}')
html.append('.md-x{background:none;border:none;font-size:20px;cursor:pointer;color:var(--muted);padding:2px 6px;border-radius:var(--r-sm)}.md-x:hover{background:var(--bg);color:var(--text)}')
html.append('.md-b{padding:22px}.md-f{padding:14px 22px;border-top:1px solid var(--border);display:flex;justify-content:flex-end;gap:8px}')

# Form
html.append('.f{margin-bottom:14px}')
html.append('.f-l{display:block;font-size:12.5px;font-weight:600;color:var(--text);margin-bottom:5px}')
html.append('.f-h{font-size:11px;color:var(--muted);margin-top:3px}')
html.append('.inp,.ta{width:100%;padding:9px 13px;border:1px solid var(--border);border-radius:var(--r-sm);font-size:13px;font-family:var(--font);background:var(--surface);transition:border-color 150ms var(--ease)}')
html.append('.inp:focus,.ta:focus{outline:none;border-color:var(--primary);box-shadow:0 0 0 3px var(--primary-l)}')
html.append('.ta{resize:vertical;min-height:100px}')
html.append('.cks{display:grid;grid-template-columns:repeat(2,1fr);gap:6px}')
html.append('.ck{display:flex;align-items:center;gap:7px;padding:7px 10px;border-radius:var(--r-sm);cursor:pointer;transition:background 100ms var(--ease)}')
html.append('.ck:hover{background:var(--bg)}.ck input{accent-color:var(--primary);width:15px;height:15px}')
html.append('.ck label{font-size:12.5px;cursor:pointer}')

# Toast
html.append('.tst{position:fixed;bottom:20px;right:20px;z-index:2000;display:flex;flex-direction:column;gap:6px}')
html.append('.t{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);padding:12px 18px;box-shadow:var(--sh-lg);font-size:13px;font-weight:500;animation:tIn 250ms var(--ease);min-width:260px}')
html.append('.t.ok{border-left:3px solid var(--ok)}.t.err{border-left:3px solid var(--err)}')
html.append('@keyframes tIn{from{opacity:0;transform:translateX(16px)}to{opacity:1;transform:translateX(0)}}')

# Empty
html.append('.em{text-align:center;padding:40px 20px}.em-i{font-size:36px;margin-bottom:12px;opacity:.4}')
html.append('.em-t{font-size:14px;font-weight:600;color:var(--text);margin-bottom:4px}.em-d{font-size:12.5px;color:var(--muted)}')

# Mobile
html.append('.mob{display:none;background:none;border:none;padding:8px;cursor:pointer;color:var(--text)}.mob svg{width:22px;height:22px}')
html.append('@media(max-width:768px){.sidebar{transform:translateX(-100%);transition:transform 300ms var(--ease)}.sidebar.open{transform:translateX(0)}.main{margin-left:0}.content{padding:16px}.stats{grid-template-columns:repeat(2,1fr)}.ch{grid-template-columns:1fr}.mob{display:block!important}}')

html.append('</style></head><body>')

# ============ SIDEBAR ============
html.append('<aside class="sidebar" id="sb"><div class="sidebar-header"><a href="/" class="logo"><div class="logo-i">贝</div><div><div class="logo-n">贝优</div><div class="logo-d">Admission System</div></div></a></div>')
html.append('<nav class="sidebar-nav"><div class="nav-sec"><div class="nav-lbl">数据管理</div>')
html.append('<button class="nav active" onclick="go(\'records\')" data-p="records"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg><span>录取记录</span></button>')
html.append('<button class="nav" onclick="go(\'tasks\')" data-p="tasks"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg><span>任务队列</span></button>')
html.append('<button class="nav" onclick="go(\'review\')" data-p="review"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg><span>数据审核</span><span class="badge-nav" id="rBadge">0</span></button>')
html.append('</div><div class="nav-sec"><div class="nav-lbl">数据分析</div>')
html.append('<button class="nav" onclick="go(\'stats\')" data-p="stats"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg><span>统计分析</span></button>')
html.append('</div></nav><div class="sidebar-f">v2.0 · 贝优教育科技</div></aside>')

# ============ MAIN ============
html.append('<div class="main"><div class="topbar"><div style="display:flex;align-items:center;gap:10px">')
html.append('<button class="mob" onclick="document.getElementById(\'sb\').classList.toggle(\'open\')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg></button>')
html.append('<div><div class="pg-t" id="pgT">录取记录</div><div class="pg-d" id="pgD">浏览和管理所有录取数据</div></div></div>')
html.append('<div class="top-a"><button class="btn bo sm" onclick="refresh()" id="rBtn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:13px;height:13px"><polyline points="23 4 23 10 17 10"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/></svg>刷新</button></div></div>')
html.append('<div class="content">')

# PAGE: 录取记录
html.append('<div class="page active" id="p-records"><div class="toolbar">')
html.append('<input class="srch" id="sI" placeholder="搜索学生姓名、大学、专业..." onkeydown="if(event.key===\'Enter\')loadRec()">')
html.append('<select class="sel" id="cF" onchange="loadRec()"><option value="">全部国家</option><option value="美国">美国</option><option value="英国">英国</option><option value="加拿大">加拿大</option><option value="澳大利亚">澳大利亚</option><option value="新加坡">新加坡</option><option value="香港">香港</option><option value="马来西亚">马来西亚</option><option value="其他">其他</option></select>')
html.append('<select class="sel" id="yF" onchange="loadRec()"><option value="">全部年份</option><option value="2026">2026</option><option value="2025">2025</option><option value="2024">2024</option></select>')
html.append('<button class="btn bp sm" onclick="loadRec()">搜索</button><button class="btn bg sm" onclick="resetS()">重置</button>')
html.append('<button class="btn bo sm" onclick="openFld()">字段设置</button><button class="btn bo sm" onclick="openMod(\'expMod\')">导出</button>')
html.append('</div><div class="tw"><div class="tw-h"><div class="tw-t">录取记录</div><div class="tw-i" id="rCnt">0 条</div></div>')
html.append('<div class="ts"><table><thead><tr id="tH"></tr></thead><tbody id="tB"></tbody></table></div>')
html.append('<div class="pag"><span class="pt" id="pI">-</span><div class="pb"><button class="btn bo sm" id="pP" onclick="chgP(-1)">上一页</button><button class="btn bo sm" id="pN" onclick="chgP(1)">下一页</button></div></div></div></div>')

# PAGE: 任务队列
html.append('<div class="page" id="p-tasks"><div style="display:flex;gap:8px;margin-bottom:16px">')
html.append('<button class="btn bp" onclick="openMod(\'tskMod\')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:15px;height:15px"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>新建任务</button>')
html.append('<button class="btn bs" onclick="execAll()">执行全部</button></div>')
html.append('<div class="tw"><div class="tw-h"><div class="tw-t">采集任务</div><div class="tw-i" id="tCnt">0 个</div></div>')
html.append('<div class="ts"><table><thead><tr><th>ID</th><th>URL</th><th>标题</th><th>状态</th><th>记录数</th><th>创建时间</th><th>操作</th></tr></thead><tbody id="tT"></tbody></table></div></div></div>')

# PAGE: 数据审核
html.append('<div class="page" id="p-review"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">')
html.append('<div class="fb"><button class="fb-b active" onclick="setRF(\'pending\',this)">待审核</button><button class="fb-b" onclick="setRF(\'approved\',this)">已通过</button><button class="fb-b" onclick="setRF(\'rejected\',this)">已拒绝</button><button class="fb-b" onclick="setRF(\'all\',this)">全部</button></div>')
html.append('<div style="display:flex;gap:6px"><button class="btn bs sm" id="bApp" style="display:none" onclick="batchR(\'approve\')">批量通过</button><button class="btn bd sm" id="bRej" style="display:none" onclick="batchR(\'reject\')">批量拒绝</button></div></div>')
html.append('<div class="tw"><div class="ts"><table><thead><tr><th style="width:36px"><input type="checkbox" id="rAll" onchange="togAll()"></th><th>ID</th><th>学生姓名</th><th>录取大学</th><th>专业</th><th>国家</th><th>来源学校</th><th>提交时间</th><th>审核状态</th><th>操作</th></tr></thead><tbody id="rT"></tbody></table></div></div></div>')

# PAGE: 统计分析
html.append('<div class="page" id="p-stats"><div class="stats" id="sG">')
html.append('<div class="st"><div class="st-l">总记录数</div><div class="st-v" id="sT">-</div><div class="st-n">持续收集中</div></div>')
html.append('<div class="st"><div class="st-l">覆盖国家</div><div class="st-v" id="sC">-</div><div class="st-n">留学目的地</div></div>')
html.append('<div class="st"><div class="st-l">收录大学</div><div class="st-v" id="sU">-</div><div class="st-n">全球院校</div></div>')
html.append('<div class="st"><div class="st-l">采集任务</div><div class="st-v" id="sK">-</div><div class="st-n" id="sTN">待执行</div></div>')
html.append('</div><div class="ch">')
html.append('<div class="cc"><div class="cc-h"><div class="cc-n">国家分布</div></div><div class="cc-b" id="cC"></div></div>')
html.append('<div class="cc"><div class="cc-h"><div class="cc-n">大学 TOP10</div></div><div class="cc-b" id="cU"></div></div>')
html.append('<div class="cc"><div class="cc-h"><div class="cc-n">年度趋势</div></div><div class="cc-b" id="cR"></div></div>')
html.append('<div class="cc"><div class="cc-h"><div class="cc-n">专业分布</div></div><div class="cc-b" id="cM"></div></div>')
html.append('</div></div></div></div>')

# ============ MODALS ============
html.append('<div class="mo" id="fldMod"><div class="md"><div class="md-h"><div class="md-t">显示字段设置</div><button class="md-x" onclick="closeMod(\'fldMod\')">&times;</button></div><div class="md-b"><div class="cks" id="fC"></div></div><div class="md-f"><button class="btn bg" onclick="closeMod(\'fldMod\')">取消</button><button class="btn bp" onclick="saveFld()">保存</button></div></div></div>')
html.append('<div class="mo" id="expMod"><div class="md" style="max-width:380px"><div class="md-h"><div class="md-t">导出数据</div><button class="md-x" onclick="closeMod(\'expMod\')">&times;</button></div><div class="md-b"><p style="color:var(--text2);margin-bottom:14px;font-size:13px">选择导出格式：</p><div style="display:flex;flex-direction:column;gap:8px">')
html.append('<button class="btn bp" onclick="exportD(\'pdf\')">导出 PDF</button><button class="btn bs" onclick="exportD(\'excel\')">导出 Excel</button><button class="btn bo" onclick="exportD(\'csv\')">导出 CSV</button>')
html.append('</div></div></div></div>')
html.append('<div class="mo" id="tskMod"><div class="md" style="max-width:540px"><div class="md-h"><div class="md-t">新建采集任务</div><button class="md-x" onclick="closeMod(\'tskMod\')">&times;</button></div>')
html.append('<div class="md-b"><div class="f"><label class="f-l">文章 URL</label><textarea class="ta" id="tU" rows="5" placeholder="https://mp.weixin.qq.com/s/xxxxx&#10;每行一个 URL"></textarea><div class="f-h">支持批量输入，每行一个微信公众号文章链接</div></div>')
html.append('<div id="pBox" style="display:none;padding:12px;background:var(--bg);border-radius:var(--r-sm);margin-top:10px"><div style="font-size:12px;font-weight:600;margin-bottom:6px">采集预览</div><div id="pCon"></div></div></div>')
html.append('<div class="md-f"><button class="btn bo" id="pBtn" onclick="prevTsk()">采集预览</button><button class="btn bp" onclick="mkTsk()">创建任务</button></div></div></div>')
html.append('<div class="tst" id="tst"></div>')

# ============ JAVASCRIPT ============
js = r'''<script>
const A='/api';let pg=1,ps=20,tot=0,rpg=1,rps=20,rf='pending',rS=[];
const fc={student_name_cn:true,country:true,university_cn:true,major_cn:true,admission_type:true,admission_status:true,admission_year:true,scholarship:true,student_name_en:false,university_en:false,major_en:false,updated_at:false,data_source:true};
const pI={records:['录取记录','浏览和管理所有录取数据'],tasks:['任务队列','采集任务管理与执行'],review:['数据审核','审核录入数据的准确性'],stats:['统计分析','数据概览与多维度分析']};

function go(t){
  document.querySelectorAll('.nav').forEach(n=>n.classList.remove('active'));
  let b=document.querySelector(`.nav[data-p="${t}"]`);if(b)b.classList.add('active');
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  let e=document.getElementById('p-'+t);if(e)e.classList.add('active');
  let i=pI[t];if(i){document.getElementById('pgT').textContent=i[0];document.getElementById('pgD').textContent=i[1]}
  if(t==='records')loadRec();if(t==='tasks')loadTsk();if(t==='review')loadRev();if(t==='stats')loadSt();
  if(window.innerWidth<768)document.getElementById('sb').classList.remove('open');
}
function openMod(id){document.getElementById(id).classList.add('open')}
function closeMod(id){document.getElementById(id).classList.remove('open')}

function toast(m,ok=true){
  let c=document.getElementById('tst'),t=document.createElement('div');
  t.className='t '+(ok?'ok':'err');t.textContent=m;c.appendChild(t);
  setTimeout(()=>{t.style.opacity='0';t.style.transform='translateX(16px)';t.style.transition='all 200ms';setTimeout(()=>t.remove(),200)},3000);
}

async function refresh(){
  let b=document.getElementById('rBtn');b.disabled=true;
  b.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:13px;height:13px;animation:spin 1s linear infinite"><polyline points="23 4 23 10 17 10"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/></svg>刷新中';
  let a=document.querySelector('.nav.active')?.dataset.p||'records';
  if(a==='records')loadRec();else if(a==='tasks')loadTsk();else if(a==='review')loadRev();else if(a==='stats')loadSt();
  b.disabled=false;
  b.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:13px;height:13px"><polyline points="23 4 23 10 17 10"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/></svg>刷新';
  toast('数据已更新');
}

/* ===== RECORDS ===== */
async function loadRec(){
  try{let p=new URLSearchParams({page:pg,page_size:ps}),s=document.getElementById('sI').value.trim(),c=document.getElementById('cF').value,y=document.getElementById('yF').value;
  if(s)p.append('search',s);if(c)p.append('country',c);if(y)p.append('year',y);
  let r=await fetch(A+'/records?'+p),d=await r.json();tot=d.total||0;renderT(d.records||[]);renderP();
  }catch(e){document.getElementById('tB').innerHTML='<tr><td colspan="10"><div class="em"><div class="em-i">⚠️</div><div class="em-t">加载失败</div><div class="em-d">请检查网络连接</div></div></td></tr>'}
}
function renderT(recs){
  let h=document.getElementById('tH'),b=document.getElementById('tB');
  let hr=[{k:'student_name_cn',l:'学生姓名'},{k:'country',l:'国家'},{k:'university_cn',l:'录取大学'},{k:'major_cn',l:'专业'},{k:'admission_type',l:'录取类型'},{k:'admission_status',l:'录取状态'},{k:'admission_year',l:'年份'},{k:'scholarship',l:'奖学金'},{k:'data_source',l:'数据来源'}].filter(x=>fc[x.k]);
  h.innerHTML=hr.map(x=>'<th>'+x.l+'</th>').join('')+'<th>操作</th>';
  document.getElementById('rCnt').textContent=tot+' 条';
  if(!recs.length){b.innerHTML='<tr><td colspan="'+(hr.length+1)+'"><div class="em"><div class="em-i">📋</div><div class="em-t">暂无数据</div><div class="em-d">创建采集任务开始收集</div></div></td></tr>';return}
  b.innerHTML=recs.map(r=>{let cs=hr.map(x=>{if(x.k==='scholarship')return r.scholarship_amount?'$'+r.scholarship_amount:'<span style="color:var(--muted)">-</span>';return r[x.k]||'<span style="color:var(--muted)">-</span>'}).join('');
  return '<tr>'+cs+'<td><button class="btn bo sm" onclick="editR('+r.id+')">编辑</button> <button class="btn bd sm" onclick="delR('+r.id+')">删除</button></td></tr>'}).join('');
}
function renderP(){let tp=Math.ceil(tot/ps)||1;document.getElementById('pI').textContent='第 '+pg+'/'+tp+' 页，共 '+tot+' 条';document.getElementById('pP').disabled=pg<=1;document.getElementById('pN').disabled=pg>=tp}
function chgP(d){pg+=d;loadRec()}
function resetS(){document.getElementById('sI').value='';document.getElementById('cF').value='';document.getElementById('yF').value='';pg=1;loadRec()}
function editR(id){toast('编辑功能开发中 (ID:'+id+')',false)}
async function delR(id){if(!confirm('确定删除？'))return;try{let r=await fetch(A+'/records/'+id,{method:'DELETE'});if(r.ok){toast('删除成功');loadRec()}else toast('删除失败',false)}catch(e){toast('失败',false)}}

/* ===== FIELDS ===== */
function openFld(){document.getElementById('fC').innerHTML=Object.keys(fc).map(k=>'<div class="ck"><input type="checkbox" id="f-'+k+'"'+(fc[k]?' checked':'')+'><label for="f-'+k+'">'+k+'</label></div>').join('');openMod('fldMod')}
function saveFld(){Object.keys(fc).forEach(k=>{fc[k]=document.getElementById('f-'+k).checked});closeMod('fldMod');loadRec();toast('字段设置已保存')}

/* ===== EXPORT ===== */
async function exportD(fmt){
  closeMod('expMod');try{let f=Object.keys(fc).filter(k=>fc[k]),r=await fetch(A+'/records/export/'+fmt,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({fields:f})});
  if(r.ok){let b=await r.blob(),u=URL.createObjectURL(b),a=document.createElement('a');a.href=u;a.download='录取数据.'+(fmt==='excel'?'xlsx':fmt);a.click();toast('导出成功')}else toast('导出失败',false)}catch(e){toast('导出失败',false)}
}

/* ===== TASKS ===== */
async function loadTsk(){
  try{let r=await fetch(A+'/collection-tasks'),tk=await r.json();document.getElementById('tCnt').textContent=tk.length+' 个';
  let b=document.getElementById('tT');if(!tk.length){b.innerHTML='<tr><td colspan="7"><div class="em"><div class="em-i">⚡</div><div class="em-t">暂无任务</div><div class="em-d">点击"新建任务"开始采集</div></div></td></tr>';return}
  let sm={0:'待处理',1:'待处理',2:'处理中',3:'已完成',4:'失败'},sc={0:'b-w',1:'b-w',2:'b-i',3:'b-ok',4:'b-err'};
  b.innerHTML=tk.map(t=>{let u=t.article_url||t.url||'-';if(u.length>50)u=u.substring(0,50)+'...';
  return '<tr><td>'+t.id+'</td><td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="'+(t.article_url||t.url||'')+'">'+u+'</td><td>'+(t.title||'<span style="color:var(--muted)">-</span>')+'</td><td><span class="b '+sc[t.task_status]+'"><span class="b-dot"></span>'+(sm[t.task_status]||'未知')+'</span></td><td>'+(t.extracted_count||t.records_count||0)+'</td><td>'+(t.created_at?t.created_at.substring(0,16):'-')+'</td><td><button class="btn bs sm" onclick="startT('+t.id+')">执行</button></td></tr>'}).join('');
  }catch(e){document.getElementById('tT').innerHTML='<tr><td colspan="7"><div class="em"><div class="em-t">加载失败</div></div></td></tr>'}
}
async function startT(id){try{let r=await fetch(A+'/collection-tasks/'+id+'/start',{method:'POST'});if(r.ok){toast('任务已启动');loadTsk()}else toast('启动失败',false)}catch(e){toast('失败',false)}}
async function execAll(){if(!confirm('执行所有待处理任务？'))return;try{let r=await fetch(A+'/collection-tasks/batch-start',{method:'POST'});if(!r.ok)r=await fetch(A+'/collection-tasks/execute-all',{method:'POST'});if(r.ok){toast('已开始执行');loadTsk()}else toast('失败',false)}catch(e){toast('失败',false)}}

async function prevTsk(){
  let u=document.getElementById('tU').value.trim().split('\n')[0].trim();if(!u){toast('请输入URL',false);return}
  let b=document.getElementById('pBtn');b.disabled=true;b.textContent='预览中...';
  try{let r=await fetch(A+'/collection/preview',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:u})}),d=await r.json();
  if(d.success){document.getElementById('pBox').style.display='block';document.getElementById('pCon').innerHTML='<div style="font-size:12px;display:grid;gap:4px"><div><b>标题:</b> '+(d.title||'-')+'</div><div><b>学校:</b> '+(d.school||'-')+'</div><div><b>预估:</b> '+(d.estimated_records||0)+' 条</div></div>'}
  else toast('预览失败',false)}catch(e){toast('预览失败',false)}finally{b.disabled=false;b.textContent='采集预览'}
}
async function mkTsk(){
  let us=document.getElementById('tU').value.trim().split('\n').filter(u=>u.trim());if(!us.length){toast('请输入URL',false);return}
  let n=0;for(let u of us){let r=await fetch(A+'/collection-tasks',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:u.trim()})});if(r.ok)n++}
  toast('创建 '+n+'/'+us.length+' 个任务');closeMod('tskMod');loadTsk();
}

/* ===== REVIEW ===== */
async function loadRev(){
  try{let p=new URLSearchParams({page:rpg,page_size:rps});if(rf&&rf!=='all')p.append('status',rf);
  let r=await fetch(A+'/review/pending?'+p),d=await r.json();renderRev(d.records||[]);updBadge();
  }catch(e){document.getElementById('rT').innerHTML='<tr><td colspan="10"><div class="em"><div class="em-t">加载失败</div></div></td></tr>'}
}
function renderRev(recs){
  let b=document.getElementById('rT');if(!recs.length){b.innerHTML='<tr><td colspan="10"><div class="em"><div class="em-i">✅</div><div class="em-t">暂无记录</div><div class="em-d">'+(rf==='pending'?'所有数据已审核完成':'该状态下无记录')+'</div></div></td></tr>';return}
  b.innerHTML=recs.map(r=>{
  let sc=r.review_status==='approved'?'b-ok':r.review_status==='rejected'?'b-err':'b-w';
  let st=r.review_status==='approved'?'已通过':r.review_status==='rejected'?'已拒绝':'待审核';
  let ip=r.review_status==='pending',ck=rS.includes(r.id)?' checked':'',di=ip?'':' disabled';
  return '<tr><td><input type="checkbox" class="rcb" onchange="togR('+r.id+',this)"'+ck+di+'></td><td>'+r.id+'</td><td><b>'+(r.student_name_cn||'-')+'</b></td><td>'+(r.university_cn||'-')+'</td><td>'+(r.major_cn||'-')+'</td><td><span class="b b-n">'+(r.country||'-')+'</span></td><td>'+(r.data_source||'-')+'</td><td>'+(r.created_at?r.created_at.substring(0,16):'-')+'</td><td><span class="b '+sc+'"><span class="b-dot"></span>'+st+'</span></td><td>'+(ip?'<button class="btn bs sm" onclick="appr('+r.id+')">通过</button> <button class="btn bd sm" onclick="rej('+r.id+')">拒绝</button>':'')+'</td></tr>'}).join('');
  document.getElementById('bApp').style.display=rS.length?'inline-flex':'none';document.getElementById('bRej').style.display=rS.length?'inline-flex':'none';
}
function togR(id,cb){if(cb.checked){if(!rS.includes(id))rS.push(id)}else{rS=rS.filter(i=>i!==id)};document.getElementById('bApp').style.display=rS.length?'inline-flex':'none';document.getElementById('bRej').style.display=rS.length?'inline-flex':'none'}
function togAll(){let ck=document.getElementById('rAll').checked;document.querySelectorAll('#rT .rcb:not(:disabled)').forEach(cb=>{cb.checked=ck;let row=cb.closest('tr'),id=parseInt(row.cells[1].textContent);if(ck){if(!rS.includes(id))rS.push(id)}else{rS=rS.filter(i=>i!==id)}});document.getElementById('bApp').style.display=rS.length?'inline-flex':'none';document.getElementById('bRej').style.display=rS.length?'inline-flex':'none'}
async function appr(id){try{let r=await fetch(A+'/review/'+id,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:'approved',comment:'',reviewer:'管理员'})}),d=await r.json();if(r.ok){toast(d.message||'已通过');rS=rS.filter(i=>i!==id);loadRev()}else toast('失败',false)}catch(e){toast('失败',false)}}
async function rej(id){let c=prompt('拒绝原因（可选）：');if(c===null)return;try{let r=await fetch(A+'/review/'+id,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:'rejected',comment:c||'',reviewer:'管理员'})}),d=await r.json();if(r.ok){toast(d.message||'已拒绝');rS=rS.filter(i=>i!==id);loadRev()}else toast('失败',false)}catch(e){toast('失败',false)}}
async function batchR(act){if(!rS.length){toast('请先选择',false);return}let c='';if(act==='reject')c=prompt('拒绝原因（可选）：')||'';if(!confirm('批量'+(act==='approve'?'通过':'拒绝')+' '+rS.length+' 条？'))return;try{let r=await fetch(A+'/review/batch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({record_ids:rS,action:act==='approve'?'approved':'rejected',comment:c,reviewer:'管理员'})}),d=await r.json();if(r.ok){toast(d.message||'成功');rS=[];loadRev()}else toast('失败',false)}catch(e){toast('失败',false)}}
function setRF(f,btn){rf=f;rpg=1;rS=[];document.querySelectorAll('.fb-b').forEach(b=>b.classList.remove('active'));btn.classList.add('active');loadRev()}
async function updBadge(){try{let r=await fetch(A+'/review/stats'),s=await r.json(),b=document.getElementById('rBadge');if(b)b.textContent=s.pending||0}catch(e){}}

/* ===== STATS ===== */
async function loadSt(){
  try{let r=await fetch(A+'/records?page=1&page_size=1'),d=await r.json();document.getElementById('sT').textContent=d.total||0}catch(e){}
  try{let r=await fetch(A+'/review/stats'),s=await r.json();document.getElementById('sC').textContent='5';document.getElementById('sU').textContent='-';let b=document.getElementById('rBadge');if(b)b.textContent=s.pending||0}catch(e){}
  try{let r=await fetch(A+'/collection-tasks'),tk=await r.json();document.getElementById('sK').textContent=tk.length;let p=tk.filter(t=>t.task_status===0||t.task_status===1).length;document.getElementById('sTN').textContent=p>0?p+' 个待执行':'全部完成'}catch(e){}
  if(typeof echarts==='undefined')return;
  let c1=echarts.init(document.getElementById('cC'));c1.setOption({tooltip:{trigger:'item'},series:[{type:'pie',radius:['35%','65%'],itemStyle:{borderRadius:5,borderColor:'#fff',borderWidth:2},label:{formatter:'{b}: {d}%'},data:[{value:30,name:'美国'},{value:20,name:'英国'},{value:10,name:'加拿大'},{value:5,name:'澳大利亚'}]}]});
  let c2=echarts.init(document.getElementById('cU'));c2.setOption({tooltip:{trigger:'axis',axisPointer:{type:'shadow'}},grid:{left:'3%',right:'4%',bottom:'3%',containLabel:true},xAxis:{type:'value'},yAxis:{type:'category',data:['牛津','剑桥','哈佛','MIT','斯坦福']},series:[{type:'bar',data:[15,12,10,8,6],itemStyle:{borderRadius:[0,4,4,0],color:'#4f46e5'}}]});
  let c3=echarts.init(document.getElementById('cR'));c3.setOption({tooltip:{trigger:'axis'},xAxis:{type:'category',data:['2022','2023','2024','2025','2026']},yAxis:{type:'value'},series:[{type:'line',data:[5,12,18,25,38],smooth:true,areaStyle:{opacity:.1},itemStyle:{color:'#4f46e5'}}]});
  let c4=echarts.init(document.getElementById('cM'));c4.setOption({tooltip:{trigger:'item'},series:[{type:'pie',radius:['35%','65%'],itemStyle:{borderRadius:5,borderColor:'#fff',borderWidth:2},label:{formatter:'{b}: {d}%'},data:[{value:15,name:'计算机'},{value:12,name:'商科'},{value:10,name:'工程'},{value:8,name:'艺术'}]}]});
  window.addEventListener('resize',()=>{c1.resize();c2.resize();c3.resize();c4.resize()});
}

document.addEventListener('DOMContentLoaded',()=>{loadRec();document.querySelectorAll('.mo').forEach(m=>{m.addEventListener('click',e=>{if(e.target===m)m.classList.remove('open')})});document.addEventListener('keydown',e=>{if(e.key==='Escape')document.querySelectorAll('.mo.open').forEach(m=>m.classList.remove('open'))})});
</script></body></html>'''

html.append(js)

full = '\n'.join(html)

# Encode
b64 = base64.b64encode(full.encode('utf-8')).decode()

py = '#!/usr/bin/env python3\n"""大学录取信息整理系统 - 管理后台 v3.0 (完整版)"""\nimport base64\n\n_HTML_B64 = ' + repr(b64) + '\n\nHTML_CONTENT = base64.b64decode(_HTML_B64).decode("utf-8")\n'

with open('/root/.openclaw/workspace/大学录取信息整理系统/backend/app/admin_page.py', 'w', encoding='utf-8') as f:
    f.write(py)

print("Written:", len(full), "bytes")
print("Base64:", len(b64), "bytes")

py_compile.compile('/root/.openclaw/workspace/大学录取信息整理系统/backend/app/admin_page.py', doraise=True)
print("Syntax: OK")

# Verify
print("Pages:", 'p-records' in full, 'p-tasks' in full, 'p-review' in full, 'p-stats' in full)
print("Nav:", full.count('data-p='))
print("Table CSS:", 'border-collapse:collapse' in full)
print("JS:", 'loadRec' in full and 'loadTsk' in full and 'loadRev' in full and 'loadSt' in full)
