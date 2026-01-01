import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS
import pandas as pd
import json
import time
import random

# --- 1. 頁面基礎設定 ---
st.set_page_config(
    page_title="NPO 戰情室 Pro", 
    page_icon="🧠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. 設定 Gemini API ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ 請先在 Streamlit Cloud 設定 Secrets: GEMINI_API_KEY")
    st.stop()

# --- 3. 核心功能函數 ---

def search_web_enhanced(org_name, category):
    """
    增強版搜尋：針對輿情、競品、時事進行多角度搜索
    """
    results_data = []
    
    # 定義三組不同的搜尋視角
    search_angles = [
        # 1. 輿情與評價 (找 PTT, Dcard, 討論區)
        f"{org_name} 評價 PTT Dcard 爭議",
        # 2. 該領域的時事熱點 (找最近大家的關注點)
        f"台灣 {category} 議題 新聞 趨勢 2024 2025",
        # 3. 競品與廣告 (找對手在做什麼)
        f"{category} 基金會 募款活動 案例"
    ]

    try:
        with DDGS() as ddgs:
            for query in search_angles:
                # 每個角度抓取 2-3 筆精華
                results = list(ddgs.text(query, max_results=2))
                if results:
                    for r in results:
                        # 儲存標題、內容與連結，作為佐證資料
                        results_data.append({
                            "source": r['title'],
                            "snippet": r['body'],
                            "link": r['href']
                        })
                time.sleep(random.uniform(0.5, 1.0)) # 隨機延遲防擋
    except Exception as e:
        print(f"搜尋警告: {e}")
    
    return results_data

def analyze_data_deep(org_name, category, search_data):
    """
    深度分析：要求 AI 根據證據推導策略
    """
    # 組合搜尋到的證據文字
    evidence_text = ""
    for idx, item in enumerate(search_data):
        evidence_text += f"[{idx+1}] 來源：{item['source']}\n內容：{item['snippet']}\n\n"
    
    if not evidence_text:
        evidence_text = "（網路搜尋無結果，請基於您的專業知識庫進行分析）"
        source_note = "⚠️ 網路搜尋受阻，分析基於 AI 內建知識。"
    else:
        source_note = f"✅ 已搜集 {len(search_data)} 筆關鍵情報，包含輿情與新聞。"

    # 使用 Gemini 2.5 Flash (目前最強大的模型)
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    prompt = f"""
    你現在是「{org_name}」的首席品牌策略長。我們專注於「{category}」領域。
    請根據下方的【網路實證資料】，進行深度的募款行銷分析。
    
    【網路實證資料】：
    {evidence_text}

    【任務要求】：
    請忽略泛泛而談的理論，我需要基於上述資料的「實戰建議」。
    請回傳嚴格的 JSON 格式 (不要 Markdown)，結構如下：
    {{
        "market_sentiment": {{
            "mood": "目前的社會輿論氛圍 (例如：焦慮、憤怒、溫馨)",
            "keywords": ["關鍵字1", "關鍵字2", "關鍵字3"],
            "insight": "針對該議題，大眾目前最在意的點是什麼？"
        }},
        "competitor_analysis": [
            {{"name": "競品A", "strength": "他們做對了什麼？", "weakness": "我們可以攻擊的弱點"}}
        ],
        "target_audience": {{
            "persona": "描述核心捐款人的輪廓 (年齡/職業/興趣)",
            "pain_point": "他們為什麼會想捐款？心裡的痛點或渴望是什麼？"
        }},
        "communication_strategy": {{
            "angle": "建議的溝通切角 (例如：從受害者故事出發 vs 從數據成效出發)",
            "tone": "建議語氣 (例如：權威專業 vs 溫暖陪伴)",
            "channels": "建議投放渠道 (FB/IG/Podcast/Line)"
        }}
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text), source_note
    except Exception as e:
        return None, f"AI 分析失敗: {str(e)}"

# --- 4. 前端介面 UI ---

with st.sidebar:
    st.title("🎛️ 戰情控制台")
    st.markdown("---")
    
    # 輸入區
    org_name = st.text_input("輸入組織名稱", "台灣展翅協會")
    category = st.selectbox(
        "選擇組織關注領域", 
        ["教育與學習", "心理健康與諮商", "兒少保護", "環境與動物", "醫療與長照", "性別與人權"]
    )
    
    run_btn = st.button("🚀 啟動深度分析", type="primary")
    
    st.markdown("---")
    st.info("💡 小撇步：選擇正確的領域，能幫助 AI 更精準地找到競爭對手。")

# 主畫面
st.title("🧠 NPO 募款戰略顧問 (Pro)")
st.markdown(f"針對 **{category}** 領域的輿情與競品深度解析")

if run_btn and org_name:
    # 執行流程視覺化
    with st.status("🔍 戰略分析中...", expanded=True) as status:
        
        st.write("📡 1. 正在掃描 PTT/Dcard 輿情與時事新聞...")
        search_results = search_web_enhanced(org_name, category)
        time.sleep(1)
        
        st.write("🧠 2. 正在進行受眾輪廓與溝通策略推演...")
        analysis, note = analyze_data_deep(org_name, category, search_results)
        
        if analysis:
            status.update(label="✅ 分析完成！", state="complete", expanded=False)
        else:
            status.update(label="❌ 分析失敗", state="error")
            st.error(note)
            st.stop()

    st.success(note)

    # --- 分析報告呈現區 ---

    # 1. 輿情風向球
    st.header("1. 🌪️ 市場輿情風向")
    sent = analysis.get('market_sentiment', {})
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("社會氛圍", sent.get('mood', '中性'))
    with col2:
        st.write(f"**🔥 熱門關鍵字：** {', '.join(sent.get('keywords', []))}")
        st.info(f"**💡 洞察：** {sent.get('insight', '無資料')}")

    # 2. 受眾與溝通 (這是你最想要的)
    st.header("2. 🎯 受眾輪廓與溝通策略")
    
    tab1, tab2 = st.tabs(["👤 誰會捐款？ (Persona)", "📢 該怎麼說？ (Strategy)"])
    
    with tab1:
        ta = analysis.get('target_audience', {})
        st.subheader("核心捐款人畫像")
        st.markdown(f"**{ta.get('persona', '一般大眾')}**")
        st.warning(f"❤️ **深層動機 (Pain Point)：**\n{ta.get('pain_point', '')}")
    
    with tab2:
        comm = analysis.get('communication_strategy', {})
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"**🔪 切入角度：**\n{comm.get('angle', '')}")
        c2.markdown(f"**🗣️ 語氣設定：**\n{comm.get('tone', '')}")
        c3.markdown(f"**📱 建議渠道：**\n{comm.get('channels', '')}")

    # 3. 競品攻防
    st.header("3. ⚔️ 競品攻防分析")
    comps = analysis.get('competitor_analysis', [])
    if comps:
        # 用卡片式呈現競品
        for comp in comps:
            with st.expander(f"🆚 競爭對手：{comp.get('name', '未知')}"):
                st.write(f"💪 **優勢：** {comp.get('strength', '')}")
                st.write(f"🛡️ **弱點 (機會點)：** {comp.get('weakness', '')}")

    # 4. 證據來源 (增加可信度)
    st.markdown("---")
    with st.expander("📚 查看 AI 參考的原始資料來源 (Evidence)"):
        for item in search_results:
            st.markdown(f"**[{item['source']}]({item['link']})**")
            st.caption(item['snippet'])
            st.markdown("---")

elif run_btn:
    st.toast("請輸入組織名稱並選擇領域！", icon="⚠️")