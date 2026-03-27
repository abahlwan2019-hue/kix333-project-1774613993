import json
import os
import threading

import pandas as pd
import streamlit as st

from utils.sitemap_resolve import resolve_store_to_sitemap_url

_SCRAPER_PROGRESS = os.path.join("data", "scraper_progress.json")

COMPETITORS_FILE = "data/competitors_list.json"
# مرجع متجرنا
PRIMARY_STORE_SITEMAP = "https://mahwous.com/sitemap.xml"
PRIMARY_STORE_LABEL   = "مهووس — متجرنا"
PRIMARY_STORE_URL     = "https://mahwous.com/"
PRIMARY_STORE_MAPS    = "https://maps.app.goo.gl/mahwous"   # ← استبدل بالرابط الفعلي

# ─────────────────────────────────────────────────────────────
# قائمة المنافسين الافتراضية (تُستخدم عند الإنشاء الأول فقط)
# ─────────────────────────────────────────────────────────────
DEFAULT_COMPETITORS = [
    "https://saeedsalah.com/sitemap.xml",
    "https://vanilla.sa/sitemap.xml",
    "https://sara-makeup.com/sitemap.xml",
    "https://alkhabeershop.com/sitemap.xml",
    "https://leesanto.com/sitemap.xml",
    "https://azalperfume.com/sitemap.xml",
    "https://candyniche.com/sitemap.xml",
    "https://luxuryperfumesnish.com/sitemap.xml",
    "https://hanan-store55.com/sitemap.xml",
    "https://areejamwaj.com/sitemap.xml",
    "https://niche.sa/sitemap.xml",
    "https://worldgivenchy.com/ar/sitemap.xml",
    "https://sarahmakeup37.com/sitemap.xml",
    "https://aromaticcloud.com/sitemap.xml",
]

# أسماء عرض للمنافسين (اختياري — للشريط الجانبي)
COMPETITOR_LABELS = {
    "saeedsalah.com":          "سعيد صلاح",
    "vanilla.sa":              "فانيلا",
    "sara-makeup.com":         "سارا ميكب",
    "alkhabeershop.com":       "خبير العطور",
    "leesanto.com":            "لي سانتو",
    "azalperfume.com":         "آزال",
    "candyniche.com":          "كاندي نيش",
    "luxuryperfumesnish.com":  "الفاخرة للنيش",
    "hanan-store55.com":       "حنان العطور",
    "areejamwaj.com":          "اريج امواج",
    "niche.sa":                "نيش",
    "worldgivenchy.com":       "عالم جيفنشي",
    "sarahmakeup37.com":       "ساره ستور",
    "aromaticcloud.com":       "اروماتيك كلاود",
}


def load_competitors():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(COMPETITORS_FILE):
        with open(COMPETITORS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_COMPETITORS, f, ensure_ascii=False, indent=4)
        return list(DEFAULT_COMPETITORS)
    try:
        with open(COMPETITORS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_competitors(competitors_list):
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(COMPETITORS_FILE, "w", encoding="utf-8") as f:
        json.dump(competitors_list, f, ensure_ascii=False, indent=4)


def _store_banner():
    """بانر متجر مهووس الرئيسي مع رابط الموقع."""
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#1a1f2e,#161b22);
                    border:1px solid #30363d;border-radius:12px;
                    padding:13px 18px;margin-bottom:16px;
                    display:flex;align-items:center;gap:14px;">
            <span style="font-size:1.6rem;flex-shrink:0;">🏠</span>
            <div style="flex:1;">
                <strong style="color:#e6edf3;font-size:1rem;">متجرنا الرئيسي — مهووس</strong>
                <div style="margin-top:5px;display:flex;flex-wrap:wrap;gap:14px;">
                    <a href="{PRIMARY_STORE_URL}" target="_blank"
                       style="color:#58a6ff;font-size:0.85rem;text-decoration:none;">
                       🔗 mahwous.com — زيارة المتجر
                    </a>
                    <a href="{PRIMARY_STORE_SITEMAP}" target="_blank"
                       style="color:#8b949e;font-size:0.82rem;text-decoration:none;">
                       🗺️ خريطة الموقع (Sitemap)
                    </a>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_competitor_management_ui():
    st.markdown("## 🏢 إدارة روابط المنافسين (Sitemaps)")
    st.info(
        "أدخل **رابط المتجر** (مثل `https://mahwous.com/`) أو **رابط Sitemap مباشر**. "
        "التطبيق يستنتج تلقائياً ملف الـ sitemap الصحيح من `robots.txt` أو المسارات الشائعة."
    )

    competitors = load_competitors()

    with st.form("add_competitor_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_url = st.text_input(
                "رابط المتجر أو Sitemap:",
                placeholder="https://example.com/",
            )
        with col2:
            st.write("")
            st.write("")
            submitted = st.form_submit_button("➕ إضافة", use_container_width=True)

        if submitted:
            if not (new_url and new_url.strip()):
                st.error("الرجاء إدخال رابط.")
            else:
                resolved, msg = resolve_store_to_sitemap_url(new_url.strip())
                if not resolved:
                    st.error(msg)
                elif resolved in competitors:
                    st.warning("هذا الرابط مضاف مسبقاً.")
                else:
                    competitors.append(resolved)
                    save_competitors(competitors)
                    st.success(f"تمت الإضافة بنجاح! {msg}")
                    st.rerun()

    st.markdown(f"### 📋 قائمة المنافسين الحاليين ({len(competitors)})")
    if not competitors:
        st.warning("لم تقم بإضافة أي منافسين بعد.")
    else:
        for idx, url in enumerate(competitors):
            # استخراج اسم عرض
            domain = url.split("/")[2] if "//" in url else url
            label  = COMPETITOR_LABELS.get(domain, domain)
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.code(url)
            with c2:
                store_link = url.replace("/sitemap.xml", "").replace("/ar/sitemap.xml", "")
                st.markdown(
                    f'<a href="{store_link}" target="_blank" '
                    f'style="font-size:0.82rem;color:#58a6ff;text-decoration:none;">'
                    f'🔗 {label}</a>',
                    unsafe_allow_html=True,
                )
            with c3:
                if st.button("🗑️ حذف", key=f"del_{idx}", use_container_width=True):
                    competitors.pop(idx)
                    save_competitors(competitors)
                    st.rerun()


def render_competitor_scrape_page():  # noqa: C901
    """صفحة كاملة: إدارة روابط المنافسين + كشط مع حفظ وعرض تدريجي."""
    st.header("🏢 كشط المنافسين")

    # ── بانر متجرنا الرئيسي ──────────────────────────────────
    _store_banner()

    st.caption(
        f"**{PRIMARY_STORE_LABEL}** = مرجع ملف منتجاتك (رفع من «📂 رفع الملفات») — "
        f"Sitemap المرجعي: `{PRIMARY_STORE_SITEMAP}`. أدناه **روابط كشط المنافسين فقط**."
    )
    st.success(
        "المنافسون المتاحون: **سعيد صلاح** · **فانيلا** · **سارا ميكب** · **خبير العطور** · "
        "**لي سانتو** · **آزال** · **كاندي نيش** · **الفاخرة للنيش** · **حنان العطور** · "
        "**اريج امواج** · **نيش** · **عالم جيفنشي** · **ساره ستور** · **اروماتيك كلاود**"
    )

    render_competitor_management_ui()

    st.markdown("---")
    st.subheader("🤖 تشغيل محرك الكشط وعرض النتائج")
    st.info(
        "يُجلب أحدث أسعار المنافسين من روابط الـ Sitemap أعلاه. **الكشط يعمل في الخلفية**؛ "
        "سترى تقدّم الطلبات وعدد الصفوف المحفوظة أثناء العمل، ثم الملخص عند الانتهاء."
    )

    prog_running = False
    prog: dict = {}
    if os.path.exists(_SCRAPER_PROGRESS):
        try:
            with open(_SCRAPER_PROGRESS, "r", encoding="utf-8") as _pf:
                prog = json.load(_pf)
            prog_running = bool(prog.get("running"))
        except Exception:
            pass

    if prog_running:
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=4000, key="competitor_scrape_autorefresh")
        except ImportError:
            pass
        st.warning("⏳ جاري سحب البيانات… يُحدَّث العرض كل بضع ثوانٍ حتى يكتمل.")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("تقدّم الطلبات",
                      f"{prog.get('urls_processed',0):,} / {max(prog.get('urls_total',0),1):,}")
        with c2:
            st.metric("صفوف محفوظة في CSV", f"{prog.get('rows_in_csv',0):,}")
        with c3:
            st.caption(f"Sitemap: `{prog.get('current_sitemap','—')}`")

    def _run_scraper_bg() -> None:
        import asyncio
        from utils.async_scraper import run_scraper_engine
        asyncio.run(run_scraper_engine())

    col_btn, _ = st.columns([1, 2])
    with col_btn:
        if st.button(
            "🚀 بدء جلب بيانات المنافسين الآن",
            use_container_width=True,
            disabled=prog_running,
            key="btn_start_scrape_page",
        ):
            threading.Thread(target=_run_scraper_bg, daemon=True).start()
            st.rerun()

    # ── ملخص آخر كشط ─────────────────────────────────────────
    meta_path = os.path.join(os.getcwd(), "data", "scraper_last_run.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as _mf:
                sm = json.load(_mf)
            st.markdown("### 📈 ملخص أداء آخر كشط")
            st.caption(
                f"آخر تحديث (UTC): `{sm.get('finished_at','—')}` · الحالة: **{sm.get('status','—')}**"
            )
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("روابط في الطابور",   f"{sm.get('urls_queued',0):,}")
            c2.metric("صفوف في CSV",         f"{sm.get('rows_written_csv',0):,}")
            c3.metric("نسبة النجاح",          f"{sm.get('success_rate_pct',0.0):.1f}%")
            c4.metric("المدة (ث)",             f"{sm.get('duration_seconds',0):.1f}")
            c5, c6, c7 = st.columns(3)
            c5.metric("قبل إزالة التكرار",    f"{sm.get('rows_extracted_before_dedupe',0):,}")
            c6.metric("طلبات فاشلة",           f"{sm.get('fetch_exceptions',0):,}")
            c7.metric("بدون استخراج",          f"{sm.get('parse_null',0):,}")
            diag = sm.get("sitemap_diagnostics") or []
            if diag:
                with st.expander("🔎 تشخيص روابط الـ Sitemap", expanded=False):
                    st.dataframe(pd.DataFrame(diag), use_container_width=True, hide_index=True)
        except Exception:
            pass

    # ── البيانات المسحوبة ─────────────────────────────────────
    st.markdown("### 📊 البيانات المسحوبة من المنافسين")
    data_path = os.path.join(os.getcwd(), "data", "competitors_latest.csv")
    if os.path.exists(data_path):
        try:
            df_comp = pd.read_csv(data_path)
            if df_comp.empty:
                st.warning("⚠️ الملف موجود لكنه فارغ. تحقق من الـ Sitemap أو انتظر أول دفعة.")
            else:
                st.success(f"✅ **{len(df_comp)}** صف محفوظ — يُحدَّث أثناء الكشط إن كان يعمل.")
                st.dataframe(df_comp, use_container_width=True, height=400)
                st.download_button(
                    "📥 تنزيل CSV",
                    data=df_comp.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
                    file_name="competitors_latest.csv",
                    mime="text/csv",
                    key="dl_competitors_csv_page",
                )
        except Exception as e:
            st.error(f"❌ حدث خطأ في قراءة ملف البيانات: {str(e)}")
    else:
        st.info(
            "لا يوجد ملف بعد. اضغط **بدء جلب** أعلاه — "
            "سيُنشأ `competitors_latest.csv` ويُملأ تدريجياً."
        )
