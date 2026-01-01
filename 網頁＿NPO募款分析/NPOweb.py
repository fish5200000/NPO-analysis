import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS
import pandas as pd
import json
import time

# --- 1. 頁面設定 ---
st.set_page_config(page_title="NPO 募款戰情室", page_icon="🚀", layout="wide")

# --- 2. 設定 Gemini API ---
# 確保你在 Streamlit Cloud 的 Secrets 裡有設定 GEMINI_API_KEY
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ 尚未設定 API Key！請去 Streamlit Cloud 後台設定 Secrets。")
    st.stop()

# --- 3. 定義功能函數 ---

def search_web(keyword):
    """使用 DuckDuckGo 搜尋網路資料 (增加防擋機制)"""
    results_text = ""
    try:
        with DDGS() as ddgs:
            # 簡化搜尋字串，減少被擋機率
            queries = [f"{keyword} 募款 爭議 新聞", f"{keyword} 行銷"]
            for q in queries:
                results = list(ddgs.text(q, max_results=2))
                if results:
                    for r in results:
                        results_text += f"標題: {r['title']}\n摘要: {r['body']}\n連結: {r['href']}\n\n"
                time.sleep(0.5)
    except Exception as e:
        print(f"搜尋模組回報: {e}")
    
    return results_text

def analyze_data(org_name, search_results):
    """呼叫 Gemini 分析資料"""
    
    # 使用目前最穩定的模型名稱
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 判斷是否有搜尋到資料
    if not search_results or len(search_results) < 50:
        source_note = "⚠️ 注意：因網路爬蟲被阻擋，以下分析是基於 AI 內建知識庫。"
        search_data_prompt = "（網路搜尋無結果，請用你已知的知識進行分析）"
    else:
        source_note = "✅ 分析依據：包含網路實時搜尋資料。"
        search_data_prompt = search_results

    prompt = f"""
    你是一位專業的行銷顧問。請分析「{org_name}」的募款狀況。
    
    【參考資料】：
    {search_data_prompt}
    
    【任務】：
    請嚴格輸出純 JSON 格式，不要包含 Markdown 標記（如 ```json），格式如下：
    {{
        "pestel": {{
            "political": "政策相關發現...",
            "social": "社會輿論發現..."
        }},
        "competitors": [
            {{"name": "競品A", "slogan": "核心訴求...", "channel": "廣告渠道..."}},
            {{"name": "競品B", "slogan": "核心訴求...", "channel": "廣告渠道..."}}
        ],
        "strategy": "給該組織的具體募款建議..."
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text), source_note
    except Exception as e:
        return None, f"AI 分析發生錯誤: {str(e)}"

# --- 4. 前端介面 UI ---

with st.sidebar:
    st.title("🎛️ 戰情控制台")
    org_name = st.text_input("輸入組織名稱", "兒福聯盟")
    run_btn = st.button("🚀 啟動 AI 全網分析", type="primary")
    st.caption("Powered by Gemini 1.5 Flash")

st.title("🚀 NPO 募款策略 AI 戰情室")
st.markdown("輸入組織名稱，AI 將協助您完成行銷環境掃描與競品分析。")

if run_btn and org_name:
    with st.status("🤖 AI 正在工作中...", expanded=True) as status:
        st.write("🔍 嘗試連線網路資料庫...")
        raw_data = search_web(org_name)
        
        st.write("🧠 正在進行策略運算...")
        analysis, note = analyze_data(org_name, raw_data)
        
        if analysis:
            status.update(label="✅ 分析完成！", state="complete", expanded=False)
        else:
            status.update(label="❌ 發生錯誤", state="error")
            st.error(note)
            st.stop()

    # 顯示資料來源狀態
    if "⚠️" in note:
        st.warning(note)
    else:
        st.success(note)

    # 呈現結果
    if analysis:
        # PESTEL 區塊
        st.header("1. 🌍 外部環境掃描 (PESTEL)")
        col1, col2 = st.columns(2)
        with col1:
            st.info("**🏛️ 政策與經濟**")
            st.write(analysis.get('pestel', {}).get('political', '無資料'))
        with col2:
            st.warning("**🗣️ 社會輿論**")
            st.write(analysis.get('pestel', {}).get('social', '無資料'))

        # 競品區塊
        st.header("2. ⚔️ 競品雷達")
        comps = analysis.get('competitors', [])
        if comps:
            df = pd.DataFrame(comps)
            st.table(df)
        else:
            st.write("無競品資料")

        # 策略建議區塊
        st.header("3. 💡 下一步策略")
        st.success(analysis.get('strategy', '無建議'))

elif run_btn:
    st.warning("請輸入組織名稱！")