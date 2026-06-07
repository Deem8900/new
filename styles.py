"""
ui/styles.py — Global CSS and shared constants for the AcademiQ UI.
Import load_css() once in streamlit_app.py before rendering any page.
"""

import streamlit as st

LOGO = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTs6H6P_HFjXiSY-3SBqYo8AwSyttwS84IO_Q&s"

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
*, html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top:0 !important; padding-left:2rem !important;
                   padding-right:2rem !important; max-width:1280px; }

/* ── Navbar ── */
.uoh-nav {
  background:linear-gradient(90deg,#0b1e48 0%,#1a3a8a 55%,#1d4ed8 100%);
  height:64px; padding:0 32px;
  display:flex; align-items:center; justify-content:space-between;
  margin:-1rem -2rem 0; box-shadow:0 3px 18px rgba(11,30,72,.45);
}
.uoh-nav-left { display:flex; align-items:center; gap:14px; }
.uoh-nav-logo { width:42px;height:42px;border-radius:50%;
  border:2px solid rgba(255,255,255,.3);object-fit:cover; }
.uoh-nav-brand { font-weight:900;font-size:1.2rem;color:#fff;letter-spacing:-.4px; }
.uoh-nav-sub   { font-size:.67rem;color:rgba(255,255,255,.45);margin-top:2px; }
.uoh-nav-pill  { background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.22);
  border-radius:50px;padding:5px 16px;font-size:.75rem;font-weight:600;color:#fff; }

/* ── Breadcrumb ── */
.uoh-bread { display:flex;align-items:center;gap:8px;padding:12px 0 4px;font-size:.82rem; }
.uoh-bread-item { color:#64748b;font-weight:500; }
.uoh-bread-sep  { color:#cbd5e1; }
.uoh-bread-curr { color:#0b1e48;font-weight:700; }

/* ── Welcome bar ── */
.uoh-welcome {
  background:linear-gradient(135deg,#0b1e48 0%,#1a3a8a 60%,#2563eb 100%);
  border-radius:18px;padding:20px 30px;margin:18px 0 22px;
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;
  box-shadow:0 6px 28px rgba(11,30,72,.2);
}
.uoh-welcome h2 { margin:0;font-size:1.12rem;font-weight:900;color:#fff; }
.uoh-welcome p  { margin:4px 0 0;font-size:.76rem;color:rgba(255,255,255,.5); }
.uoh-badge { background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.2);
  border-radius:50px;padding:5px 15px;font-size:.72rem;font-weight:700;color:#fff;margin:2px; }

/* ── Section title ── */
.uoh-sec-title { display:flex;align-items:center;gap:10px;margin:24px 0 12px; }
.uoh-sec-icon  {
  width:38px;height:38px;border-radius:10px;
  background:linear-gradient(135deg,#0b1e48,#2563eb);
  display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;
}
.uoh-sec-label { font-weight:800;font-size:1rem;color:#0b1e48; }
.uoh-sec-sub   { font-size:.74rem;color:#64748b;margin-top:1px; }

/* ── Schedule table ── */
.sched-wrap { border-radius:14px;overflow:hidden;
  box-shadow:0 4px 22px rgba(11,30,72,.1);margin-bottom:6px; }
.sched-tbl  { width:100%;border-collapse:collapse;font-size:.84rem; }
.sched-tbl thead th {
  background:#0b1e48;color:#fff;padding:13px 16px;
  font-weight:700;font-size:.76rem;text-align:center;
  text-transform:uppercase;letter-spacing:.4px;white-space:nowrap;
}
.sched-tbl tbody td {
  padding:11px 16px;text-align:center;border-bottom:1px solid #f0f4fb;color:#1e293b;
}
.sched-tbl tbody tr:nth-child(even) td { background:#f7f9ff; }
.sched-tbl tbody tr:nth-child(odd)  td { background:#fff; }
.sched-tbl tbody tr:hover td { background:#eef3ff !important; }
.sched-tbl td.ref-col {
  background:#0b1e48 !important;color:#fff !important;font-weight:900;font-size:.95rem;
}
.sched-tbl tr:hover .ref-col { background:#162d6b !important; }
.type-lec { display:inline-block;background:#dbeafe;color:#1d4ed8;
  border-radius:6px;padding:2px 9px;font-size:.7rem;font-weight:700; }
.type-lab { display:inline-block;background:#ede9fe;color:#6d28d9;
  border-radius:6px;padding:2px 9px;font-size:.7rem;font-weight:700; }

/* ── Service buttons row (small action buttons) ── */
.svc-actions-row {
  display:flex; gap:12px; flex-wrap:wrap; margin:16px 0 8px;
}

/* ── Section card ── */
.sec-card {
  border-radius:16px;overflow:hidden;margin-bottom:4px;
  box-shadow:0 4px 18px rgba(11,30,72,.1);border:1.5px solid #e5eaf5;
}
.sec-card-head {
  background:linear-gradient(135deg,#0b1e48 0%,#1e3a8a 60%,#2563eb 100%);
  padding:15px 22px;display:flex;align-items:flex-start;
  justify-content:space-between;flex-wrap:wrap;gap:10px;
}
.sec-rank  { background:rgba(255,255,255,.15);border-radius:6px;
  padding:3px 10px;font-size:.7rem;font-weight:800;color:#fff;
  letter-spacing:.3px;margin-bottom:6px;display:inline-block; }
.sec-crn   { font-weight:900;font-size:1.05rem;color:#fff; }
.sec-name  { font-size:.8rem;color:rgba(255,255,255,.65);margin-top:4px; }
.sec-stars-wrap { text-align:right; }
.sec-stars      { font-size:1.2rem;line-height:1; }
.sec-score-lbl  { font-size:.7rem;color:rgba(255,255,255,.5);margin-top:4px; }
.sec-card-body  { background:#fff;padding:16px 22px 14px; }
.sec-grid { display:grid;grid-template-columns:repeat(4,1fr);gap:12px 8px; }
.sec-gi .gi-lbl {
  font-size:.63rem;color:#94a3b8;font-weight:700;
  text-transform:uppercase;letter-spacing:.6px;margin-bottom:3px;
}
.sec-gi .gi-val { font-size:.87rem;font-weight:700;color:#0f172a; }
.seats-hi { color:#16a34a !important; }
.seats-lo { color:#dc2626 !important; }

/* ── Info / warn boxes ── */
.box-info { background:#eff6ff;border-left:4px solid #3b82f6;
  border-radius:0 10px 10px 0;padding:12px 16px;
  font-size:.83rem;color:#1e40af;margin-bottom:14px;line-height:1.6; }
.box-warn { background:#fef9ec;border-left:4px solid #f59e0b;
  border-radius:0 10px 10px 0;padding:12px 16px;
  font-size:.83rem;color:#92400e;margin-bottom:14px; }

/* ── Confirm card ── */
.confirm-card {
  background:linear-gradient(135deg,#fffbeb,#fef3c7);
  border:2px solid #fbbf24;border-radius:18px;
  padding:22px 28px;margin-bottom:20px;
  box-shadow:0 4px 20px rgba(251,191,36,.15);
}
.confirm-card h3 { margin:0 0 14px;color:#78350f;font-size:1rem;font-weight:900; }
.cf-grid  { display:grid;grid-template-columns:1fr 1fr;gap:10px 32px; }
.cf-label { font-size:.66rem;font-weight:700;text-transform:uppercase;
  letter-spacing:.5px;color:#b45309; }
.cf-value { font-size:.9rem;font-weight:700;color:#78350f;margin-top:2px; }

/* ── Divider ── */
.uoh-divider { border:none;border-top:1.5px solid #e8edf8;margin:20px 0; }

/* ── Login panel ── */
.login-left {
  background:linear-gradient(160deg,#0b1e48 0%,#1a3a8a 55%,#2563eb 100%);
  border-radius:20px 0 0 20px;padding:52px 36px;min-height:510px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;
}
.login-left img {
  width:88px;height:88px;border-radius:50%;object-fit:cover;
  border:4px solid rgba(255,255,255,.3);box-shadow:0 8px 28px rgba(0,0,0,.3);
  margin-bottom:20px;
}
.login-left h2 { color:#fff;font-size:1.35rem;font-weight:900;margin:0 0 8px; }
.login-left p  { color:rgba(255,255,255,.5);font-size:.79rem;margin:0 0 22px;line-height:1.7; }
.l-badge {
  display:inline-block;background:rgba(255,255,255,.12);
  border:1px solid rgba(255,255,255,.2);border-radius:50px;
  padding:5px 15px;font-size:.71rem;font-weight:700;color:#fff;margin:3px;
}
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:nth-child(3) {
  background:#fff;border-radius:0 20px 20px 0;padding:44px 36px !important;
  box-shadow:0 18px 56px rgba(11,30,72,.13);
}

/* ── Input / Button polish ── */
div[data-baseweb="select"] > div {
  border-radius:11px !important;border:1.5px solid #dce4f3 !important;background:#f8faff !important;
}
.stTextInput > div > div > input {
  border-radius:11px !important;border:1.5px solid #dce4f3 !important;
  padding:11px 15px !important;background:#f8faff !important;
  color:#0f172a !important;
}
.stTextInput > div > div > input::placeholder {
  color:#94a3b8 !important;
}
.stButton > button {
  border-radius:11px !important;font-weight:700 !important;
  font-size:.87rem !important;transition:all .18s !important;
}
.stButton > button:hover { transform:translateY(-1px) !important; }

/* ── Soft card shadows (additive, applied to existing cards) ── */
.sec-card { box-shadow:0 6px 20px rgba(11,30,72,.10), 0 2px 6px rgba(11,30,72,.06) !important; }
.sched-wrap { box-shadow:0 6px 24px rgba(11,30,72,.10), 0 2px 6px rgba(11,30,72,.05) !important; }
.box-info, .box-warn { box-shadow:0 3px 12px rgba(11,30,72,.07); }
.confirm-card { box-shadow:0 8px 28px rgba(251,191,36,.18), 0 2px 8px rgba(11,30,72,.06) !important; }
.uoh-welcome { box-shadow:0 10px 34px rgba(11,30,72,.22), 0 2px 8px rgba(11,30,72,.10) !important; }

/* ── Floating Academic-Advisor chat widget (FAB) ── */
.st-key-uoh_advisor_fab_wrap {
  position:fixed; bottom:28px; right:28px; z-index:9999;
  width:auto !important; pointer-events:none;
}
.st-key-uoh_advisor_fab_wrap > * { pointer-events:auto; }
.st-key-uoh_advisor_fab_wrap [data-testid="stButton"] > button {
  width:64px !important; height:64px !important;
  border-radius:50% !important; padding:0 !important;
  font-size:1.7rem !important; line-height:1 !important;
  background:linear-gradient(135deg,#0b1e48 0%,#1d4ed8 60%,#3b82f6 100%) !important;
  color:#fff !important; border:3px solid #fff !important;
  box-shadow:0 10px 28px rgba(29,78,216,.45),
             0 2px 6px rgba(11,30,72,.25),
             inset 0 1px 0 rgba(255,255,255,.3) !important;
  position:relative;
  animation: uoh-fab-pulse 2.4s ease-in-out infinite;
}
.st-key-uoh_advisor_fab_wrap [data-testid="stButton"] > button:hover {
  transform:translateY(-3px) scale(1.06) !important;
  box-shadow:0 14px 36px rgba(29,78,216,.55),
             0 4px 10px rgba(11,30,72,.30) !important;
}
@keyframes uoh-fab-pulse {
  0%,100% { box-shadow:0 10px 28px rgba(29,78,216,.45),
                       0 0  0   0 rgba(59,130,246,.55); }
  50%     { box-shadow:0 10px 28px rgba(29,78,216,.55),
                       0 0  0  14px rgba(59,130,246,0); }
}
.uoh-fab-tag {
  position:fixed; bottom:96px; right:22px; z-index:9999;
  background:#0b1e48; color:#fff;
  padding:6px 12px; border-radius:18px;
  font-size:.7rem; font-weight:700; letter-spacing:.2px;
  box-shadow:0 6px 18px rgba(11,30,72,.30);
  white-space:nowrap; pointer-events:none;
}
.uoh-fab-tag::after {
  content:""; position:absolute; right:18px; bottom:-6px;
  width:12px; height:12px; background:#0b1e48; transform:rotate(45deg);
}

/* ── Distinctive chat dialog (popup) — enhanced ── */
.uoh-chat-modal-head {
  background:linear-gradient(135deg,#0b1e48 0%,#1a3a8a 60%,#2563eb 100%);
  color:#fff; border-radius:14px 14px 0 0;
  padding:16px 20px; margin:-1rem -1rem 18px -1rem;
  display:flex; align-items:center; gap:14px;
  box-shadow:0 4px 16px rgba(11,30,72,.25);
}
.uoh-chat-modal-avatar {
  width:46px; height:46px; border-radius:50%;
  background:linear-gradient(135deg,#3b82f6,#1d4ed8);
  display:flex; align-items:center; justify-content:center;
  font-size:1.5rem; border:2px solid rgba(255,255,255,.4);
  box-shadow:0 4px 12px rgba(0,0,0,.25);
}
.uoh-chat-modal-title { font-weight:900; font-size:1rem; line-height:1.2; }
.uoh-chat-modal-sub   { font-size:.72rem; opacity:.75; margin-top:3px; }
.uoh-chat-status-dot  {
  display:inline-block; width:8px; height:8px; border-radius:50%;
  background:#22c55e; box-shadow:0 0 0 3px rgba(34,197,94,.25);
  margin-right:6px; vertical-align:middle;
}
.uoh-chat-scroll {
  max-height:340px; overflow-y:auto;
  background:#f8faff; border:1px solid #e5eaf5;
  border-radius:12px; padding:12px 14px; margin-bottom:14px;
  box-shadow:inset 0 2px 6px rgba(11,30,72,.05);
}

/* ── Enhanced chat bubbles ── */
.chat-bubble-student {
  background:linear-gradient(135deg,#dbeafe,#eff6ff);
  border:1px solid #bfdbfe;
  border-radius:16px 16px 4px 16px;
  padding:12px 16px;
  font-size:.83rem; color:#1e40af;
  margin:8px 0; display:inline-block; max-width:85%;
  text-align:left;
  box-shadow:0 2px 8px rgba(59,130,246,.12);
}
.chat-bubble-advisor {
  background:linear-gradient(135deg,#fef9ec,#fffbeb);
  border:1px solid #fde68a;
  border-radius:16px 16px 16px 4px;
  padding:12px 16px;
  font-size:.83rem; color:#92400e;
  margin:8px 0; display:inline-block; max-width:85%;
  text-align:left;
  box-shadow:0 2px 8px rgba(245,158,11,.12);
}
.chat-bubble-meta {
  font-size:.7rem; opacity:.65; margin-bottom:4px; font-weight:600;
}
.chat-bubble-body { margin-top:4px; line-height:1.55; }
.chat-bubble-action {
  margin-top:6px; font-size:.76rem;
  padding:6px 10px; border-radius:8px;
  background:rgba(0,0,0,.04);
}
.chat-empty-state {
  text-align:center; padding:40px 20px; color:#94a3b8;
  font-size:.85rem;
}
.chat-empty-state .chat-empty-icon { font-size:2.5rem; margin-bottom:10px; }

/* ── Notification badge ── */
.notif-badge {
  display:inline-flex; align-items:center; justify-content:center;
  background:#ef4444; color:#fff;
  font-size:.65rem; font-weight:800;
  min-width:20px; height:20px; padding:0 5px;
  border-radius:50px;
  box-shadow:0 2px 8px rgba(239,68,68,.4);
  animation: notif-pop .3s ease-out;
}
@keyframes notif-pop {
  0% { transform:scale(0); }
  60% { transform:scale(1.2); }
  100% { transform:scale(1); }
}

/* ── Notification panel ── */
.notif-panel {
  background:#fff; border:1.5px solid #e5eaf5; border-radius:14px;
  padding:16px; margin-bottom:18px;
  box-shadow:0 4px 18px rgba(11,30,72,.08);
}
.notif-panel-head {
  display:flex; align-items:center; justify-content:space-between;
  margin-bottom:12px;
}
.notif-panel-title {
  font-weight:800; font-size:.95rem; color:#0b1e48;
  display:flex; align-items:center; gap:8px;
}
.notif-item {
  display:flex; align-items:flex-start; gap:10px;
  padding:10px 12px; border-radius:10px;
  margin-bottom:6px; transition:background .15s;
}
.notif-item:hover { background:#f8faff; }
.notif-item-unread { background:#eff6ff; border-left:3px solid #3b82f6; }
.notif-item-read { background:#fff; border-left:3px solid transparent; opacity:.7; }
.notif-icon {
  width:32px; height:32px; border-radius:8px;
  display:flex; align-items:center; justify-content:center;
  font-size:.9rem; flex-shrink:0;
}
.notif-icon-add    { background:#dbeafe; }
.notif-icon-drop   { background:#fee2e2; }
.notif-icon-change { background:#fef3c7; }
.notif-icon-msg    { background:#dcfce7; }
.notif-icon-info   { background:#f1f5f9; }
.notif-title  { font-weight:700; font-size:.82rem; color:#0b1e48; }
.notif-body   { font-size:.75rem; color:#64748b; margin-top:2px; line-height:1.4; }
.notif-time   { font-size:.65rem; color:#94a3b8; margin-top:3px; }

/* ── Advisor inbox preview (unread messages from students) ── */
.inbox-card {
  background:#fff; border:1.5px solid #e5eaf5; border-radius:14px;
  padding:14px 18px; margin-bottom:8px;
  display:flex; align-items:center; justify-content:space-between;
  gap:12px; cursor:pointer; transition:all .15s;
}
.inbox-card:hover { background:#f8faff; box-shadow:0 4px 14px rgba(11,30,72,.08); }
.inbox-card-unread { border-left:3px solid #3b82f6; }
.inbox-avatar {
  width:36px; height:36px; border-radius:50%;
  background:linear-gradient(135deg,#0b1e48,#2563eb);
  display:flex; align-items:center; justify-content:center;
  color:#fff; font-size:.8rem; font-weight:800; flex-shrink:0;
}
.inbox-info { flex:1; }
.inbox-name { font-weight:700; font-size:.85rem; color:#0b1e48; }
.inbox-preview { font-size:.73rem; color:#64748b; margin-top:2px;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:300px; }
.inbox-meta { text-align:right; }
.inbox-time { font-size:.65rem; color:#94a3b8; }

</style>
"""


def load_css() -> None:
    """Inject the global CSS into the Streamlit page. Call once at startup."""
    st.markdown(_CSS, unsafe_allow_html=True)
