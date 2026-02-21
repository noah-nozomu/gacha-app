import streamlit as st
import pandas as pd
import time
import datetime
from streamlit_gsheets import GSheetsConnection

# --- ページ設定 ---
st.set_page_config(page_title="スペシャルガチャ", page_icon="🎁", layout="centered")

# --- CSSでデザイン修正（スマホ中央揃え・超安定版） ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #f3f4f6, #e5e7eb); }
    [data-testid="stAppViewContainer"] > .main > .block-container {
        background-color: #ffffff;
        padding: 2rem 1rem;
        border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        max-width: 480px;
        margin: auto;
    }
    h1 {
        color: #ef4444 !important;
        text-align: center;
        font-family: sans-serif;
        font-weight: 800;
        margin-bottom: 0.5rem;
        line-height: 1.3;
    }
    p, div { color: #374151; font-family: sans-serif; }
    img { border-radius: 10px; max-height: 300px; object-fit: contain; }
    
    /* ボタンは配置の魔法を消し、色と形だけを指定 */
    .stButton > button {
        background-color: #ef4444;
        color: white;
        font-weight: bold;
        border-radius: 9999px;
        border: none;
        padding: 0.75rem 1rem;
        box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.4);
        transition: transform 0.1s;
    }
    .stButton > button:hover { background-color: #dc2626; transform: scale(1.02); }
    .stButton > button:active { transform: scale(0.98); }
    header {visibility: hidden;} 
    </style>
    """, unsafe_allow_html=True)

# --- スプレッドシート接続 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- データの読み込み ---
try:
    df_items = conn.read(worksheet="settings", ttl=0)
except Exception as e:
    st.error(f"⚠️ スプレッドシートの「settings」タブが見つかりません。作成してください。エラー詳細: {e}")
    st.stop()

try:
    df_winners = conn.read(worksheet="winners", ttl=0)
    if df_winners.empty:
        df_winners = pd.DataFrame(columns=["日時", "お名前", "景品名", "等級", "使用済み", "使用日時"])
    else:
        if "使用済み" in df_winners.columns:
            df_winners["使用済み"] = df_winners["使用済み"].fillna(False).astype(bool)
        if "使用日時" not in df_winners.columns:
            df_winners["使用日時"] = ""
        else:
            df_winners["使用日時"] = df_winners["使用日時"].fillna("")
except Exception as e:
    df_winners = pd.DataFrame(columns=["日時", "お名前", "景品名", "等級", "使用済み", "使用日時"])

# --- 状態管理 ---
if 'page_state' not in st.session_state:
    st.session_state.page_state = 'start'
if 'result_data' not in st.session_state:
    st.session_state.result_data = None
if 'is_registered' not in st.session_state:
    st.session_state.is_registered = False

# ==========================================
#  画面1: スタート画面
# ==========================================
if st.session_state.page_state == 'start':
    st.markdown("<h1>🎁 Laf2周年 🎁<br>スペシャルガチャ</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 20px;'>何が出るかな？運試し！</p>", unsafe_allow_html=True)

    # 左右に余白(1)、真ん中を広く(2)の比率で画面を分割
    col1, col2, col3 = st.columns([1, 2, 1])
    
    # 画像もボタンも、真ん中の枠(col2)の中にまとめる！
    with col2:
        try:
            st.image("images/gacha_body.jpg", use_container_width=True)
        except:
             st.info("gacha_body.jpg がありません")

        st.write("") 
        
        # ▼▼▼ 枠の横幅いっぱいにボタンを広げる（use_container_width=True） ▼▼▼
        if st.button("ガチャを回す！", use_container_width=True):
            st.session_state.is_registered = False
            st.session_state.page_state = 'rolling'
            st.rerun()

# ==========================================
#  画面2: 動画だけの画面 (rolling)
# ==========================================
elif st.session_state.page_state == 'rolling':
    st.write("") 
    st.write("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("images/rolling.gif", use_container_width=True)
        except:
             st.info("rolling.gif がありません")
    
    time.sleep(3.5) 

    selected_row = df_items.sample(n=1, weights=df_items['weight']).iloc[0]
    st.session_state.result_data = selected_row 
    
    st.session_state.page_state = 'result'
    st.rerun()

# ==========================================
#  画面3: 結果画面 (result)
# ==========================================
elif st.session_state.page_state == 'result':
    row = st.session_state.result_data
    rank = int(row['rank'])

    if rank == 1:
        st.balloons()
        border_color = "#f59e0b"
        bg_color = "#fffbeb"
        title_text = "🎉 大当たり！ 🎉"
    elif rank == 2:
        st.snow()
        border_color = "#3b82f6"
        bg_color = "#eff6ff"
        title_text = "✨ 当たり！ ✨"
    else:
        border_color = "#e5e7eb"
        bg_color = "#f9fafb"
        title_text = "ガチャ結果"

    st.markdown(f"""
    <div style="
        border: 4px solid {border_color};
        background-color: {bg_color};
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        margin-top: 20px;
    ">
        <h2 style="margin: 0 0 10px 0; color: #333; font-size: 1.5rem;">{title_text}</h2>
        <p style="font-size: 1.2rem; font-weight: bold; color: #ef4444; margin: 0;">{row['name']}</p>
        <p style="font-size: 0.9rem; color: #666; margin-top: 5px;">{row['message']}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image(f"images/{row['image']}", use_container_width=True)
        except:
            st.error("商品画像エラー")

    if rank <= 3:
        if not st.session_state.is_registered:
            st.markdown("<p style='text-align:center; font-weight:bold; color:#ef4444; margin-top:15px;'>🎁景品引き換えのため、お名前を登録してください。</p>", unsafe_allow_html=True)
            
            winner_name = st.text_input("お名前（ニックネーム可）", placeholder="例：山田 太郎")
            
            # 登録ボタンも真ん中に
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("登録する", use_container_width=True):
                    if winner_name:
                        new_record = pd.DataFrame([{
                            "日時": datetime.datetime.now().strftime("%m/%d %H:%M"),
                            "お名前": winner_name,
                            "景品名": row['name'],
                            "等級": rank,
                            "使用済み": False,
                            "使用日時": ""  
                        }])
                        updated_winners = pd.concat([df_winners, new_record], ignore_index=True)
                        try:
                            conn.update(worksheet="winners", data=updated_winners)
                            st.session_state.is_registered = True 
                            st.rerun() 
                        except Exception as e:
                            st.error(f"保存エラー: {e}")
                    else:
                        st.warning("お名前を入力してください！")
        else:
            st.success("✅ 登録が完了しました！この画面をスタッフにお見せください。")
            st.write("")
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("最初に戻る", use_container_width=True):
                    st.session_state.page_state = 'start'
                    st.rerun()
    else:
        st.write("")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("もう一度回す", use_container_width=True):
                st.session_state.page_state = 'start'
                st.rerun()

# --- 管理者用 ---
st.write("")
st.write("")
with st.expander("⚙️ 管理者設定"):
    st.write("📊 現在の設定と確率")
    st.markdown("<p style='font-size:0.8rem; color:#666;'>表の文字をダブルクリックして書き換え、下の保存ボタンを押してください。（※画像ファイル名だけは変更できません）</p>", unsafe_allow_html=True)
    
    edited_df = st.data_editor(
        df_items,
        disabled=["image"], 
        hide_index=True,
        use_container_width=True,
        key="prob_editor"
    )

    if st.button("設定を保存する"):
        try:
            conn.update(worksheet="settings", data=edited_df)
            st.success("設定を更新しました！次回から新しい内容でガチャが回ります。")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"保存エラー: {e}")

    st.write("---")

    st.write("🎟️ 券の使用処理")
    st.markdown("<p style='font-size:0.8rem; color:#666;'>お客様から画面を見せてもらったら、ここで名前を選んで使用済みにしてください。</p>", unsafe_allow_html=True)
    
    unused_df = df_winners[df_winners["使用済み"] == False]
    
    if not unused_df.empty:
        options = unused_df.apply(lambda r: f"{r['お名前']}様 - {r['景品名']} ({r['日時']})", axis=1).tolist()
        selected_option = st.selectbox("景品を渡す人を選んでください", options)
        
        if st.button("✅ この券を「使用済み」にする"):
            selected_idx = unused_df.index[options.index(selected_option)]
            now_str = datetime.datetime.now().strftime("%m/%d %H:%M")
            df_winners.at[selected_idx, "使用済み"] = True
            df_winners.at[selected_idx, "使用日時"] = now_str
            
            try:
                conn.update(worksheet="winners", data=df_winners)
                st.success(f"記録完了！ {now_str} に使用済みにしました。")
                time.sleep(1.5)
                st.rerun()
            except Exception as e:
                st.error(f"保存エラー: {e}")
    else:
        st.info("現在、未使用の当選者はいません。")

    st.write("---")
    st.write("📝 全当選者データ（修正用）")
    
    edited_winner_df = st.data_editor(
        df_winners,
        column_config={
            "使用済み": st.column_config.CheckboxColumn(
                "使用済み",
                help="手動でチェックを外すこともできます",
                default=False,
            )
        },
        disabled=["日時", "お名前", "景品名", "等級", "使用日時"], 
        hide_index=True,
        use_container_width=True,
        key="winner_editor"
    )
    
    if st.button("チェック状態を保存する"):
        try:
            conn.update(worksheet="winners", data=edited_winner_df)
            st.success("スプレッドシートのリストを更新しました！")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"保存エラー: {e}")