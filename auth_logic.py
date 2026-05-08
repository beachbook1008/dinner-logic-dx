import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from datetime import datetime
from dotenv import load_dotenv

# --- 1. 初期設定 ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key, transport="rest")
    model = genai.GenerativeModel('models/gemini-3-flash-preview')
else:
    st.error("APIキーがないよ！.envを確認してね。")
    st.stop()

st.set_page_config(page_title="Dinner Logic DX", layout="wide")

# CSS読み込み関数（UTF-8指定で日本語エラーを回避！）
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, encoding="utf-8") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

# --- 2. データ管理 ---
USER_FILE = "user_settings.csv"
MENU_FILE = "dinner_list.csv"

def get_all_users():
    cols = ["user_id", "password", "target_weight", "last_update"]
    if os.path.exists(USER_FILE):
        try:
            df = pd.read_csv(USER_FILE)
            for c in cols:
                if c not in df.columns: df[c] = None
            return df
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def save_user(user_id, password, target_weight=None):
    df = get_all_users()
    u_str = str(user_id)
    if u_str in df['user_id'].astype(str).values:
        idx = df[df['user_id'].astype(str) == u_str].index[0]
        if password: df.at[idx, 'password'] = password
        if target_weight is not None:
            df.at[idx, 'target_weight'] = target_weight
            df.at[idx, 'last_update'] = datetime.now().strftime("%Y-%m-%d")
    else:
        new_row = pd.DataFrame({"user_id": [user_id], "password": [password], "target_weight": [target_weight], "last_update": [datetime.now().strftime("%Y-%m-%d")]})
        df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(USER_FILE, index=False)

@st.cache_data
def load_menu():
    try:
        df_m = pd.read_csv(MENU_FILE, header=None).iloc[:, :5]
        df_m.columns = ['id', 'store', 'name', 'genre', 'cal']
        df_m['cal'] = pd.to_numeric(df_m['cal'], errors='coerce').fillna(0)
        df_m['display'] = df_m['store'] + " - " + df_m['name'] + " (" + df_m['cal'].astype(int).astype(str) + "kcal)"
        return df_m
    except:
        return pd.DataFrame()

# --- 3. ログイン管理 ---
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False
if 'show_register' not in st.session_state:
    st.session_state['show_register'] = False

if not st.session_state['is_logged_in']:
    if st.session_state['show_register']:
        st.title("📝 新規会員登録")
        n_id = st.text_input("希望ID")
        n_pw = st.text_input("パスワード", type="password")
        if st.button("登録"):
            if n_id and n_pw:
                save_user(n_id, n_pw)
                st.success("登録完了！")
                st.session_state['show_register'] = False
                st.rerun()
    else:
        st.title("🔐 Dinner Logic ログイン")
        l_id = st.text_input("ユーザーID")
        l_pw = st.text_input("パスワード", type="password")
        if st.button("ログイン"):
            df = get_all_users()
            match = df[(df['user_id'].astype(str) == l_id) & (df['password'].astype(str) == l_pw)]
            if not match.empty:
                st.session_state['is_logged_in'] = True
                st.session_state['current_user'] = l_id
                st.rerun()
            else: st.error("間違い！")
        if st.button("新規登録はこちら"):
            st.session_state['show_register'] = True
            st.rerun()
    st.stop()

# --- 4. メイン画面 ---
user_id = st.session_state['current_user']
df_users = get_all_users()
user_row = df_users[df_users['user_id'].astype(str) == user_id].iloc[0]
df_menu = load_menu()

# 目標設定
if pd.isna(user_row['target_weight']):
    st.title(f"📅 目標設定 ({user_id})")
    t_w = st.number_input("今月の目標体重 (kg)", 30.0, 150.0, 52.0)
    if st.button("目標を保存"):
        save_user(user_id, user_row['password'], t_w)
        st.rerun()
    st.stop()

# アバター設定
if os.path.exists("mii_thunder.jpg"): thunder_avatar = "mii_thunder.jpg"
elif os.path.exists("mii_thunder.png"): thunder_avatar = "mii_thunder.png"
else: thunder_avatar = "⚡️"

st.title(f"🥘 美食家サンダーさん とライエット")

with st.sidebar:
    st.image(thunder_avatar, width=150, caption="美食家サンダー⚡️")
    st.header("👤 ステータス")
    st.success(f"User: {user_id}\nTarget: {user_row['target_weight']}kg")
    weight = st.number_input("今の体重 (kg)", 30.0, 150.0, 55.0)
    height = st.number_input("身長 (cm)", 100.0, 220.0, 160.0)
    age = st.number_input("年齢", 15, 100, 20)
    gender = st.radio("性別", ["女子", "男子"])
    levels = {"1.2：座りっぱなし": 1.2, "1.375：通学": 1.375, "1.55：運動あり": 1.55}
    activity = levels[st.selectbox("生活スタイル", list(levels.keys()))]
    if st.button("ログアウト"):
        st.session_state.clear()
        st.rerun()

# 計算
bmr = (447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)) if gender == "女子" else (88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age))
target_cal = (bmr * activity) - ((weight - float(user_row['target_weight'])) * 7200 / 30)

col1, col2 = st.columns(2)
with col1: b_items = st.multiselect("朝食", df_menu['display'].tolist() if not df_menu.empty else [])
with col2: l_items = st.multiselect("昼食", df_menu['display'].tolist() if not df_menu.empty else [])

dinner_cal = target_cal - (df_menu[df_menu['display'].isin(b_items)]['cal'].sum() + df_menu[df_menu['display'].isin(l_items)]['cal'].sum())
st.metric("今日の残り枠", f"{int(dinner_cal)} kcal")

# --- 5. 自動挨拶 ---
st.divider()
with st.chat_message("assistant", avatar=thunder_avatar):
    if dinner_cal > 500: st.write(f"あったまいいね！今日はまだ {int(dinner_cal)}kcal も余裕があるわ。美味しいもの探しに行こうよ！")
    elif dinner_cal > 0: st.write(f"今のところ順調ね。夜は控えめな美食を楽しんで！")
    else: st.write(f"ちょっと！もうカロリーオーバーよ！明日は火鍋禁止ね！")

# --- 6. おすすめ表示（3列にして見やすく！） ---
st.subheader("🥢 サンダーさんのおすすめ")
if not df_menu.empty:
    recs = df_menu[df_menu['cal'] <= dinner_cal].sort_values(by='cal', ascending=False).head(6)
    if not recs.empty:
        cols = st.columns(3)
        for i, (_, row) in enumerate(recs.iterrows()):
            with cols[i % 3]:
                st.metric(label=row['store'], value=f"{int(row['cal'])}kcal", delta=row['name'], delta_color="inverse")

# --- 7. AI相談室 ---
if user_msg := st.chat_input("サンダーさんに相談"):
    with st.chat_message("assistant", avatar=thunder_avatar):
        prompt = f"あなたは中国の美食を求めて旅する女子大生サンダーさん。口癖『あったまいいね！』。相手{user_id}。残り{int(dinner_cal)}kcal。質問:{user_msg}"
        try:
            st.write(model.generate_content(prompt).text)
        except:
            st.error("AIエラー：ネットを確認してね！")