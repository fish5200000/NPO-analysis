import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS
import pandas as pd
import json
import time
import random

# --- 1. 頁面基礎設定 ---
st.set_page_config(
    page_title="NPO 募款策略顧問", 
    page_icon="💎", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. 設定 Gemini API ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ 請先在 Streamlit Cloud 設定 Secrets: GEMINI_API_KEY")
    st.stop()

# --- 3. 核心搜尋引擎 (針對四大面向) ---

def search_web_structured(org_name):
    """
    執行 Gem 指令中的四大搜尋重點：自身活動、競品、輿情、政策
    """
    results_data = []
    
    # 這裡對應原本指令的「步驟 1：啟動 Google 搜尋」
    search_queries = [
        # 1. 自身剖析 (Recent Activity)
        f"{org_name} 募款活動 新聞 2024 2025 成效",
        # 2. 社會輿論 (Sentiment - PTT/Dcard)
        f"{org_name} 評價 PTT Dcard 爭議 討論",
        # 3. 政策與環境 (PESTEL - Policy/Social)
        f"台灣 公益團體 募款 法規 政策 趨勢 2025",
        # 4. 競爭對手 (Competitors)
        f"{org_name} 競爭對手 類似組織 募款案例"
    ]

    try:
        with DDGS() as ddgs:
            for query in search_queries:
                # 每個角度抓取 2 筆最相關的
                results = list(ddgs.text(query, max_results=2))
                if results:
                    for r in results:
                        results_data.append(f"【來源】{r['title']}\n{r['body']}\n(連結: {r['href']})")
                time.sleep(random.uniform(0.5, 1.0)) # 隨機延遲，模擬人類行為
    except Exception as e:
        print(f"搜尋警告: {e}")
    
    return "\n\n".join(results_data)

def analyze_with_gem_logic(org_name, search_context):
    """
    完全依照 Gem 指令的 Prompt 邏輯進行分析
    """
    # 使用目前權限最高的模型
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    # 這是你提供的原始指令架構，我將其轉化為 Prompt
    prompt = f"""
    你是一位資深的非營利組織（NPO）募款策略顧問。
    使用者的輸入組織為：「{org_name}」。
    
    請根據下方的【真實搜尋資料】，產出一份募款行銷架構分析。
    
    【真實搜尋資料】：
    {search_context}

    【輸出規定】：
    請嚴格依照以下 JSON 格式回傳 (不要 Markdown 標記)，以利系統生成圖表：
    {{
        "self_analysis": {{
            "recent_activity": "該組織近期的主要活動或新聞摘要",
            "public_sentiment": "目前的網路輿論風向 (PTT/Dcard/新聞熱度)"
        }},
        "pestel": {{
            "policy_economic": "政策(P)與經濟(E)的重點發現 (補助/法規/景氣)",
            "social": "社會(S)趨勢與輿論熱點",
            "opportunity_judgment": "機會點判定 (現在適合募款嗎？為什麼？)"
        }},
        "competitors": [
            {{"name": "競品A", "slogan": "核心訴求", "gift": "募款贈品/回饋", "channel": "行銷渠道"}},
            {{"name": "競品B", "slogan": "核心訴求", "gift": "募款贈品/回饋", "channel": "行銷渠道"}}
        ],
        "strategy": {{
            "target_audience": "建議目標受眾 (具體族群)",
            "pain_points": "受眾痛點洞察 (為什麼捐款?)",
            "action_plan": [
                "具體建議1",
                "具體建議2",
                "具體建議3"
            ]
        }}
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        return None

# --- 4. 前端介面 UI ---

with st.sidebar:
    st.title("🎛️ 顧問控制台")
    st.markdown("---")
    org_name = st.text_input("輸入組織名稱或議題", "兒福聯盟")
    run_btn = st.button("🚀 啟動顧問分析", type="primary")
    st.caption("架構：PESTEL + 競品雷達 + 策略建議")

# 主標題
st.title("💎 NPO 募款策略顧問")
st.markdown("本系統將模擬資深顧問思維，結合 **Google 搜尋** 與 **Gemini 邏輯推演**，為您產出架構化報告。")

if run_btn and org_name:
    # 執行狀態
    with st.status("🔍 顧問正在工作中...", expanded=True) as status:
        
        st.write(f"1. 正在調查「{org_name}」的近期活動與網路評價 (PTT/Dcard)...")
        # 搜尋邏輯已更新：包含自身剖析
        search_data = search_web_structured(org_name)
        time.sleep(1)
        
        st.write("2. 正在掃描外部政策環境與競爭對手...")
        
        st.write("3. 正在撰寫分析報告...")
        analysis = analyze_with_gem_logic(org_name, search_data)
        
        if analysis:
            status.update(label="✅ 報告生成完畢！", state="complete", expanded=False)
        else:
            status.update(label="❌ 分析失敗", state="error")
            st.error("AI 無法生成 JSON，請重試。")
            st.stop()

    # --- 報告呈現區 (依照你要求的 Markdown 格式轉化為 UI) ---

    # 0. 自身剖析 (新增區塊)
    st.header(f"0. 🔎 關於 {org_name} 的現況掃描")
    self_data = analysis.get('self_analysis', {})
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.info("**📰 近期活動/新聞**")
        st.write(self_data.get('recent_activity', '無顯著資料'))
    with col_s2:
        st.warning("**🗣️ 網路輿論 (PTT/Dcard)**")
        st.write(self_data.get('public_sentiment', '無顯著資料'))

    st.divider()

    # 1. PESTEL 分析
    st.header("1. 📊 外部環境掃描 (PESTEL)")
    pestel = analysis.get('pestel', {})
    
    st.markdown("#### **🏛️ 政策 (P) & 經濟 (E)**")
    st.write(pestel.get('policy_economic', ''))
    
    st.markdown("#### **🔥 社會 (S)**")
    st.write(pestel.get('social', ''))
    
    st.markdown("#### **💡 機會點判定**")
    st.success(pestel.get('opportunity_judgment', ''))

    st.divider()

    # 2. 競品雷達
    st.header("2. ⚔️ 競品雷達偵測")
    comps = analysis.get('competitors', [])
    if comps:
        # 轉成乾淨的表格
        df = pd.DataFrame(comps)
        # 重新命名欄位以符合顯示
        df = df.rename(columns={
            "name": "競品名稱",
            "slogan": "核心訴求 (Slogan)",
            "gift": "募款贈品/回饋",
            "channel": "行銷渠道"
        })
        st.table(df)
    else:
        st.write("未搜尋到明確競品資料。")

    st.divider()

    # 3. 策略建議
    st.header("3. 🎯 受眾與策略建議")
    strategy = analysis.get('strategy', {})
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👥 建議目標受眾")
        st.write(strategy.get('target_audience', ''))
    with col2:
        st.subheader("💔 痛點洞察")
        st.write(strategy.get('pain_points', ''))
    
    st.subheader("🚀 下一步行動 (CTA)")
    actions = strategy.get('action_plan', [])
    for idx, action in enumerate(actions):
        st.markdown(f"**{idx+1}. {action}**")

    # 4. 資料來源 (確保有憑有據)
    with st.expander("📚 點此查看原始搜尋來源與證據"):
        st.text(search_data)

elif run_btn:
    st.toast("請輸入組織名稱！", icon="⚠️")