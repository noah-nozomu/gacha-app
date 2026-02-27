import streamlit as st
import pandas as pd
import time
import datetime
from streamlit_gsheets import GSheetsConnection

# --- ページ設定 ---
st.set_page_config(page_title="Laf2周年ガチャ", page_icon="🎁", layout="centered")

# --- CSS（スマホ中央揃え・結果画面の文字を見やすく修正） ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #f3f4f6, #e5e7eb); }
    [data-testid="stAppViewContainer"] > .main > .block-container {
        background-color: #ffffff; padding: 2rem 1rem; border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); max-width: 480px; margin: auto;
    }
    h1 { color: #ef4444 !important; text-align: center; font-weight: 800; line-height: 1.3; }
    div.stButton { display: flex; justify-content: center; }
    .stButton > button {
        width: 100%; background-color: #ef4444; color: white; font-weight: bold;
        border-radius: 9999px; padding: 0.75rem 1rem;
    }
    
    /* ガチャ結果のポップアップ用のCSS */
    .result-popup {
        border-radius: 15px;
        margin-top: 20px;
        margin-bottom: 20px;
        padding: 20px;
        text-align: center;
        
        /* 背景を白にして見やすくする */
        background-color: #ffffff !important;
        
        /* 濃い青色のボーダーで引き締める */
        border: 4px solid #3b82f6 !important;
    }
    
    /* ポップアップ内の文字を黒の太字に */
    .result-popup h2 {
        color: #000000 !important;
        font-weight: bold !important;
        margin: 0 0 10px 0 !important;
        font-size: 1.5rem !important;
    }
    .result-popup p {
        color: #000000 !important;
        font-weight: bold !important;
        margin: 0 !important;
    }
    .result-popup .prize-name {
        font-size: 1.2rem !important;
    }
    .result-popup .message-text {
        font-size: 0.9rem !important;
        margin-top: 5px !important;
    }

    header {visibility: hidden;} 
    </style>
    """, unsafe_allow_html=True)

# --- スプレッドシート接続 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- データの読み込み ---
try:
    df_items = conn.read(worksheet="settings", ttl=0)
    df_items['stock'] = pd.to_numeric(df_items['stock'], errors='coerce').fillna(0)
    
    df_winners = conn.read(worksheet="winners", ttl=0)
    if df_winners.empty:
        df_winners = pd.DataFrame(columns=["日時", "お名前", "景品名", "等級", "使用済み", "使用日時"])
    else:
        df_winners["使用済み"] = df_winners["使用済み"].fillna(False).astype(bool)
        if "使用日時" not in df_winners.columns: df_winners["使用日時"] = ""
except Exception as e:
    st.error(f"読み込みエラー: {e}")
    st.stop()

# --- 状態管理 ---
if 'page_state' not in st.session_state: st.session_state.page_state = 'start'

# ==========================================
#  画面1: スタート画面
# ==========================================
if st.session_state.page_state == 'start':
    st.markdown("<h1>🎁 Laf2周年 🎁<br>スペシャルガチャ</h1>", unsafe_allow_html=True)
    
    if df_items['stock'].sum() <= 0:
        st.warning("大好評につき、すべての景品が終了しました！")
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2: st.image("images/gacha_body.jpg", use_container_width=True)
        if st.button("ガチャを回す！", use_container_width=True, key="spin_btn"):
            st.session_state.is_registered = False
            st.session_state.page_state = 'rolling'
            st.rerun()

# ==========================================
#  画面2: 抽選演出 (rolling)
# ==========================================
elif st.session_state.page_state == 'rolling':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2: st.image("images/rolling.gif", use_container_width=True)
    
    available_items = df_items[df_items['stock'] > 0]
    if available_items.empty:
        st.session_state.page_state = 'start'; st.rerun()

    selected_row = available_items.sample(n=1, weights=available_items['weight']).iloc[0]
    
    df_items.loc[df_items['name'] == selected_row['name'], 'stock'] -= 1
    try:
        conn.update(worksheet="settings", data=df_items)
        st.session_state.result_data = selected_row
        time.sleep(3.5)
        st.session_state.page_state = 'result'; st.rerun()
    except Exception as e:
        st.error(f"在庫更新エラー: {e}")

# ==========================================
#  画面3: 結果画面 (result)
# ==========================================
elif st.session_state.page_state == 'result':
    row = st.session_state.result_data
    rank = int(row['rank'])
    
    title_text = "🎉 大当たり！ 🎉" if rank == 1 else "✨ 当たり！ ✨" if rank == 2 else "ガチャ結果"
    
    st.markdown(f"""
    <div class="result-popup">
        <h2>{title_text}</h2>
        <p class="prize-name">{row["name"]}</p>
        <p class="message-text">{row["message"]}</p>
    </div>
    """, unsafe_allow_html=True)

    st.image(f"images/{row['image']}", use_container_width=True)

    if rank <= 3 and not st.session_state.is_registered:
        st.markdown("<p style='text-align:center; font-weight:bold; color:#ef4444; margin-top:15px;'>🎁景品引き換えのため、お名前を登録してください。</p>", unsafe_allow_html=True)
        winner_name = st.text_input("お名前を入力してください", placeholder="例：山田 太郎")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("登録する", use_container_width=True, key="register_btn"):
                if winner_name:
                    new_rec = pd.DataFrame([{"日時": datetime.datetime.now().strftime("%m/%d %H:%M"), "お名前": winner_name, "景品名": row['name'], "等級": rank, "使用済み": False, "使用日時": ""}])
                    df_winners = pd.concat([df_winners, new_rec], ignore_index=True)
                    try:
                        conn.update(worksheet="winners", data=df_winners)
                        st.session_state.is_registered = True; st.rerun()
                    except Exception as e:
                        st.error(f"当選者登録エラー: {e}")
                else:
                    st.warning("お名前を入力してください！")
    else:
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("最初に戻る", use_container_width=True, key="back_btn"): st.session_state.page_state = 'start'; st.rerun()

# --- 管理者用 ---
with st.expander("⚙️ 管理者設定"):
    st.write("📊 在庫・確率設定（残り個数を確認・修正できます）")
    edited_df = st.data_editor(df_items, disabled=["image"], hide_index=True, use_container_width=True, key="stock_editor")
    
    if st.button("設定を保存", key="save_settings_btn"):
        try:
            conn.update(worksheet="settings", data=edited_df)
            st.success("設定を更新しました！"); st.rerun()
        except Exception as e:
            st.error(f"設定保存エラー: {e}")

    st.write("---")
    st.write("🎟️ 券の使用処理（景品を渡したら消し込みしてください）")
    unused = df_winners[df_winners["使用済み"] == False]
    
    if not unused.empty:
        options = unused.apply(lambda r: f"{r['お名前']}様 - {r['景品名']} ({r['日時']})", axis=1).tolist()
        selected_option = st.selectbox("景品を渡す人を選択", options, key="winner_selectbox")
        
        if st.button("✅ 使用済みにする", use_container_width=True, key="mark_used_btn"):
            try:
                selected_idx = unused.index[options.index(selected_option)]
                now_str = datetime.datetime.now().strftime("%m/%d %H:%M")
                df_winners.at[selected_idx, "使用済み"] = True
                df_winners.at[selected_idx, "使用日時"] = now_str
                
                conn.update(worksheet="winners", data=df_winners)
                st.success(f"記録完了！ {now_str} に使用済みにしました。")
                time.sleep(1.5)
                st.rerun()
            except Exception as e:
                st.error(f"使用済みマークエラー: {e}")
    else:
        st.info("現在、未使用の当選者はいません。")

    st.write("---")
    st.write("📝 全当選者データ（確認用）")
    # ここは閲覧専用のシンプルな表にしました
    st.dataframe(df_winners, hide_index=True, use_container_width=True)