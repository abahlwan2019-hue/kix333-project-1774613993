import streamlit as st
import pandas as pd
import math
import html as html_lib

PLACEHOLDER_IMG = "https://placehold.co/200x180/1a1a2e/8b949e?text=No+Image"
MAHWOUS_URL = "https://mahwous.com/"


def _safe_img_url(raw) -> str:
    if raw is None:
        return PLACEHOLDER_IMG
    s = str(raw).strip()
    if s.startswith("http") and "via.placeholder" not in s and s != "nan":
        return s
    return PLACEHOLDER_IMG


def render_product_cards(df: pd.DataFrame, items_per_page: int = 15):
    if df.empty:
        st.warning("لا توجد بيانات لعرضها.")
        return

    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    st.markdown("### 🔍 أدوات التحكم والبحث")
    col_search, col_filter = st.columns([2, 1])
    with col_search:
        search_query = st.text_input("ابحث عن منتج (بالاسم أو SKU):", "").strip().lower()
    with col_filter:
        filter_options = ["الكل"]
        if "action_required" in df.columns:
            filter_options.extend(df["action_required"].dropna().unique().tolist())
        selected_filter = st.selectbox("تصفية حسب الحالة:", filter_options)

    filtered_df = df.copy()
    if search_query:
        nm = filtered_df.get("name", pd.Series(dtype=str)).astype(str).str.lower().str.contains(search_query, na=False)
        sk = filtered_df.get("sku",  pd.Series(dtype=str)).astype(str).str.lower().str.contains(search_query, na=False)
        filtered_df = filtered_df[nm | sk]
    if selected_filter != "الكل" and "action_required" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["action_required"] == selected_filter]

    total_items = len(filtered_df)
    if total_items == 0:
        st.info("لم يتم العثور على منتجات تطابق بحثك.")
        return

    total_pages = max(math.ceil(total_items / items_per_page), 1)
    if st.session_state.current_page > total_pages:
        st.session_state.current_page = 1

    start_idx = (st.session_state.current_page - 1) * items_per_page
    page_df   = filtered_df.iloc[start_idx : start_idx + items_per_page]

    st.markdown("""<style>
    .pc{background:linear-gradient(145deg,#161b22,#1c2330);border-radius:14px;
        box-shadow:0 4px 14px rgba(0,0,0,.4);padding:16px;margin-bottom:16px;
        border:1px solid #30363d;display:flex;flex-direction:column;
        justify-content:space-between;min-height:420px;
        transition:transform .2s,box-shadow .2s;}
    .pc:hover{transform:translateY(-3px);box-shadow:0 8px 22px rgba(0,0,0,.55);border-color:#58a6ff44;}
    .pc-img{width:100%;height:170px;object-fit:contain;border-radius:10px;
            margin-bottom:10px;background:#0d1117;border:1px solid #21262d;}
    .pc-title{font-size:14px;font-weight:700;color:#e6edf3;margin-bottom:6px;
              line-height:1.45;display:-webkit-box;-webkit-line-clamp:2;
              -webkit-box-orient:vertical;overflow:hidden;min-height:40px;}
    .pc-sku{font-size:11px;color:#6e7681;margin-bottom:10px;}
    .pc-prices{display:flex;justify-content:space-between;align-items:center;
               background:#0d1117;padding:10px 12px;border-radius:10px;
               margin-bottom:10px;border:1px solid #21262d;}
    .pc-pc{text-align:center;width:48%;}
    .pc-plbl{font-size:10px;color:#8b949e;font-weight:600;text-transform:uppercase;letter-spacing:.4px;}
    .pc-pval{font-size:16px;font-weight:800;color:#c9d1d9;margin-top:2px;}
    .pc-sval{font-size:16px;font-weight:800;color:#3fb950;margin-top:2px;}
    .pc-divv{width:1px;background:#30363d;align-self:stretch;}
    .pc-comp{padding-top:10px;border-top:1px dashed #30363d;font-size:13px;text-align:center;}
    .ch{color:#f85149;font-weight:700;} .cl{color:#3fb950;font-weight:700;} .cn{color:#8b949e;}
    .pc-link{display:block;margin-top:7px;font-size:11px;color:#58a6ff;
             text-decoration:none;text-align:center;}
    .pc-link:hover{text-decoration:underline;}
    </style>""", unsafe_allow_html=True)

    st.markdown(
        f"<p style='color:#8b949e;font-size:13px;'>نعرض <b style='color:#e6edf3;'>{len(page_df)}</b> "
        f"من أصل <b style='color:#e6edf3;'>{total_items}</b> منتج</p>",
        unsafe_allow_html=True,
    )

    cols_per_row = 3
    for i in range(0, len(page_df), cols_per_row):
        cols  = st.columns(cols_per_row)
        chunk = page_df.iloc[i : i + cols_per_row]
        for ci, (_, row) in enumerate(chunk.iterrows()):
            with cols[ci]:
                name       = html_lib.escape(str(row.get("name", "منتج")))
                img_url    = _safe_img_url(row.get("image_url"))
                my_p       = float(row.get("price", 0) or 0)
                sug_p      = float(row.get("suggested_price", 0) or 0)
                comp_p     = float(row.get("comp_price", 0) or 0)
                sku        = html_lib.escape(str(row.get("sku", ci)))
                prod_url   = str(row.get("url", row.get("product_url", ""))).strip()

                if comp_p == 0:
                    comp_html = "<span class='cn'>سعر المنافس: غير متوفر ➖</span>"
                elif comp_p > my_p:
                    comp_html = f"<span class='cl'>المنافس: {comp_p:.0f} ر.س 🔺 <small>(أعلى بـ {comp_p-my_p:.0f})</small></span>"
                elif comp_p < my_p:
                    comp_html = f"<span class='ch'>المنافس: {comp_p:.0f} ر.س 🔻 <small>(أقل بـ {my_p-comp_p:.0f})</small></span>"
                else:
                    comp_html = f"<span class='cn'>المنافس: {comp_p:.0f} ر.س ➖ مطابق</span>"

                link_href  = html_lib.escape(prod_url) if prod_url.startswith("http") else MAHWOUS_URL
                link_label = "🔗 عرض على مهووس" if prod_url.startswith("http") else "🔗 متجر مهووس"

                st.markdown(f"""
                <div class="pc">
                  <div>
                    <img src="{img_url}" class="pc-img"
                         onerror="this.src='{PLACEHOLDER_IMG}'" loading="lazy">
                    <div class="pc-title" title="{name}">{name}</div>
                    <div class="pc-sku">SKU: {sku}</div>
                  </div>
                  <div>
                    <div class="pc-prices">
                      <div class="pc-pc">
                        <div class="pc-plbl">سعري الحالي</div>
                        <div class="pc-pval">{my_p:.0f} <small style="font-size:10px;color:#8b949e;">ر.س</small></div>
                      </div>
                      <div class="pc-divv"></div>
                      <div class="pc-pc">
                        <div class="pc-plbl">المقترح</div>
                        <div class="pc-sval">{sug_p:.0f} <small style="font-size:10px;color:#3fb950;">ر.س</small></div>
                      </div>
                    </div>
                    <div class="pc-comp">
                      {comp_html}
                      <a class="pc-link" href="{link_href}" target="_blank">{link_label}</a>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)

                if st.button(f"🚀 اعتماد {sug_p:.0f} ر.س", key=f"btn_{sku}_{i}_{ci}", use_container_width=True):
                    st.toast(f"✅ تم إرسال تحديث المنتج {sku}!", icon="✅")

    st.markdown("---")
    p1, p2, p3 = st.columns([1, 2, 1])
    with p1:
        if st.button("⬅️ السابقة", disabled=(st.session_state.current_page == 1), use_container_width=True):
            st.session_state.current_page -= 1
            st.rerun()
    with p2:
        st.markdown(
            f"<div style='text-align:center;padding-top:8px;font-weight:bold;color:#e6edf3;'>"
            f"الصفحة {st.session_state.current_page} من {total_pages}</div>",
            unsafe_allow_html=True,
        )
    with p3:
        if st.button("التالية ➡️", disabled=(st.session_state.current_page == total_pages), use_container_width=True):
            st.session_state.current_page += 1
            st.rerun()
