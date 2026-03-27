import html
import streamlit as st

MAHWOUS_URL = "https://mahwous.com/"

def get_styles():
    return """
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stat-card {
        background: linear-gradient(145deg,#161b22,#1c2330);
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #30363d;
        text-align: center;
        margin-bottom: 10px;
        transition: transform .2s;
    }
    .stat-card:hover { transform: translateY(-2px); }
    .vs-card {
        background: #161b22;
        padding: 14px;
        border-radius: 14px;
        border: 1px solid #30363d;
        margin-bottom: 14px;
        transition: box-shadow .2s;
    }
    .vs-card:hover { box-shadow: 0 4px 18px rgba(0,0,0,.5); }
    .comp-strip {
        display: flex;
        gap: 8px;
        overflow-x: auto;
        padding: 8px 0;
        scrollbar-width: thin;
    }
    .comp-strip::-webkit-scrollbar { height: 4px; }
    .comp-strip::-webkit-scrollbar-thumb { background: #30363d; border-radius: 4px; }
    .miss-card {
        background: #1c1c1c;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 10px;
    }
    .store-banner {
        background: linear-gradient(135deg,#1a1f2e,#161b22);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 14px;
    }
    </style>
    """

def get_sidebar_toggle_js():
    return "<script>console.log('Sidebar toggle JS loaded');</script>"

def stat_card(icon, label, val, color):
    return f"""
    <div class="stat-card" style="border-top: 3px solid {color}">
        <div style="font-size: 1.5rem;">{icon}</div>
        <div style="font-size: 0.8rem; color: #8b949e;">{label}</div>
        <div style="font-size: 1.2rem; font-weight: bold; color: {color};">{val}</div>
    </div>
    """

def vs_card(our_name, our_price, comp_name, comp_price, diff_pct, diff_val,
             our_image_url=None, comp_image_url=None, comp_src="", pid_str=""):
    """بطاقة مقارنة بصرية مزدوجة (منتجنا vs المنافس)."""
    on  = html.escape(str(our_name))
    cn  = html.escape(str(comp_name))
    cs  = html.escape(str(comp_src or ""))
    ps  = html.escape(str(pid_str or ""))
    dps = html.escape(str(diff_pct))

    try:
        dv = float(diff_val)
    except (TypeError, ValueError):
        dv = 0.0

    accent = "#3fb950" if dv <= 0 else "#f85149"

    def _img_block(url, placeholder):
        u = (url or "").strip()
        if u and u not in ("None", "nan") and u.startswith("http"):
            return (
                f'<img src="{html.escape(u)}" '
                'style="width:64px;height:64px;border-radius:9px;object-fit:cover;'
                'border:1px solid #30363d;flex-shrink:0;" '
                'onerror="this.style.display=\'none\'">'
            )
        return (
            f'<div style="width:64px;height:64px;border-radius:9px;background:#21262d;'
            f'color:#8b949e;font-size:0.6rem;display:flex;align-items:center;'
            f'justify-content:center;text-align:center;padding:4px;">{placeholder}</div>'
        )

    our_img  = _img_block(our_image_url,  "بدون<br>صورة")
    comp_img = _img_block(comp_image_url, "بدون<br>صورة")

    pid_line = (
        f'<div style="font-size:0.72rem;color:#8b949e;margin-top:3px;">ID: {ps}</div>'
        if ps else ""
    )
    src_line = (
        f'<div style="font-size:0.72rem;color:#8b949e;margin-top:3px;">{cs}</div>'
        if cs else ""
    )

    # رابط مهووس لمنتجنا
    mahwous_link = (
        f'<div style="margin-top:5px;">'
        f'<a href="{MAHWOUS_URL}" target="_blank" '
        f'style="font-size:0.7rem;color:#58a6ff;text-decoration:none;">🔗 مهووس</a>'
        f'</div>'
    )

    return f"""
    <div class="vs-card">
        <div style="display:flex;justify-content:space-between;align-items:stretch;
                    gap:8px;background:#0d1117;border:1px solid #21262d;
                    border-radius:10px;padding:10px;">
            <!-- منتجنا -->
            <div style="flex:1;text-align:right;padding-left:8px;min-width:0;">
                <div style="display:flex;align-items:center;gap:10px;justify-content:flex-end;">
                    <div style="min-width:0;">
                        <strong style="color:#8b949e;font-size:0.75rem;">متجرنا</strong><br>
                        <span style="color:#e6edf3;font-size:0.9rem;">{on}</span><br>
                        <b style="color:#58a6ff;font-size:1rem;">{our_price} ر.س</b>
                        {pid_line}
                        {mahwous_link}
                    </div>
                    {our_img}
                </div>
            </div>
            <!-- الفارق -->
            <div style="padding:0 10px;text-align:center;border-left:1px solid #30363d;
                        border-right:1px solid #30363d;display:flex;flex-direction:column;
                        justify-content:center;min-width:72px;">
                <strong style="color:{accent};font-size:15px;" dir="ltr">{dps}%</strong>
                <span style="color:#8b949e;font-size:10px;margin-top:2px;">الفارق</span>
                <span style="color:{accent};font-size:11px;margin-top:4px;" dir="ltr">{dv:.0f} ر.س</span>
            </div>
            <!-- المنافس -->
            <div style="flex:1;text-align:left;padding-right:8px;min-width:0;">
                <div style="display:flex;align-items:center;gap:10px;justify-content:flex-start;">
                    {comp_img}
                    <div style="min-width:0;">
                        <strong style="color:#8b949e;font-size:0.75rem;">المنافس</strong><br>
                        <span style="color:#e6edf3;font-size:0.9rem;">{cn}</span><br>
                        <b style="color:{accent};font-size:1rem;">{comp_price} ر.س</b>
                        {src_line}
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

def comp_strip(all_comps):
    out = '<div class="comp-strip">'
    for comp in (all_comps or []):
        out += (
            f'<div style="background:#21262d;padding:4px 12px;border-radius:20px;'
            f'font-size:0.78rem;white-space:nowrap;border:1px solid #30363d;">{comp}</div>'
        )
    out += '</div>'
    return out

def miss_card(name, price, brand, size, ptype, comp, suggested_price,
              note, variant_html, tester_badge, border_color,
              confidence_level, confidence_score, product_id):
    _cl = str(confidence_level or "").lower()
    _conf_ar = {"green": "ثقة قوية ✅", "yellow": "ثقة متوسطة ⚠️", "red": "مشكوك ❌"}.get(
        _cl, str(confidence_level or "—")
    )
    return f"""
    <div class="miss-card" style="border-left-color:{border_color}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
                <div style="font-weight:bold;font-size:1.05rem;">{tester_badge} {name}
                    <span style="color:#8b949e;font-size:0.8rem;">({product_id})</span>
                </div>
                <div style="color:#8b949e;font-size:0.82rem;margin-top:3px;">{brand} | {size} | {ptype}</div>
            </div>
            <div style="text-align:right;flex-shrink:0;margin-left:10px;">
                <div style="font-size:1.15rem;font-weight:bold;">{price} ر.س</div>
                <div style="color:#3fb950;font-size:0.88rem;">المقترح: {suggested_price} ر.س</div>
            </div>
        </div>
        <div style="margin-top:8px;font-size:0.82rem;color:#8b949e;">
            المنافس: <b style="color:#c9d1d9;">{comp}</b> |
            درجة ثقة المطابقة: <b>{_conf_ar}</b> ({confidence_score}%)
        </div>
        {variant_html}
        {f'<div style="margin-top:6px;color:#ffd600;font-style:italic;font-size:0.85rem;">{note}</div>' if note else ''}
    </div>
    """
