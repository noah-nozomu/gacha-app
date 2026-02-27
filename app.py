import streamlit as st
import pandas as pd
import time
import datetime
from streamlit_gsheets import GSheetsConnection

# --- ページ設定 ---
st.set_page_config(page_title="Laf2周年ガチャ", page_icon="🎁", layout="centered")

# --- CSS（スマホ中央揃え・デザイン維持） ---
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
        if st.button("ガチャを回す！", use_container_width=True):
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
    
    # 在庫を減らして保存
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
    st.markdown(f'<div style="border: 4px solid #ef4444; padding: 20px; text-align: center; border-radius: 15px; margin-top:20px;">'
                f'<h2>{title_text}</h2><p style="font-size:1.2rem; font-weight:bold;">{row["name"]}</p><p>{row["message"]}</p></div>', unsafe_allow_html=True)
    st.image(f"images/{row['image']}", use_container_width=True)

    if rank <= 3 and not st.session_state.is_registered:
        winner_name = st.text_input("お名前を入力してください")
        if st.button("登録する", use_container_width=True):
            if winner_name:
                new_rec = pd.DataFrame([{"日時": datetime.datetime.now().strftime("%m/%d %H:%M"), "お名前": winner_name, "景品名": row['name'], "等級": rank, "使用済み": False, "使用日時": ""}])
                df_winners = pd.concat([df_winners, new_rec], ignore_index=True)
                conn.update(worksheet="winners", data=df_winners)
                st.session_state.is_registered = True; st.rerun()
    else:
        if st.button("最初に戻る", use_container_width=True): st.session_state.page_state = 'start'; st.rerun()

# --- 管理者用 ---
with st.expander("⚙️ 管理者設定"):
    # リセット機能
    st.subheader("🔄 データの初期化")
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        if st.button("📦 在庫をリセット"):
            # 在庫を 5, 5, 50, 140 に戻す
            reset_stocks = {1: 5, 2: 5, 3: 50, 4: 140}
            df_items['stock'] = df_items['rank'].map(reset_stocks).fillna(0)
            conn.update(worksheet="settings", data=df_items)
            st.success("在庫を初期数に戻しました！")
            time.sleep(1); st.rerun()
            
    with col_res2:
        if st.button("🗑️ 当選者を消去"):
            # 見出しだけ残して空にする
            empty_winners = pd.DataFrame(columns=["日時", "お名前", "景品名", "等級", "使用済み", "使用日時"])
            conn.update(worksheet="winners", data=empty_winners)
            st.success("当選者リストを空にしました！")
            time.sleep(1); st.rerun()

    st.write("---")
    st.write("📊 在庫・確率設定")
    edited_df = st.data_editor(df_items, disabled=["image"], hide_index=True, use_container_width=True)
    if st.button("設定を保存"):
        conn.update(worksheet="settings", data=edited_df)
        st.success("更新しました！"); st.rerun()

    st.write("---")
    st.write("🎟️ 券の使用処理")
    unused = df_winners[df_winners["使用済み"] == False]
    if not unused.empty:
        options = unused.apply(lambda r: f"{r['お名前']}様 - {r['景品名']}", axis=1).tolist()
        selected_option = st.selectbox("景品を渡す人を選択", options)
        if st.button("✅ 使用済みにする", use_container_width=True):
            idx = unused.index[options.index(selected_option)]
            df_winners.at[idx, "使用済み"] = True
            df_winners.at[idx, "使用日時"] = datetime.datetime.now().strftime("%m/%d %H:%M")
            conn.update(worksheet="winners", data=df_winners)
            st.success("完了！"); time.sleep(1); st.rerun()