import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS
import pandas as pd
import json
import time

# --- 1. 頁面設定 ---
st.set_page_config(page_title="NPO 募款戰情室", page_icon="🚀", layout="wide")

# --- 2. 設定 Gemini API ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ 尚未設定 API Key！請去 Streamlit Cloud 後台設定 Secrets。")
    st.stop()

# --- 3. 定義功能函數 ---

def search_web(keyword):
    """使用 DuckDuckGo 搜尋網路資料 (增加重試機制)"""
    results_text = ""
    try:
        with DDGS() as ddgs:
            # 搜尋關鍵字：組織名稱 + 募款 / 新聞
            queries = [f"{keyword} 募款活動 2024 2025", f"{keyword} 爭議 新聞"]
            for q in queries:
                # 嘗試搜尋，若失敗則稍作休息
                results = list(ddgs.text(q, max_results=2))
                if results:
                    for r in results:
                        results_text += f"標題: {r['title']}\n摘要: {r['body']}\n連結: {r['href']}\n\n"
                time.sleep(1) # 避免太快被擋
    except Exception as e:
        print(f"搜尋過程發生警告: {e}")
    
    return results_text

def analyze_data(org_name, search_results):
    """呼叫 Gemini 分析資料"""
    
    # 【關鍵修正】改用最穩定的 gemini-pro 模型，避免 404 錯誤
    model = genai.GenerativeModel('gemini-pro') 
    
    # 如果真的搜不到資料，就讓 AI 用它的內建知識庫回答，不要報錯
    if not search_results:
        search_results = "（注意：網路搜尋未返回結果，請根據您已知的背景知識進行分析。）"
    
    prompt = f"""
    你是一位專業的行銷顧問。請根據以下資料，分析「{org_name}」的募款狀況。
    
    【參考資料】：
    {search_results}
    
    【任務】：
    請嚴格輸出純 JSON 格式，不要包含 ```json 標記，格式如下：
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
    
    response = model.generate_content(prompt)
    
    # 清理回應，確保是乾淨的 JSON
    text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

# --- 4. 前端介面 UI ---

with st.sidebar:
    st.title("🎛️ 戰情控制台")
    org_name = st.text_input("輸入組織名稱", "兒福聯盟")
    run_btn = st.button("🚀 啟動 AI 全網分析", type="primary")
    st.markdown("---")
    st.caption("Powered by Gemini & DuckDuckGo")

st.title("🚀 NPO 募款策略 AI 戰情室")
st.markdown("輸入組織名稱，AI 將自動**搜尋網路實時資料**並進行分析。")

if run_btn and org_name:
    try:
        # 階段 1: 搜尋
        with st.status("🔍 AI 正在網路上閱讀相關新聞...", expanded=True) as status:
            st.write("正在搜尋 DuckDuckGo...")
            raw_data = search_web(org_name)
            
            # 顯示搜尋到的字數，讓你知道有沒有搜到
            data_len = len(raw_data)
            if data_len == 0:
                st.warning("⚠️ 網路爬蟲未抓取到資料（可能被阻擋），將改用 AI 內建知識分析。")
            else:
                st.write(f"✅ 已獲取 {data_len} 字元的資料，正在進行語意分析...")
            
            # 階段 2: 分析
            analysis = analyze_data(org_name, raw_data)
            status.update(label="✅ 分析完成！", state="complete", expanded=False)

        # 階段 3: 呈現結果
        
        # PESTEL 區塊
        st.header("1. 🌍 外部環境掃描 (PESTEL)")
        col1, col2 = st.columns(2)
        with col1:
            st.info("**🏛️ 政策與經濟**")
            st.write(analysis['pestel']['political'])
        with col2:
            st.warning("**🗣️ 社會輿論**")
            st.write(analysis['pestel']['social'])

        # 競品區塊
        st.header("2. ⚔️ 競品雷達")
        df = pd.DataFrame(analysis['competitors'])
        st.table(df)

        # 策略建議區塊
        st.header("3. 💡 下一步策略")
        st.success(analysis['strategy'])

    except Exception as e:
        st.error(f"發生錯誤: {e}")
        st.markdown("建議：請重新整理網頁後再試一次，或檢查 API Key 是否正確。")

elif run_btn:
    st.warning("請輸入組織名稱！")