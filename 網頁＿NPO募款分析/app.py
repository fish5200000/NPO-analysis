import streamlit as st
import pandas as pd
import time

# --- 1. 頁面設定 (UI 基礎) ---
st.set_page_config(
    page_title="NPO 募款策略戰情室",
    page_icon="💡",
    layout="wide"  # 寬螢幕模式，看起來更像專業後台
)

# --- 2. 左側邊欄 (控制區) ---
with st.sidebar:
    st.title("🎛️ 戰情控制台")
    st.markdown("---")
    
    # 輸入框
    org_name = st.text_input("輸入組織名稱", placeholder="例如：兒福聯盟")
    
    # 多選設定
    target_market = st.multiselect(
        "鎖定目標受眾",
        ["企業 CSR", "親子族群", "退休人員", "年輕 Z 世代"],
        ["親子族群"]
    )
    
    # 啟動按鈕
    analyze_btn = st.button("🚀 開始搜尋與分析", type="primary") # type="primary" 會讓按鈕變顯眼顏色
    
    st.markdown("---")
    st.caption("Powered by Gemini & Python")

# --- 3. 主畫面 (顯示區) ---
st.title("📊 募款行銷情報儀表板")
st.markdown(f"針對 **{org_name if org_name else '尚未輸入'}** 的 AI 自動化分析報告")

if analyze_btn and org_name:
    # 模擬 AI 正在工作的進度條 (UI 互動感)
    with st.status("正在連線至 Google 搜尋資料...", expanded=True) as status:
        st.write("🔍 正在掃描相關新聞...")
        time.sleep(1) # 假裝在跑
        st.write("🧠 AI 正在分析競品策略...")
        time.sleep(1)
        st.write("📝 正在生成策略建議...")
        time.sleep(0.5)
        status.update(label="分析完成！", state="complete", expanded=False)

    # --- UI 區塊：關鍵指標 (Metrics) ---
    col1, col2, col3 = st.columns(3)
    col1.metric("網路討論熱度", "高 🔥", "與上月相比 +12%")
    col2.metric("預估競品數量", "3 家", "主要為同性質 NPO")
    col3.metric("建議募款急迫性", "中等", "避開選舉議題")

    st.markdown("---")

    # --- UI 區塊：分頁籤 (Tabs) ---
    tab1, tab2, tab3 = st.tabs(["🌍 外部環境 PESTEL", "⚔️ 競品分析", "💡 策略建議"])

    with tab1:
        st.subheader("外部環境掃描")
        st.info("💡 **機會點：** 政府剛宣布加碼心理衛生預算，民眾關注度提升。")
        st.warning("⚠️ **威脅點：** 通膨導致小額捐款意願下降。")
        
        # 使用 Expander 收合詳細資料，讓介面乾淨
        with st.expander("查看詳細 PESTEL 分析報告"):
            st.markdown("""
            * **Political:** 新法案通過...
            * **Economic:** 股市波動影響...
            * **Social:** 社會對於兒少保護意識抬頭...
            """)

    with tab2:
        st.subheader("競品雷達偵測")
        # 模擬表格數據
        df = pd.DataFrame({
            "競品名稱": ["競品 A", "競品 B", "競品 C"],
            "核心訴求": ["用愛擁抱", "看見改變", "即刻救援"],
            "贈品策略": ["環保餐具", "聯名悠遊卡", "電子感謝狀"],
            "廣告渠道": ["Facebook", "Instagram", "Podcast"]
        })
        st.dataframe(df, use_container_width=True) # 讓表格填滿寬度

    with tab3:
        st.subheader("AI 策略建議")
        st.success(f"針對 {target_market} 的募款建議：")
        st.markdown(f"""
        1. **主要訊息：** 強調「專款專用」與「透明度」。
        2. **渠道建議：** 由於鎖定 {target_market}，建議投入 60% 預算在 LINE OA 經營。
        3. **行動呼籲 (CTA)：** 「每天 10 元，成為孩子的守護者」。
        """)

elif analyze_btn and not org_name:
    st.error("請先在左側輸入組織名稱！")

else:
    # 尚未開始時的空狀態 (Empty State)
    st.info("👈 請從左側輸入資料並點擊按鈕開始分析")