import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="未来のお金シミュレーター",
    page_icon="🌿",
    layout="wide",
)

# ---------- Design ----------
st.markdown("""
<style>
    .stApp { background: #f7faf7; color: #23352c; }
    [data-testid="stHeader"] { background: rgba(247,250,247,0.9); }
    h1, h2, h3 { color: #24583f; }
    .hero {
        background: linear-gradient(120deg, #e4f2e7, #f4faf4);
        border: 1px solid #d2e6d7; padding: 1.35rem 1.5rem;
        border-radius: 18px; margin-bottom: 1rem;
    }
    .hero p { margin-bottom: 0; color: #466653; }
    .step-card {
        background: white; border: 1px solid #dce9df;
        padding: 1rem 1.15rem; border-radius: 14px; margin-bottom: .7rem;
    }
    .small-note { color: #63766a; font-size: .9rem; }
    div[data-testid="stMetric"] {
        background: white; border: 1px solid #dce9df;
        padding: 12px 14px; border-radius: 14px;
    }
    div.stButton > button {
        background: #2e714b; color: white; border: 0; border-radius: 10px;
    }
    div.stButton > button:hover { background: #24583f; color: white; }
</style>
""", unsafe_allow_html=True)

def yen(value):
    return f"¥{value:,.0f}"

def simulate(initial, monthly, annual_rate, years):
    """月末に積立する想定の簡易シミュレーション。税金・手数料は含まない。"""
    balance = float(initial)
    rows = [{"年数": 0, "資産額": balance, "元本": balance}]
    monthly_rate = annual_rate / 100 / 12
    for month in range(1, years * 12 + 1):
        balance = balance * (1 + monthly_rate) + monthly
        if month % 12 == 0:
            year = month // 12
            principal = initial + monthly * month
            rows.append({"年数": year, "資産額": balance, "元本": principal})
    return pd.DataFrame(rows)

st.markdown("""
<div class="hero">
  <h1>🌿 未来のお金シミュレーター</h1>
  <p>お金の増え方を試して、投資の基本を学ぼう。知ることから、未来の選択肢を広げよう。</p>
</div>
""", unsafe_allow_html=True)

page = st.radio(
    "ページを選ぶ",
    ["🏠 資産シミュレーション", "📊 3パターン比較", "🔎 投資スタイル診断", "🌱 投資の始め方"],
    horizontal=True,
    label_visibility="collapsed",
)

# ---------- Compound-interest simulator ----------
if page == "🏠 資産シミュレーション":
    st.header("資産シミュレーション")
    st.write("毎月の積立額や想定利回りを変えて、将来の資産額を試算できます。")
    left, right = st.columns([1, 1.7], gap="large")
    with left:
        initial = st.number_input("最初に用意するお金（円）", min_value=0, max_value=100_000_000, value=100_000, step=10_000)
        monthly = st.number_input("毎月積み立てる金額（円）", min_value=0, max_value=1_000_000, value=10_000, step=1_000)
        rate = st.slider("年利の想定（%）", min_value=0.0, max_value=10.0, value=3.0, step=0.5)
        years = st.slider("運用する期間（年）", min_value=1, max_value=50, value=20)
    result = simulate(initial, monthly, rate, years)
    final_assets = float(result.iloc[-1]["資産額"])
    principal = float(result.iloc[-1]["元本"])
    with right:
        m1, m2, m3 = st.columns(3)
        m1.metric("将来の資産額（試算）", yen(final_assets))
        m2.metric("積み立てた元本", yen(principal))
        m3.metric("運用による増減（試算）", yen(final_assets - principal))
        st.line_chart(result.set_index("年数")[["資産額", "元本"]])
        st.caption("※一定の利回りで毎月複利運用できたと仮定した試算です。税金・手数料・物価変動は含まず、実際の運用成果を予測・保証するものではありません。")

# ---------- Three scenarios ----------
elif page == "📊 3パターン比較":
    st.header("3パターンを比べてみよう")
    st.write("同じ積立条件で、想定利回りが違うと結果がどう変わるかを比較します。")
    c1, c2, c3 = st.columns(3)
    with c1:
        initial = st.number_input("最初のお金（円）", min_value=0, max_value=100_000_000, value=100_000, step=10_000, key="compare_initial")
    with c2:
        monthly = st.number_input("毎月の積立額（円）", min_value=0, max_value=1_000_000, value=10_000, step=1_000, key="compare_monthly")
    with c3:
        years = st.slider("期間（年）", min_value=1, max_value=50, value=20, key="compare_years")
    st.markdown("#### それぞれの想定利回り")
    r1, r2, r3 = st.columns(3)
    with r1:
        rate_a = st.number_input("パターンA（%）", min_value=0.0, max_value=10.0, value=0.1, step=0.1, format="%.1f")
    with r2:
        rate_b = st.number_input("パターンB（%）", min_value=0.0, max_value=10.0, value=2.0, step=0.5, format="%.1f")
    with r3:
        rate_c = st.number_input("パターンC（%）", min_value=0.0, max_value=10.0, value=5.0, step=0.5, format="%.1f")
    data = []
    curves = {}
    for name, r in [("A", rate_a), ("B", rate_b), ("C", rate_c)]:
        df = simulate(initial, monthly, r, years)
        curves[f"パターン{name}（年利{r:g}%）"] = df.set_index("年数")["資産額"]
        data.append({"パターン": name, "想定年利": f"{r:g}%", "最終資産額（試算）": yen(float(df.iloc[-1]["資産額"])), "元本": yen(float(df.iloc[-1]["元本"]))})
    chart = pd.DataFrame(curves)
    st.line_chart(chart)
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    st.info("ここでの利回りは比較のための仮定です。パターンA・B・Cは、実際の商品やリスクの程度を表すものではありません。投資の利回りは一定ではなく、元本割れする可能性もあります。")

# ---------- Learning style diagnostic ----------
elif page == "🔎 投資スタイル診断":
    st.header("投資について、何から学ぶ？")
    st.write("これは金融商品をおすすめする診断ではなく、学習テーマを考えるための簡単なチェックです。")
    q1 = st.radio("1. お金を使う予定はどれくらい先？", ["数か月以内", "1〜5年くらい先", "10年以上先", "まだ決まっていない"])
    q2 = st.radio("2. お金の運用について、今の気持ちに近いのは？", ["できるだけ仕組みやリスクを知ってから考えたい", "少額の例で試しながら学びたい", "値動きの理由や経済のことを知りたい", "まだよくわからない"])
    q3 = st.radio("3. 今いちばん知りたいことは？", ["貯金と投資の違い", "NISAや口座の仕組み", "リスクとリターン", "複利や長期積立の計算"])
    if st.button("学習テーマを見る"):
        topics = []
        if q1 == "数か月以内":
            topics.append("近いうちに使うお金と、長期で準備するお金の分け方")
        elif q1 == "1〜5年くらい先":
            topics.append("使う時期に合わせた資金計画と、値動きのリスク")
        elif q1 == "10年以上先":
            topics.append("長期・積立・分散の考え方と複利")
        else:
            topics.append("お金の目的を整理する方法")
        topics.append({
            "できるだけ仕組みやリスクを知ってから考えたい": "元本割れ・手数料・商品の仕組み",
            "少額の例で試しながら学びたい": "シミュレーションで条件を変えて比較する",
            "値動きの理由や経済のことを知りたい": "株価・金利・景気の基本",
            "まだよくわからない": "貯金・投資・リスクの基本用語",
        }[q2])
        topics.append({
            "貯金と投資の違い": "貯金と投資の特徴の比較",
            "NISAや口座の仕組み": "NISAの制度と口座の基本",
            "リスクとリターン": "利益の可能性と損失の可能性",
            "複利や長期積立の計算": "複利シミュレーション",
        }[q3])
        st.success("まず学んでみるテーマ")
        for topic in dict.fromkeys(topics):
            st.markdown(f"- {topic}")
        st.caption("回答結果は学習のヒントです。実際の投資判断は、年齢、目的、家計、リスク許容度などを踏まえ、保護者など信頼できる大人とも相談して考えましょう。")

# ---------- Beginner guide ----------
elif page == "🌱 投資の始め方":
    st.header("投資の始め方ガイド")
    st.write("投資が初めての人向けに、基本を順番に確認できるページです。焦って始める必要はありません。まずは知ることから始めましょう。")

    st.subheader("はじめる前の4ステップ")
    steps = [
        ("STEP 1｜お金の目的を考える", "何のために、いつ使うお金なのかを考えます。近いうちに必要なお金と、当面使う予定のないお金は分けて考えましょう。"),
        ("STEP 2｜貯金と投資の違いを知る", "貯金は必要なときに使うお金を保管する方法の一つです。投資は利益が得られる可能性がある一方、値下がりして損をする可能性もあります。"),
        ("STEP 3｜仕組み・費用・リスクを調べる", "株式、債券、投資信託などの特徴を比べます。値動き、手数料、換金しやすさなどを理解し、わからないまま契約しないことが大切です。"),
        ("STEP 4｜必要な条件を確認する", "実際に口座を開く前に、年齢などの条件、口座の種類、商品や手数料を確認します。未成年の人は、保護者と一緒に公式情報を確認しましょう。"),
    ]
    for title, desc in steps:
        st.markdown(f'<div class="step-card"><h3>{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)

    st.subheader("NISAってどんな制度？")
    st.markdown("""
    NISAは、一定の条件のもとで、投資で得た利益が非課税になる制度です。投資そのものの損失を防ぐ制度ではありません。
    """)
    with st.expander("NISAのポイントを確認する"):
        st.markdown("""
        - **税金の優遇**：対象となる投資から得た利益が、通常の課税口座とは異なり非課税になります。
        - **商品は自分で確認**：NISA口座なら何を買っても安全、という意味ではありません。対象商品や費用を確認する必要があります。
        - **元本保証ではない**：価格が下がれば、投資した金額を下回ることがあります。
        - **年齢などの条件**：口座開設には制度上の条件があります。未成年の人は最新の公式情報を保護者と確認しましょう。
        - **公式情報を確認**：制度の詳細は変わることがあるため、金融庁のNISA特設サイトなどで最新情報を確認してください。
        """)
        st.link_button("金融庁のNISA特設サイトを開く", "https://www.fsa.go.jp/policy/nisa2/")

    st.subheader("リスクと注意点")
    risk_items = [
        ("元本割れ", "投資した金額より、売却したときの金額が少なくなることがあります。"),
        ("価格の変動", "経済や企業の状況などによって、商品の価格は上下します。"),
        ("手数料", "購入・保有・売却などで費用がかかる商品があります。"),
        ("分散してもリスクはゼロにならない", "複数の商品や地域に分けることでリスクを抑えられる場合がありますが、損失を完全に防ぐものではありません。"),
        ("うまい話に注意", "「必ず儲かる」「絶対に損しない」といった説明をうのみにせず、信頼できる公式情報を確認しましょう。"),
    ]
    for title, desc in risk_items:
        with st.expander(title):
            st.write(desc)

    st.subheader("投資用語集")
    terms = [
        ("元本", "最初に投資したお金や、積み立てたお金。"),
        ("利回り", "投資したお金に対して、一定期間でどれくらいの収益があったかを示す割合。将来の利回りが決まっているという意味ではありません。"),
        ("複利", "得られた利益も運用に回すことで、その利益にも次の利益が生まれる仕組み。実際の投資では利益が毎回出るとは限りません。"),
        ("投資信託", "多くの人から集めたお金をまとめ、運用の専門家などが決められた方針に沿って運用する金融商品。価格は変動します。"),
        ("株式", "企業が資金を集めるために発行するもの。株価は変動し、企業の業績などによって損失が生じることがあります。"),
        ("債券", "国や企業などがお金を借りるために発行するもの。発行体の信用や市場金利などにより価格が変動することがあります。"),
        ("分散投資", "投資先や地域、時期などを分ける考え方。リスクを抑える助けになる場合がありますが、損失をなくすものではありません。"),
        ("積立投資", "決めた金額を定期的に投資していく方法。買うタイミングを分けられますが、利益が保証されるわけではありません。"),
    ]
    for term, explanation in terms:
        with st.expander(term):
            st.write(explanation)

    st.subheader("ミニクイズ")
    st.write("学んだ内容を3問で確認してみよう！")
    quiz = [
        {
            "q": "1. 投資について正しい説明はどれ？",
            "options": [
                "投資すれば必ず利益が出る",
                "投資では利益の可能性と損失の可能性の両方がある",
                "短い期間なら必ず安全",
                "手数料はどの商品でも同じ",
            ],
            "answer": "投資では利益の可能性と損失の可能性の両方がある",
            "explain": "投資では価格が上がることも下がることもあり、元本割れする可能性があります。",
        },
        {
            "q": "2. NISAについて正しい説明はどれ？",
            "options": [
                "損失を国が補償してくれる制度",
                "すべての商品が必ず値上がりする制度",
                "一定の条件のもとで投資の利益が非課税になる制度",
                "預金の利息が必ず高くなる制度",
            ],
            "answer": "一定の条件のもとで投資の利益が非課税になる制度",
            "explain": "NISAは税制上の優遇制度で、投資の損失を防いだり、利益を保証したりする制度ではありません。",
        },
        {
            "q": "3. 分散投資について正しい説明はどれ？",
            "options": [
                "投資先を分けてリスクを抑えることを目指す考え方",
                "一つの商品だけに全額を投資すること",
                "損失が絶対に出ないようにする方法",
                "必ず高い利益を出す方法",
            ],
            "answer": "投資先を分けてリスクを抑えることを目指す考え方",
            "explain": "分散はリスクを抑える助けになる場合がありますが、損失を完全に防ぐものではありません。",
        },
    ]
    with st.form("beginner_quiz"):
        answers = []
        for i, item in enumerate(quiz):
            answers.append(st.radio(item["q"], item["options"], key=f"quiz_{i}"))
        submitted = st.form_submit_button("答え合わせ")
    if submitted:
        score = sum(answers[i] == quiz[i]["answer"] for i in range(len(quiz)))
        st.success(f"結果：{score} / {len(quiz)} 問正解！")
        for i, item in enumerate(quiz):
            if answers[i] == item["answer"]:
                st.markdown(f"**{i+1}問目：正解！**")
            else:
                st.markdown(f"**{i+1}問目：もう一度確認しよう。** 正しい答え：{item['answer']}")
            st.caption(item["explain"])

    st.markdown("---")
    st.caption("学習用の情報です。特定の金融商品をすすめるものではありません。制度の詳細や口座開設条件は変わることがあるため、金融庁などの公式情報を確認してください。")

st.markdown("---")
st.caption("🌿 このアプリは金融教育・学習用です。シミュレーションは仮定に基づく計算であり、将来の利益や投資成果を保証するものではありません。")
