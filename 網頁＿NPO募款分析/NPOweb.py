import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS
import json
import time

st.set_page_config(page_title="NPO 戰情室 (模型檢測版)", layout="wide")

# --- 1. 設定與檢查 API Key ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ 尚未設定 API Key (Secrets)")
    st.stop()

# --- 2. 關鍵步驟：列出所有可用模型 ---
st.title("🕵️‍♀️ 模型權限偵測")
st.info("我們來檢查您的 API Key 到底可以使用哪些模型...")

available_models = []
try:
    # 呼叫 Google 查詢可用模型清單
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
    
    st.success(f"✅ 成功連線！您的 Key 支援以下 {len(available_models)} 個模型：")
    st.code(available_models)
    
except Exception as e:
    st.error(f"❌ 無法列出模型，API Key 可能無效或受限。\n錯誤訊息: {e}")
    st.stop()

# --- 3. 自動選擇一個會動的模型 ---
# 優先順序： Flash -> Pro -> 任何可用的
target_model = "models/gemini-1.5-flash"
if "models/gemini-1.5-flash" not in available_models:
    if "models/gemini-pro" in available_models:
        target_model = "models/gemini-pro"
        st.warning("⚠️ 您的 Key 不支援 Flash，將自動降級使用 gemini-pro")
    else:
        # 如果都沒有，就拿清單裡的第一個
        if available_models:
            target_model = available_models[0]
            st.warning(f"⚠️ 找不到常用模型，將強制使用: {target_model}")
        else:
            st.error("❌ 您的帳號似乎沒有任何可用的文字生成模型。")
            st.stop()
else:
    st.success("✨ 檢測通過：將使用 gemini-1.5-flash")

# ==========================================
# 下面是正常的分析功能 (使用上面選出來的 target_model)
# ==========================================

def search_web(keyword):
    results_text = ""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"{keyword} 新聞", max_results=2))
            if results:
                for r in results:
                    results_text += f"標題: {r['title']}\n摘要: {r['body']}\n\n"
    except Exception as e:
        results_text = "(搜尋被阻擋，改用內建知識)"
    return results_text

def analyze_data(org_name, search_results, model_name):
    # 使用我們剛剛檢測到的「可用模型」
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    你是募款顧問。請根據以下資訊分析「{org_name}」：
    {search_results}
    
    請回傳純 JSON 格式:
    {{
        "pestel_summary": "環境分析...",
        "competitors": [{{"name": "競品A", "strategy": "..."}}],
        "suggestion": "三個建議..."
    }}
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        return {"suggestion": f"發生錯誤: {e}"}

# --- UI ---
st.markdown("---")
st.header("🚀 NPO 分析器 (自動適配版)")
org_name = st.text_input("輸入組織名稱", "台灣癌症基金會")

if st.button("開始分析"):
    with st.status("正在執行..."):
        st.write(f"1. 使用模型: {target_model}")
        st.write("2. 搜尋資料中...")
        data = search_web(org_name)
        st.write("3. AI 分析中...")
        result = analyze_data(org_name, data, target_model)
        st.write("✅ 完成！")
    
    st.subheader("分析結果")
    st.write(result)