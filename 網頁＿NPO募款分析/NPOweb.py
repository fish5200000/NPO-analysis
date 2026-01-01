import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS
import pandas as pd
import json
import time

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="NPO 募款戰情室", 
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. 設定 Gemini API ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ 尚未設定 API Key！請去 Streamlit Cloud 後台設定 Secrets。")
    st.stop()

# --- 3. 核心功能函數 ---

def search_web(keyword):
    """搜尋網路資料 (DuckDuckGo)"""
    results_text = ""
    try:
        with DDGS() as ddgs:
            # 搜尋兩次以確保覆蓋率
            queries = [f"{keyword} 募款活動 爭議", f"{keyword} 行銷 競爭對手"]
            for q in queries:
                results = list(ddgs.text(q, max_results=2))
                if results:
                    for r in results:
                        results_text += f"標題: {r['title']}\n摘要: {r['body']}\n連結: {r['href']}\n\n"
                time.sleep(0.5) # 避免過快請求
    except Exception as e:
        print(f"搜尋警告: {e}")
    
    return results_text

def analyze_data(org_name, search_results):
    """呼叫 Gemini 2.5 分析資料"""
    
    # 【關鍵修正】使用你帳號清單中最強的 Flash 模型
    model_name = 'models/gemini-2.5-flash' 
    
    # 防呆：如果沒搜到資料，就用 AI 內建知識
    if not search_results or len(search_results) < 10:
        source_note = "⚠️ 網路爬蟲被阻擋或無新資料，分析將基於 AI 內建知識庫。"
        data_context = "（網路搜尋無結果，請用你已知的知識進行分析）"
    else:
        source_note = "✅ 分析依據：包含網路實時搜尋資料。"
        data_context = search_results

    # 建立模型
    model = genai.GenerativeModel(model_name)

    prompt = f"""
    你是一位專業的非營利組織(NPO)募款顧問。請分析「{org_name}」的行銷現況。
    
    【參考資料】：
    {data_context}
    
    【輸出規定】：
    請回傳嚴格的 JSON 格式，不要包含 Markdown (```json)，格式如下：
    {{
        "pestel": {{
            "opportunity": "外部機會點 (政策/社會趨勢)...",
            "threat": "外部威脅點 (經濟/競爭)..."
        }},
        "competitors": [
            {{"name": "競品A", "slogan": "核心訴求", "channel": "主要管道"}},
            {{"name": "競品B", "slogan": "核心訴求", "channel": "主要管道"}}
        ],
        "strategy": {{
            "target": "建議目標受眾",
            "action": "具體行銷建議 (一句話)"
        }}
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # 清理回應，確保 JSON 格式正確
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text), source_note
    except Exception as e:
        return None, f"模型分析失敗 ({model_name}): {str(e)}"

# --- 4. 前端介面 UI ---

with st.sidebar:
    st.title("🎛️ 戰情控制台")
    st.markdown("---")
    org_name = st.text_input("輸入組織名稱", "台灣癌症基金會")
    run_btn = st.button("🚀 啟動 AI 全網分析", type="primary")
    
    st.markdown("---")
    st.caption("Core: Gemini 2.5 Flash")
    st.caption("Search: DuckDuckGo")

# 主標題區
st.title("🚀 NPO 募款策略 AI 戰情室")
st.markdown("輸入組織名稱，AI 將自動**搜尋網路實時資料**並進行 PESTEL 與競品分析。")

if run_btn and org_name:
    # 進度條與狀態顯示
    with st.status("🤖 AI 正在工作中...", expanded=True) as status:
        
        st.write("🔍 1. 正在潛入網路搜尋最新資料...")
        raw_data = search_web(org_name)
        time.sleep(1)
        
        st.write("🧠 2. 正在呼叫 Gemini 2.5 進行策略運算...")
        analysis, note = analyze_data(org_name, raw_data)
        
        if analysis:
            status.update(label="✅ 分析完成！", state="complete", expanded=False)
        else:
            status.update(label="❌ 發生錯誤", state="error")
            st.error(note)
            st.stop()

    # 顯示資料來源提示
    if "⚠️" in note:
        st.warning(note)
    else:
        st.success(note)

    # --- 分析結果呈現區 ---
    
    # 1. 環境掃描
    st.header("1. 🌍 外部機會與威脅 (OT分析)")
    col1, col2 = st.columns(2)
    with col1:
        st.info("**🚀 機會點 (Opportunity)**")
        st.write(analysis.get('pestel', {}).get('opportunity', '無資料'))
    with col2:
        st.error("**⚠️ 威脅點 (Threat)**")
        st.write(analysis.get('pestel', {}).get('threat', '無資料'))

    # 2. 競品表格
    st.header("2. ⚔️ 競品雷達")
    comps = analysis.get('competitors', [])
    if comps:
        st.table(pd.DataFrame(comps))
    else:
        st.caption("本次分析未發現顯著競爭對手資料。")

    # 3. 策略建議
    st.header("3. 💡 下一步行動建議")
    strategy = analysis.get('strategy', {})
    st.markdown(f"**🎯 鎖定受眾：** {strategy.get('target', '一般大眾')}")
    st.markdown(f"**⚡ 行動方針：** {strategy.get('action', '加強品牌曝光')}")

elif run_btn:
    st.toast("請先輸入組織名稱！", icon="⚠️")