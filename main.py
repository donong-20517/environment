import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# 환경 행동의 과학: 일상 속 행동이 환경에 미치는 영향을 배우는 앱
# 실행: streamlit run main.py
# ============================================================

st.set_page_config(
    page_title="환경 행동의 과학",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# 1. 공통 디자인 설정
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    .stApp { background: linear-gradient(180deg, #f4fbf6 0%, #ffffff 38%); }
    .main .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px; }
    .hero {
        background: linear-gradient(120deg, #e0f4e7, #f1faf4);
        border: 1px solid #d2ead9; border-radius: 22px;
        padding: 1.6rem 1.8rem; margin-bottom: 1.2rem;
    }
    .eyebrow { color: #328354; font-size: .82rem; font-weight: 800; letter-spacing: .08em; }
    .hero h1 { color: #174d32; font-size: 2.2rem; margin: .35rem 0 .55rem 0; }
    .hero p { color: #41634f; font-size: 1rem; line-height: 1.8; margin: 0; }
    .step {
        background: white; border: 1px solid #dcebe0; border-radius: 16px;
        padding: 1.1rem 1.2rem; height: 100%;
    }
    .step-no { color: #34875a; font-size: .78rem; font-weight: 800; }
    .step h3 { color: #174d32; font-size: 1.08rem; margin: .35rem 0 .6rem 0; }
    .step p { color: #42594a; line-height: 1.75; margin-bottom: 0; }
    .small-note { color: #6a7e70; font-size: .84rem; line-height: 1.6; }
    div[data-testid="stMetric"] {
        background: #f2faf4; border: 1px solid #d9eddf;
        padding: 14px; border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 2. 활동별 과학 정보와 시뮬레이션 계수
# -----------------------------
# 수치는 모든 상황에 적용되는 보편적인 측정값이 아니라,
# 학생들이 계산 구조를 이해하도록 설정한 '교육용 예시 가정'입니다.
# 실제 효과는 제품·전력원·지역·재활용 시설·사용 기간 등에 따라 달라집니다.
ACTIONS = {
    "페트병 라벨 제거 후 분리배출": {
        "category": "자원순환",
        "unit": "회",
        "step1": "페트병을 비우고, 가능한 경우 라벨과 뚜껑을 분리한 뒤 지역 분리배출 지침에 맞게 배출합니다.",
        "step2": (
            "**선별과 재질 분리의 원리**\n\n"
            "페트병 몸체는 주로 폴리에틸렌 테레프탈레이트(PET)라는 열가소성 폴리에스터로 만들어집니다. "
            "라벨은 폴리프로필렌(PP), 폴리스티렌(PS) 등 다른 플라스틱이나 종이인 경우가 있어 몸체와 재질이 다를 수 있습니다. "
            "재활용 시설에서는 재질·색·밀도·광학적 특성 등을 이용해 물질을 선별합니다. "
            "라벨과 내용물이 많이 남아 있으면 선별과 세척 과정에서 오염원이 늘어날 수 있습니다.\n\n"
            "분리된 PET는 세척·분쇄되어 플레이크가 되고, 추가 정제와 용융·재가공을 거쳐 재생 원료로 사용될 수 있습니다. "
            "PET는 에스터 결합을 포함하는 고분자이며, 열을 가하면 녹여 다시 성형할 수 있는 열가소성 수지입니다. "
            "다만 반복적인 열 이력과 수분·오염은 고분자 사슬의 분해나 품질 저하를 일으킬 수 있어 세척과 품질 관리가 중요합니다."
        ),
        "step3": (
            "라벨을 제거하면 재질이 다른 물질이 PET 재활용 흐름에 섞이는 것을 줄이는 데 도움이 됩니다. "
            "이는 선별·세척 효율과 재생 원료의 품질을 높일 가능성이 있습니다. "
            "단, 라벨 제거 방식과 배출 방법은 지역별 지침을 우선해야 하며, 라벨 제거만으로 재활용이 보장되는 것은 아닙니다."
        ),
        "impact": "재질이 다른 라벨의 혼입 및 선별 오염 가능성 감소",
        "factor": 0.0,
        "factor_label": "탄소량 대신 재질 분리 효과를 설명",
        "science": "고분자·재질 선별·재활용",
        "quiz": 0,
    },
    "텀블러 사용": {
        "category": "자원순환",
        "unit": "회",
        "step1": "일회용 컵 대신 개인 텀블러를 사용하고, 사용 후 세척하여 반복해서 사용합니다.",
        "step2": (
            "**제품 전 과정 평가(LCA)와 손익분기점**\n\n"
            "일회용 컵은 원료 채취, 원료 가공, 제조, 운송, 폐기 과정에서 자원과 에너지를 사용합니다. "
            "텀블러도 금속·유리·플라스틱 원료를 채취하고 제조하는 과정에서 환경 부담이 발생합니다. "
            "따라서 텀블러가 무조건 처음부터 환경 부담이 작은 것은 아닙니다.\n\n"
            "텀블러의 제조 단계 환경 부담을 반복 사용에 따른 일회용 컵 대체 효과가 누적해서 상쇄하는 시점이 "
            "손익분기점입니다. 이 시점은 텀블러 재질과 무게, 세척에 필요한 물·에너지, 대체하는 컵의 종류와 "
            "사용 횟수에 따라 달라집니다. 오래 사용하고 효율적으로 세척할수록 유리해질 가능성이 커집니다."
        ),
        "step3": (
            "일회용 컵을 실제로 대체한 횟수가 늘어날수록 일회용 컵의 원료·제조·폐기 수요를 줄일 수 있습니다. "
            "다만 정확한 탄소 저감량은 텀블러의 재질과 사용 기간, 세척 방식 등을 포함한 전 과정 평가가 필요합니다."
        ),
        "impact": "반복 사용으로 일회용 컵의 제조·폐기 수요를 줄임",
        "factor": 0.025,
        "factor_label": "1회당 0.025 kg CO₂e 감축으로 가정",
        "science": "전 과정 평가·손익분기점",
        "quiz": 1,
    },
    "사용하지 않는 플러그·전자제품 전원 끄기": {
        "category": "기후변화",
        "unit": "시간",
        "step1": "사용하지 않는 전자제품의 전원을 끄고, 대기전력이 계속 소비되는 기기는 안전과 제품 설명서를 확인한 뒤 전원 차단을 실천합니다.",
        "step2": (
            "**전기에너지와 발전 과정의 온실가스**\n\n"
            "일부 전자제품은 전원을 끈 것처럼 보여도 리모컨 수신, 시계 표시, 네트워크 대기 등을 위해 "
            "소량의 전력을 계속 소비합니다. 이를 대기전력이라고 합니다. "
            "전력 소비량은 전력(W)에 사용 시간(h)을 곱해 와트시(Wh)로 계산할 수 있습니다.\n\n"
            "전력 수요가 줄면 전력 시스템에서 공급해야 할 전력량도 줄어듭니다. 전력 생산에 화석연료 발전이 "
            "포함된 경우 석탄·천연가스 등의 연소량과 이에 따른 이산화탄소 배출을 줄이는 데 기여할 수 있습니다. "
            "다만 실제 발전원 구성과 시간대별 전력 수요에 따라 감축 효과는 달라집니다."
        ),
        "step3": (
            "대기전력을 줄이면 전력 사용량이 감소하고, 전력 생산 과정의 온실가스 배출도 간접적으로 줄일 수 있습니다. "
            "아래 시뮬레이터는 평균 대기전력 5 W인 기기를 차단한 시간과 전력 배출계수 0.4 kg CO₂e/kWh를 "
            "가정해 예시 계산을 합니다. 실제 기기별 대기전력은 측정값이 다릅니다."
        ),
        "impact": "전력 사용량 감소 → 발전 연료 수요와 간접 배출 감소",
        "factor": 0.002,
        "factor_label": "차단 1시간당 0.002 kg CO₂e 감축 가정",
        "science": "대기전력·에너지 전환·연소",
        "quiz": 2,
    },
    "잔반 남기지 않기": {
        "category": "기후변화",
        "unit": "끼",
        "step1": "먹을 만큼만 배식하고, 먹을 수 있는 음식을 남기지 않도록 식사량을 조절합니다.",
        "step2": (
            "**식품 생산의 자원 투입과 유기물 분해**\n\n"
            "음식은 재배·사육, 가공, 냉장·냉동, 운송, 조리 과정에서 토지·물·에너지 등을 사용합니다. "
            "먹지 않고 버려지면 그 생산 과정에 투입된 자원도 충분히 활용되지 못한 셈입니다.\n\n"
            "음식물 쓰레기가 산소가 부족한 매립 환경에서 미생물에 의해 분해되면 메탄(CH₄)이 생성될 수 있습니다. "
            "메탄은 이산화탄소보다 대기 중 체류 기간은 짧지만, 일정 기간을 기준으로 비교하면 강한 온실효과를 "
            "나타내는 온실가스입니다. 음식물 쓰레기는 처리 시설에서 퇴비화·사료화·혐기성 소화 등으로 처리되기도 하며, "
            "처리 방식에 따라 배출과 자원 회수 효과가 달라집니다."
        ),
        "step3": (
            "잔반을 줄이면 음식 생산에 들어간 자원의 낭비를 줄이고, 음식물 쓰레기의 수거·처리 부담도 낮출 수 있습니다. "
            "매립 과정에서 발생할 수 있는 메탄 배출을 줄이는 데도 기여할 수 있지만, 실제 효과는 음식물의 종류와 "
            "처리 방식에 따라 달라집니다."
        ),
        "impact": "식품 생산 자원 낭비 및 음식물 폐기물 처리 부담 감소",
        "factor": 0.08,
        "factor_label": "잔반을 줄인 1끼당 0.08 kg CO₂e 감축 가정",
        "science": "유기물 분해·혐기성 소화·메탄",
        "quiz": 3,
    },
    "장바구니 사용": {
        "category": "자원순환",
        "unit": "회",
        "step1": "물건을 구매할 때 새 비닐봉지를 받는 대신 이미 가지고 있는 장바구니를 사용합니다.",
        "step2": (
            "**고분자 재료와 일회용품의 전 과정**\n\n"
            "일반적인 비닐봉지는 폴리에틸렌(PE)과 같은 고분자로 만들어집니다. "
            "에틸렌 단위가 반복적으로 연결된 긴 사슬 구조이며, 가볍고 유연하지만 사용 시간이 짧으면 "
            "제조에 투입된 원료와 에너지가 충분히 활용되지 못할 수 있습니다.\n\n"
            "장바구니는 한 번 만들 때 더 많은 재료와 에너지가 필요할 수도 있습니다. "
            "따라서 환경적 이점은 장바구니를 얼마나 오래, 여러 번 사용하여 일회용 봉투를 실제로 대체하는지에 달려 있습니다. "
            "사용 후 폐기까지 포함한 전 과정 평가로 비교해야 합니다."
        ),
        "step3": (
            "장바구니를 반복 사용하면 새 일회용 봉투의 생산과 폐기 수요를 줄일 수 있습니다. "
            "장바구니를 한두 번만 사용하고 버리기보다 오래 사용하는 것이 중요합니다."
        ),
        "impact": "일회용 봉투의 원료·제조·폐기 수요 감소",
        "factor": 0.01,
        "factor_label": "1회당 0.01 kg CO₂e 감축 가정",
        "science": "고분자·자원 소비·전 과정 평가",
        "quiz": 4,
    },
    "종이 양면 인쇄 및 이면지 사용": {
        "category": "자원순환",
        "unit": "장",
        "step1": "인쇄할 때 양면 인쇄를 선택하고, 한쪽 면만 사용한 종이는 메모나 연습용으로 다시 사용합니다.",
        "step2": (
            "**셀룰로오스 섬유와 종이 재활용**\n\n"
            "종이의 주성분은 식물 세포벽을 이루는 셀룰로오스입니다. 셀룰로오스는 포도당 단위가 길게 연결된 "
            "다당류이며, 섬유들이 서로 얽히고 수소 결합 등을 형성해 종이의 형태를 유지합니다.\n\n"
            "종이를 새로 생산하려면 목재 펄프 제조와 건조 등에 물과 에너지가 필요합니다. "
            "양면 인쇄와 이면지 사용은 같은 양의 정보를 표현하는 데 필요한 종이 사용량을 줄여 "
            "원료와 제조 에너지 수요를 낮추는 방법입니다. 종이 재활용 과정에서는 물에 풀어 섬유를 분리하고 "
            "잉크·이물질을 제거한 뒤 다시 종이를 만듭니다. 섬유는 재활용을 반복할수록 짧아지고 약해질 수 있습니다."
        ),
        "step3": (
            "종이 사용량을 줄이면 펄프 생산과 종이 제조에 필요한 목재·물·에너지 사용을 줄이는 데 도움이 됩니다. "
            "재활용만큼이나 처음부터 덜 사용하는 것이 자원 절약에 중요합니다."
        ),
        "impact": "종이 원료와 제조 에너지 사용량 감소",
        "factor": 0.004,
        "factor_label": "절약한 종이 1장당 0.004 kg CO₂e 감축 가정",
        "science": "셀룰로오스·수소 결합·섬유 재활용",
        "quiz": 0,
    },
    "가까운 거리는 걷거나 자전거 이용": {
        "category": "기후변화",
        "unit": "km",
        "step1": "대중교통이나 자동차 대신 안전하게 이동할 수 있는 가까운 거리는 걷거나 자전거를 이용합니다.",
        "step2": (
            "**연료 연소와 온실가스 배출**\n\n"
            "내연기관 자동차는 연료 속 탄화수소를 산소와 반응시켜 에너지를 얻습니다. "
            "완전연소가 일어나면 주로 이산화탄소와 물이 생성되며, 이 과정에서 연료에 포함된 탄소가 "
            "이산화탄소로 대기 중에 배출됩니다. 실제 엔진에서는 조건에 따라 질소산화물·일산화탄소·미세먼지 "
            "등도 발생할 수 있습니다.\n\n"
            "자동차 이동을 걷기나 자전거로 대체하면 해당 이동에 필요한 연료 소비를 줄일 수 있습니다. "
            "다만 대체한 거리, 차량의 연비, 탑승 인원, 전기차 여부 등에 따라 효과가 달라집니다."
        ),
        "step3": (
            "자동차 이동을 실제로 대체한 거리가 늘어나면 연료 소비와 배기관 온실가스 배출을 줄이는 데 기여합니다. "
            "시뮬레이터는 일반 승용차의 예시 배출계수 0.15 kg CO₂e/km를 적용합니다. "
            "이는 차량별 실측값이 아닌 단순화한 교육용 가정입니다."
        ),
        "impact": "자동차 연료 연소 감소 → 이산화탄소 등 배출 감소",
        "factor": 0.15,
        "factor_label": "자동차 대체 1 km당 0.15 kg CO₂e 감축 가정",
        "science": "연소 반응·탄소 순환·온실효과",
        "quiz": 2,
    },
}

QUIZ = [
    {
        "question": "페트병 몸체와 라벨을 분리하는 것이 재활용에 도움이 되는 주된 이유는 무엇일까요?",
        "options": [
            "서로 다른 재질이 섞여 선별·재생 원료의 품질을 떨어뜨릴 가능성을 줄이기 위해",
            "PET가 물과 만나면 금속으로 변하기 때문에",
            "라벨을 제거하면 페트병의 탄소 원자가 사라지기 때문에",
        ],
        "answer": 0,
        "explain": "페트병 몸체와 라벨은 서로 다른 재질일 수 있습니다. 재질을 분리하면 선별과 세척 과정의 오염을 줄이고 재생 원료의 품질을 높이는 데 도움이 됩니다.",
    },
    {
        "question": "텀블러의 환경적 이점이 커지려면 가장 중요한 조건은 무엇일까요?",
        "options": [
            "구매 직후 바로 버리는 것",
            "제조 부담을 여러 번의 사용으로 상쇄할 만큼 반복해서 사용하는 것",
            "매번 뜨거운 물로 오래 세척하는 것",
        ],
        "answer": 1,
        "explain": "텀블러도 제조 과정에서 자원과 에너지를 사용합니다. 여러 번 사용해 일회용 컵을 실제로 대체해야 제조 단계의 환경 부담을 상쇄할 수 있습니다.",
    },
    {
        "question": "대기전력을 차단하면 온실가스 배출이 줄어들 수 있는 이유는 무엇일까요?",
        "options": [
            "전기가 사라지면서 대기 중 산소가 늘어나기 때문에",
            "전력 수요가 줄어 발전에 필요한 연료 소비와 배출을 줄일 수 있기 때문에",
            "플러그가 이산화탄소를 직접 흡수하기 때문에",
        ],
        "answer": 1,
        "explain": "전력 사용량이 줄면 필요한 발전량도 줄어들 수 있습니다. 화석연료 발전이 포함된 전력 시스템에서는 연료 연소와 이산화탄소 배출 감소로 이어질 수 있습니다.",
    },
    {
        "question": "음식물 쓰레기가 산소가 부족한 환경에서 분해될 때 발생할 수 있는 온실가스는 무엇일까요?",
        "options": ["산소(O₂)", "메탄(CH₄)", "헬륨(He)"],
        "answer": 1,
        "explain": "산소가 부족한 환경에서 미생물이 유기물을 분해하는 과정인 혐기성 분해에서는 메탄이 생성될 수 있습니다. 메탄은 온실가스입니다.",
    },
    {
        "question": "장바구니를 사용할 때 환경적 이점을 높이는 행동은 무엇일까요?",
        "options": [
            "새 장바구니를 매번 구매하는 것",
            "장바구니를 한 번 사용하고 폐기하는 것",
            "가지고 있는 장바구니를 오래 반복해서 사용하는 것",
        ],
        "answer": 2,
        "explain": "장바구니도 생산 과정에서 자원과 에너지가 필요합니다. 기존 장바구니를 오래 반복 사용하여 일회용 봉투를 실제로 대체하는 것이 중요합니다.",
    },
]

# -----------------------------
# 3. 사이드바: 메뉴와 학습자 설정
# -----------------------------
with st.sidebar:
    st.markdown("## 🌿 환경 행동의 과학")
    st.caption("작은 행동 뒤에 숨은 과학을 발견해요.")
    page = st.radio(
        "탐색 메뉴",
        [
            "홈(기획 의도)",
            "일상 행동 과학 분석기",
            "나의 환경 기여도 시뮬레이터",
            "과학 원리 퀴즈",
        ],
        label_visibility="visible",
    )
    st.divider()
    st.markdown("### 나의 학습 설정")
    grade = st.selectbox("학년", ["중학교 1학년", "중학교 2학년", "중학교 3학년", "고등학교 1학년", "고등학교 2학년", "고등학교 3학년"])
    interest = st.selectbox("관심 분야", ["전체", "기후변화", "해양생태계", "자원순환"])
    st.caption("선택한 설정은 설명과 활동을 탐색할 때 참고합니다.")
    st.divider()
    st.markdown(
        "<div class='small-note'>이 앱의 수치 예시는 원리를 이해하기 위한 단순화된 가정입니다. 실제 환경 효과는 조건에 따라 달라집니다.</div>",
        unsafe_allow_html=True,
    )

# -----------------------------
# 4. 공통 함수
# -----------------------------
def show_hero(kicker: str, title: str, description: str):
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{kicker}</div>
            <h1>{title}</h1>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def action_matches_interest(action: dict, selected_interest: str) -> bool:
    """관심 분야에 맞는 활동인지 확인합니다."""
    if selected_interest == "전체":
        return True
    if selected_interest == "해양생태계":
        # 해양생태계 관련 행동도 자원순환과 연결되는 경우가 많아,
        # 플라스틱 사용 및 폐기물 감축 행동을 함께 보여 줍니다.
        return action["category"] == "자원순환"
    return action["category"] == selected_interest


def render_action_steps(action_name: str):
    """선택한 활동을 행동-과학 작용-환경 영향의 3단계로 출력합니다."""
    data = ACTIONS[action_name]
    cols = st.columns(3)
    steps = [
        ("STEP 1", "행동의 시작", data["step1"]),
        ("STEP 2", "과학적·화학적 작용", data["step2"]),
        ("STEP 3", "실질적 환경 영향", data["step3"]),
    ]
    for col, (number, heading, body) in zip(cols, steps):
        with col:
            st.markdown(
                f"<div class='step'><div class='step-no'>{number}</div><h3>{heading}</h3></div>",
                unsafe_allow_html=True,
            )
            st.markdown(body)
    st.info(f"핵심 연결 고리: **{data['impact']}**")


# -----------------------------
# 5. 홈 화면
# -----------------------------
if page == "홈(기획 의도)":
    show_hero(
        "SCIENCE IN EVERYDAY ACTION",
        "작은 행동에는 과학이 숨어 있습니다.",
        "분리배출, 텀블러 사용, 잔반 줄이기처럼 익숙한 행동이 어떤 물리적·화학적·생태학적 과정을 거쳐 환경에 영향을 주는지 살펴보는 학습 공간입니다.",
    )
    st.subheader("환경보호를 '왜' 실천해야 하는지 과학으로 이해하기")
    st.write(
        "환경보호 활동은 단순히 좋은 일을 하는 데서 끝나지 않습니다. "
        "재료의 성질, 화학 반응, 에너지 전환, 미생물의 분해 작용처럼 구체적인 과학 원리가 행동과 환경 변화를 연결합니다. "
        "이 앱은 그 과정을 세 단계로 나누어 보여 줍니다."
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 🧤 행동")
        st.write("내가 일상에서 실제로 바꿀 수 있는 행동을 선택합니다.")
    with c2:
        st.markdown("### ⚗️ 과학적 작용")
        st.write("고분자, 연소, 분해, 에너지 소비 등 행동 뒤의 원리를 살펴봅니다.")
    with c3:
        st.markdown("### 🌏 환경 변화")
        st.write("자원 소비와 폐기물, 온실가스 배출에 어떤 변화가 생기는지 이해합니다.")
    st.divider()
    st.subheader("이용 방법")
    st.markdown(
        """
        1. **일상 행동 과학 분석기**에서 궁금한 행동을 선택합니다.
        2. 세 단계 설명을 읽고 과학적 인과관계를 확인합니다.
        3. **환경 기여도 시뮬레이터**에서 일주일 실천 횟수에 따른 예시 효과를 계산합니다.
        4. **과학 원리 퀴즈**로 배운 내용을 확인합니다.
        """
    )
    st.warning(
        "중요: 시뮬레이터의 탄소 저감 계수는 교육용 가정값입니다. "
        "제품별 전 과정 평가나 지역별 배출계수를 적용한 공식 측정값이 아닙니다."
    )
    st.caption(f"현재 학습 설정: {grade} · 관심 분야: {interest}")

# -----------------------------
# 6. 일상 행동 과학 분석기
# -----------------------------
elif page == "일상 행동 과학 분석기":
    show_hero(
        "EXPLORE THE MECHANISM",
        "일상 행동 과학 분석기",
        "행동 하나를 선택하고, 그 행동이 어떤 과학적 원리를 거쳐 환경 변화로 이어지는지 단계별로 살펴보세요.",
    )
    available_actions = [
        name for name, data in ACTIONS.items()
        if action_matches_interest(data, interest)
    ]
    if not available_actions:
        st.info("선택한 관심 분야에 해당하는 활동이 없습니다. 사이드바에서 '전체'를 선택해 보세요.")
    else:
        selected_action = st.selectbox("분석할 환경보호 활동을 선택하세요.", available_actions)
        data = ACTIONS[selected_action]
        st.markdown(f"**분야:** `{data['category']}`　 **관련 과학 개념:** `{data['science']}`")
        render_action_steps(selected_action)
        with st.expander("조금 더 깊이 알아보기: 핵심 개념 정리"):
            if selected_action.startswith("페트병"):
                st.markdown(
                    """
                    - **고분자:** 작은 분자 단위가 반복적으로 연결된 큰 분자입니다.
                    - **PET:** 에스터 결합을 포함하는 폴리에스터로, 음료병 등에 널리 쓰입니다.
                    - **열가소성 수지:** 가열하면 부드러워지거나 녹아 다시 성형할 수 있는 고분자 재료입니다.
                    - **주의:** 페트병의 라벨·뚜껑 재질은 제품마다 다를 수 있으므로 지역별 분리배출 안내를 확인해야 합니다.
                    """
                )
            elif selected_action == "텀블러 사용":
                st.markdown(
                    """
                    - **전 과정 평가(LCA):** 원료 채취부터 제조·운송·사용·폐기까지의 환경 영향을 살피는 방법입니다.
                    - **손익분기점:** 반복 사용으로 절약한 환경 부담이 텀블러 제조 부담을 넘어서는 시점입니다.
                    - **핵심 변수:** 텀블러 재질과 무게, 세척 방식, 실제 사용 횟수, 대체하는 일회용 컵의 종류입니다.
                    """
                )
            elif selected_action.startswith("사용하지 않는"):
                st.markdown(
                    """
                    - **전력량:** 전력(W)과 시간(h)을 곱해 계산하며, 1,000 Wh는 1 kWh입니다.
                    - **대기전력:** 기기가 주 기능을 수행하지 않을 때에도 대기 상태 유지를 위해 소비하는 전력입니다.
                    - **간접 배출:** 전기를 사용하는 장소에서 연기가 나지 않더라도, 전력 생산 과정에서 온실가스가 배출될 수 있습니다.
                    """
                )
            elif selected_action == "잔반 남기지 않기":
                st.markdown(
                    """
                    - **유기물:** 탄소를 포함하는 물질 중 생물체와 관련된 물질을 폭넓게 가리킬 때 사용합니다.
                    - **혐기성 분해:** 산소가 거의 없는 환경에서 미생물이 유기물을 분해하는 과정입니다.
                    - **메탄:** 산소가 부족한 조건에서 유기물이 분해될 때 생성될 수 있는 온실가스입니다.
                    - **처리 방식의 차이:** 매립, 퇴비화, 사료화, 혐기성 소화는 환경 영향과 회수 가능한 자원이 서로 다릅니다.
                    """
                )
            elif selected_action == "장바구니 사용":
                st.markdown(
                    """
                    - **폴리에틸렌(PE):** 에틸렌 단위가 반복된 구조를 가진 대표적인 열가소성 고분자입니다.
                    - **반복 사용:** 장바구니 제조에 든 자원과 에너지를 여러 번의 사용으로 나누어 부담을 낮춥니다.
                    - **핵심:** 새 장바구니를 계속 사기보다 기존 제품을 오래 쓰는 것이 중요합니다.
                    """
                )
            elif selected_action.startswith("종이"):
                st.markdown(
                    """
                    - **셀룰로오스:** 포도당 단위가 연결된 다당류로 식물 세포벽의 주요 성분입니다.
                    - **수소 결합:** 셀룰로오스 사슬 사이의 상호작용 중 하나로 종이 섬유의 결합에 기여합니다.
                    - **섬유의 한계:** 종이 섬유는 재활용 과정에서 짧아지거나 손상되어 무한히 재활용할 수는 없습니다.
                    """
                )
            else:
                st.markdown(
                    """
                    - **연소:** 연료가 산소와 반응해 에너지를 방출하는 화학 반응입니다.
                    - **완전연소:** 탄화수소 연료가 충분한 산소와 반응하면 주로 이산화탄소와 물이 생성됩니다.
                    - **탄소 순환:** 연료 속 탄소가 연소를 통해 이산화탄소로 대기 중에 이동할 수 있습니다.
                    """
                )

# -----------------------------
# 7. 환경 기여도 시뮬레이터
# -----------------------------
elif page == "나의 환경 기여도 시뮬레이터":
    show_hero(
        "MY WEEKLY IMPACT",
        "나의 환경 기여도 시뮬레이터",
        "일주일 동안 실천한 행동의 횟수나 양을 입력해 보세요. 설정된 예시 계수로 누적 효과를 계산합니다.",
    )
    st.info(
        "계산 결과는 비교와 학습을 위한 단순화된 추정치입니다. "
        "실제 감축량을 보증하지 않으며, 제품·지역·전력 구성·처리 방식에 따라 달라집니다."
    )
    sim_options = [
        name for name, data in ACTIONS.items()
        if data["factor"] > 0 and action_matches_interest(data, interest)
    ]
    if not sim_options:
        sim_options = [name for name, data in ACTIONS.items() if data["factor"] > 0]
    selected_sim = st.selectbox("시뮬레이션할 행동", sim_options)
    sim_data = ACTIONS[selected_sim]

    # 활동별 입력 단위에 따라 슬라이더 범위와 설명을 다르게 설정합니다.
    slider_config = {
        "텀블러 사용": (0, 35, 7, "일주일 동안 일회용 컵을 대체한 횟수"),
        "사용하지 않는 플러그·전자제품 전원 끄기": (0, 168, 20, "일주일 동안 대기전력을 차단한 시간"),
        "잔반 남기지 않기": (0, 21, 7, "일주일 동안 잔반을 줄인 식사 횟수"),
        "장바구니 사용": (0, 35, 7, "일회용 봉투 대신 장바구니를 사용한 횟수"),
        "종이 양면 인쇄 및 이면지 사용": (0, 200, 20, "절약한 종이 장수"),
        "가까운 거리는 걷거나 자전거 이용": (0, 100, 10, "자동차 이동을 대체한 거리(km)"),
    }
    min_value, max_value, default_value, slider_label = slider_config[selected_sim]
    count = st.slider(slider_label, min_value, max_value, default_value, 1)
    estimated_kg = count * sim_data["factor"]

    # 교육용 가정값을 적용한 계산 결과를 표시합니다.
    m1, m2, m3 = st.columns(3)
    m1.metric("일주일 실천량", f"{count:,} {sim_data['unit']}")
    m2.metric("예시 온실가스 감축량", f"{estimated_kg:.3f} kg CO₂e")
    m3.metric("적용한 계산 계수", sim_data["factor_label"])

    chart_df = pd.DataFrame(
        {
            "구분": ["예시 감축량", "비교 기준(1 kg)"],
            "양(kg CO₂e)": [estimated_kg, 1.0],
        }
    )
    fig = px.bar(
        chart_df,
        x="구분",
        y="양(kg CO₂e)",
        color="구분",
        color_discrete_sequence=["#55a879", "#c6dfcf"],
        title="예시 감축량과 1 kg 비교",
        text_auto=".3f",
    )
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis_title="온실가스 배출량 환산값 (kg CO₂e)",
        xaxis_title="",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"**계산 방식:** {count} {sim_data['unit']} × {sim_data['factor']} kg CO₂e/{sim_data['unit']} = **{estimated_kg:.3f} kg CO₂e**")
    st.caption(f"가정: {sim_data['factor_label']}. 이 계수는 교육용 예시이며 공인된 제품별 측정값이 아닙니다.")
    with st.expander("계산 계수의 의미와 한계"):
        st.write(
            "탄소 환산량(CO₂e)은 여러 온실가스의 영향을 이산화탄소 기준으로 환산해 비교하는 단위입니다. "
            "이 앱의 계수는 복잡한 전 과정 평가를 대신하지 않습니다. 특히 텀블러·장바구니는 제조 부담과 반복 사용 횟수, "
            "전력은 실제 대기전력과 전력 배출계수, 이동은 차량 종류와 연비에 따라 값이 달라집니다. "
            "따라서 숫자의 절대적인 정확성보다 어떤 가정을 곱해 추정치를 얻는지 이해하는 데 목적이 있습니다."
        )

# -----------------------------
# 8. 과학 원리 퀴즈
# -----------------------------
elif page == "과학 원리 퀴즈":
    show_hero(
        "CHECK YOUR UNDERSTANDING",
        "과학 원리 퀴즈",
        "환경보호 행동 뒤에 숨은 과학적 원리를 이해했는지 확인해 보세요. 다섯 문제를 풀고 제출하면 해설을 확인할 수 있습니다.",
    )
    with st.form("science_quiz_form"):
        answers = []
        for i, item in enumerate(QUIZ):
            st.markdown(f"**문제 {i + 1}. {item['question']}**")
            answer = st.radio(
                "정답을 선택하세요.",
                item["options"],
                key=f"quiz_{i}",
                index=None,
                label_visibility="collapsed",
            )
            answers.append(answer)
            if i != len(QUIZ) - 1:
                st.divider()
        submitted = st.form_submit_button("정답 제출", type="primary", use_container_width=True)

    if submitted:
        if any(answer is None for answer in answers):
            st.warning("모든 문제에 답한 뒤 제출해 주세요.")
        else:
            score = 0
            for i, (answer, item) in enumerate(zip(answers, QUIZ)):
                is_correct = answer == item["options"][item["answer"]]
                if is_correct:
                    score += 1
                with st.expander(f"문제 {i + 1} {'✅ 정답' if is_correct else '🔎 다시 살펴보기'}", expanded=True):
                    st.write(f"**정답:** {item['options'][item['answer']]}")
                    st.write(item["explain"])
            st.metric("나의 점수", f"{score} / {len(QUIZ)}")
            if score == len(QUIZ):
                st.balloons()
                st.success("모든 문제를 맞혔어요! 행동과 과학 원리의 연결을 잘 이해했습니다.")
            elif score >= 3:
                st.success("잘했어요! 해설을 읽고 헷갈렸던 개념을 다시 확인해 보세요.")
            else:
                st.info("괜찮아요. 분석기에서 과학적 작용을 다시 살펴본 뒤 도전해 보세요.")

# -----------------------------
# 9. 푸터
# -----------------------------
st.divider()
st.caption(
    "🌱 환경 행동의 과학 | 교육 목적의 학습 자료입니다. "
    "환경 영향 수치는 명시된 가정에 따른 예시이며, 실제 감축 실적이나 공식 통계로 해석하면 안 됩니다."
)
