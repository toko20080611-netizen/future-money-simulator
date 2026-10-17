
import streamlit as st
import pandas as pd

# ---------- ページ設定 ----------
st.set_page_config(
    page_title="未来のお金シミュレーター",
    page_icon="🌿",
    layout="wide"
)

# ---------- デザイン ----------
st.markdown("""
<style>
.stApp {
    background-color: #F7F9F6;
}
.block-container {
    max-width: 1100px;
    padding-top: 2rem;
}
h1, h2, h3 {
    color: #24583D;
}
div[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #DDE8DD;
    padding: 18px;
    border-radius: 14px;
}
div.stButton > button {
    background-color: #397653;
    color: white;
    border-radius: 10px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ---------- 共通関数 ----------
def simulate(initial, monthly, annual_rate, years):
    balance = float(initial)
    rate = annual_rate / 100 / 12
    history = [balance]
    invested_history = [float(initial)]

    for month in range(years * 12):
        balance = balance * (1 + rate)
        balance += monthly

        invested = initial + monthly * (month + 1)

        if (month + 1) % 12 == 0:
            history.append(balance)
            invested_history.append(invested)

    return balance, invested, history, invested_history


# ---------- ヘッダー ----------
st.title("🌿 未来のお金シミュレーター")
st.write("お金の未来を、楽しく学ぼう。")
st.caption(
    "積立・複利・リスクについて学び、"
    "自分に合ったお金との向き合い方を考えるツールです。"
)

st.divider()

page = st.radio(
    "メニュー",
    ["🏠 資産シミュレーション",
     "📊 3パターン比較",
     "🔎 投資スタイル診断",
     "📚 基礎知識"],
    horizontal=True,
    label_visibility="collapsed"
)

# ---------- 1. 資産シミュレーション ----------
if page == "🏠 資産シミュレーション":
    st.header("資産シミュレーション")
    st.write("条件を変更して、将来の資産がどう変わるか試してみよう。")

    left, right = st.columns(2)

    with left:
        initial = st.number_input(
            "初期資金（円）",
            min_value=0, max_value=100000000,
            value=100000, step=10000
        )
        monthly = st.number_input(
            "毎月の積立額（円）",
            min_value=0, max_value=1000000,
            value=10000, step=1000
        )

    with right:
        rate = st.slider(
            "想定年利（％）",
            min_value=0.0, max_value=10.0,
            value=5.0, step=0.5
        )
        years = st.slider(
            "運用期間（年）",
            min_value=1, max_value=50,
            value=20
        )

    balance, invested, history, invested_history = simulate(
        initial, monthly, rate, years
    )

    st.subheader("シミュレーション結果")

    c1, c2, c3 = st.columns(3)
    c1.metric("最終資産額", f"約{balance:,.0f}円")
    c2.metric("積立元本", f"{invested:,.0f}円")
    c3.metric("運用による増減", f"{balance-invested:+,.0f}円")

    chart_data = pd.DataFrame({
        "資産総額": history,
        "積立元本": invested_history
    }, index=range(years + 1))
    chart_data.index.name = "経過年数"

    st.line_chart(chart_data)
    st.caption(
        "毎月末に積み立てる想定の概算です。"
        "税金・手数料は含まず、一定の利回りを仮定しています。"
    )

# ---------- 2. 3パターン比較 ----------
elif page == "📊 3パターン比較":
    st.header("3パターンを比較しよう")
    st.write("同じ積立条件で、仮定した利回りの違いを調べよう。")

    c1, c2 = st.columns(2)

    with c1:
        initial = st.number_input(
            "初期資金（円）",
            min_value=0, max_value=100000000,
            value=100000, step=10000,
            key="compare_initial"
        )
        monthly = st.number_input(
            "毎月の積立額（円）",
            min_value=0, max_value=1000000,
            value=10000, step=1000,
            key="compare_monthly"
        )

    with c2:
        years = st.slider(
            "比較する期間（年）",
            min_value=1, max_value=50,
            value=20, key="compare_years"
        )
        savings_rate = st.number_input(
            "貯金の仮定利率（％）",
            min_value=0.0, max_value=10.0,
            value=0.1, step=0.1
        )

    stable_rate = st.number_input(
        "比較ケースBの仮定利回り（％）",
        min_value=0.0, max_value=10.0,
        value=2.0, step=0.5
    )
    growth_rate = st.number_input(
        "比較ケースCの仮定利回り（％）",
        min_value=0.0, max_value=10.0,
        value=5.0, step=0.5
    )

    cases = {
        "貯金（仮定）": savings_rate,
        "ケースB（仮定）": stable_rate,
        "ケースC（仮定）": growth_rate
    }

    chart = {}
    rows = []

    for name, r in cases.items():
        balance, invested, history, _ = simulate(
            initial, monthly, r, years
        )
        chart[name] = history
        rows.append({
            "比較ケース": name,
            "仮定利回り": f"{r:.1f}%",
            "積立元本": f"{invested:,.0f}円",
            "最終資産額": f"{balance:,.0f}円",
            "元本との差": f"{balance-invested:+,.0f}円"
        })

    st.subheader("資産推移の比較")
    df = pd.DataFrame(chart, index=range(years + 1))
    df.index.name = "経過年数"
    st.line_chart(df)

    st.subheader("結果一覧")
    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True
    )

    st.info(
        "ケースB・Cは比較のための仮定です。"
        "利回りの高さだけで実際のリスクや安全性を"
        "判断することはできません。"
    )

# ---------- 3. 投資スタイル診断 ----------
elif page == "🔎 投資スタイル診断":
    st.header("投資スタイル診断")
    st.write("自分のお金の使い方や、学びたいことを整理してみよう。")

    timing = st.radio(
        "Q1. お金を使う予定はいつ？",
        [
            "1〜3年以内",
            "5〜10年後",
            "10年以上先"
        ]
    )

    priority = st.radio(
        "Q2. 何を重視したい？",
        [
            "元本が減る可能性をできるだけ避けたい",
            "リスクとリターンの関係を理解したい",
            "長期的な資産形成について学びたい"
        ]
    )

    learning = st.radio(
        "Q3. 何を学びたい？",
        [
            "貯金・家計管理",
            "投資の仕組み・リスク",
            "複利・長期投資・分散投資"
        ]
    )

    if st.button("診断結果を見る"):
        st.subheader("あなたの学習ヒント")

        if timing == "1〜3年以内":
            st.write(
                "🌱 **お金を使う時期を重視**\n\n"
                "近いうちに必要なお金は、"
                "投資に回す前に必要額を確保することを考えよう。"
            )
        elif timing == "5〜10年後":
            st.write(
                "🌿 **目標と期間を考える**\n\n"
                "お金を使う時期に合わせて、"
                "貯蓄と運用の違いを学んでみよう。"
            )
        else:
            st.write(
                "🌳 **長期的な資産形成を学ぶ**\n\n"
                "複利や積立、分散投資について調べてみよう。"
            )

        st.write(f"**重視したいこと：** {priority}")
        st.write(f"**次に学ぶテーマ：** {learning}")

        st.info(
            "これは学習用の診断であり、"
            "個人に合う投資商品を決定・推奨するものではありません。"
        )

# ---------- 4. 基礎知識 ----------
elif page == "📚 基礎知識":
    st.header("投資の基礎知識")

    with st.expander("複利とは？", expanded=True):
        st.write(
            "運用で得た利益も含めて、その後の運用を続ける仕組み。"
            "期間が長くなると、利益が次の利益を生む効果が表れます。"
        )

    with st.expander("積立投資とは？"):
        st.write(
            "決まった金額を定期的に投資する方法。"
            "価格が変動する商品では、購入価格も毎回変わります。"
        )

    with st.expander("リスクとリターンの関係"):
        st.write(
            "リターンは運用の成果、リスクは一般に成果の振れ幅を指します。"
            "高いリターンが必ず得られる方法はありません。"
        )

    with st.expander("長期・分散投資とは？"):
        st.write(
            "長期間続けることや、投資先を分けることによって、"
            "値動きとの付き合い方を考える方法です。"
            "損失を必ず防げるわけではありません。"
        )

st.divider()
st.caption(
    "このアプリは金融教育を目的としたシミュレーションです。"
    "実際の投資成果を予測・保証するものではありません。"
)
