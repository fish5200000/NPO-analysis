import streamlit as st
# 你需要安裝 langchain 或使用 google search api 來實作真的搜尋功能
# 這裡展示介面邏輯

st.set_page_config(page_title="NPO 募款戰情室", layout="wide")

st.title("🚀 NPO 募款策略 AI 戰情室")
st.markdown("輸入組織名稱，AI 將自動協助您完成行銷環境掃描與競品分析。")

# 側邊欄輸入
with st.sidebar:
    org_name = st.text_input("輸入組織名稱或是議題", "例如：兒福聯盟")
    run_btn = st.button("開始分析")

# 主要分析區
if run_btn:
    with st.spinner(f'正在搜尋關於 {org_name} 的市場資料...'):
        # 這裡通常會接上你的 n8n webhook 或是 OpenAI API
        # 模擬 AI 搜尋回傳的結果
        
        st.success("分析完成！")
        
        # 第一部分：外部環境
        st.header("1. 🔍 外部環境掃描 (PESTEL)")
        col1, col2 = st.columns(2)
        with col1:
            st.info("**政策機會 (Political)**")
            st.write(f"目前政府針對 {org_name} 相關領域的補助政策包含...")
        with col2:
            st.warning("**社會趨勢 (Social)**")
            st.write("近期新聞熱議話題集中在...")

        # 第二部分：競品分析
        st.header("2. ⚔️ 競品雷達")
        data = {
            "競品名稱": ["競品A", "競品B"],
            "核心訴求": ["讓愛傳遞", "看見改變"],
            "募款贈品": ["環保袋", "悠遊卡"],
            "廣告渠道": ["FB, IG", "Youtube"]
        }
        st.table(data)

        # 第三部分：策略建議
        st.header("3. 💡 下一步策略")
        st.markdown("""
        * **受眾定位：** 建議鎖定 35-45 歲族群。
        * **核心訊息：** 強調「透明度」與「直接影響力」。
        """)