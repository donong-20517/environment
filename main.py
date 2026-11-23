import os
from datetime import datetime, timezone, timedelta
import streamlit as st

# ============================================================
# 환경 행동의 과학
# 대상: 고등학교 1~3학년
# 실행: streamlit run main.py
# ============================================================

st.set_page_config(
    page_title="환경 행동의 과학",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Supabase 연결 (선택적 외부 DB 영구 저장)
# .streamlit/secrets.toml 또는 환경변수에
# SUPABASE_URL, SUPABASE_KEY 설정 시 영구 저장 활성화
# -----------------------------
KST = timezone(timedelta(hours=9))


@st.cache_resource
def get_supabase_client():
    url = None
    key = None
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
    except Exception:
        pass
    url = url or os.environ.get("SUPABASE_URL")
    key = key or os.environ.get("SUPABASE_KEY")

    if not url or not key:
        return None
    try:
        from supabase import create_client
        return create_client(url, key)
    except Exception:
        return None


def load_board_posts():
    client = get_supabase_client()
    if client is not None:
        try:
            res = (
                client.table("eco_reflection_board")
                .select("*")
                .order("created_at", desc=True)
                .limit(100)
                .execute()
            )
            return res.data or [], True
        except Exception as e:
            st.warning(f"외부 데이터베이스 조회 중 오류가 발생해 임시 저장소를 표시합니다: {e}")
    return st.session_state.get("fallback_posts", []), False


def save_board_post(student_id: str, student_name: str, reflection: str):
    now_kst = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
    client = get_supabase_client()
    if client is not None:
        try:
            client.table("eco_reflection_board").insert(
                {
                    "student_id": student_id,
                    "student_name": student_name,
                    "reflection": reflection,
                }
            ).execute()
            return True, "서버 데이터베이스에 게시글이 영구 저장되었습니다."
        except Exception as e:
            return False, f"서버 저장에 실패했습니다. 테이블 설정을 확인해 주세요: {e}"

    posts = st.session_state.setdefault("fallback_posts", [])
    posts.insert(
        0,
        {
            "student_id": student_id,
            "student_name": student_name,
            "reflection": reflection,
            "created_at": now_kst,
        },
    )
    return True, "현재 세션에 게시글이 등록되었습니다. (영구 저장을 위해 Supabase 설정을 연결해 주세요.)"


# -----------------------------
# 디자인
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    .stApp { background: #f7faf8; }
    .main .block-container { max-width: 1250px; padding-top: 1.6rem; padding-bottom: 3rem; }
    .hero {
        background: linear-gradient(120deg, #e0f2e7 0%, #f0f8f2 100%);
        border: 1px solid #cfe5d5; border-radius: 22px;
        padding: 1.55rem 1.8rem; margin-bottom: 1.1rem;
    }
    .eyebrow { color: #28764b; font-size: .8rem; font-weight: 800; letter-spacing: .09em; }
    .hero h1 { color: #17452d; font-size: 2.05rem; margin: .35rem 0 .5rem 0; }
    .hero p { color: #405d4a; line-height: 1.8; margin: 0; font-size: 1rem; }
    .input-panel {
        background: white; border: 2px solid #a9d3b5; border-radius: 18px;
        padding: 1.1rem 1.25rem; margin: .8rem 0 1.3rem 0;
    }
    .input-title { color: #17452d; font-weight: 800; font-size: 1.15rem; margin-bottom: .25rem; }
    .input-sub { color: #607568; font-size: .88rem; margin-bottom: .6rem; }
    .info-card {
        background: white; border: 1px solid #dce9df; border-radius: 15px;
        padding: 1rem 1.1rem; margin-bottom: .75rem;
    }
    .info-card h3 { color: #17452d; font-size: 1.05rem; margin: 0 0 .45rem 0; }
    .info-card p { color: #42594a; line-height: 1.75; margin: 0; }
    .post-card {
        background: white; border: 1px solid #d5e6da; border-left: 5px solid #2e8555;
        border-radius: 14px; padding: 1rem 1.2rem; margin-bottom: .75rem;
    }
    .post-meta {
        color: #28764b; font-weight: 700; font-size: .92rem; margin-bottom: .4rem;
    }
    .post-body {
        color: #2c3e33; line-height: 1.7; font-size: .97rem; white-space: pre-wrap;
    }
    .tag {
        display: inline-block; background: #e8f4eb; color: #286b43;
        border-radius: 999px; padding: .2rem .65rem; font-size: .78rem; font-weight: 700;
        margin: 0 .25rem .35rem 0;
    }
    .small-note { color: #687b6e; font-size: .83rem; line-height: 1.65; }
    div[data-testid="stMetric"] {
        background: white; border: 1px solid #dce9df; padding: 13px; border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 재활용 품목 자료
# -----------------------------
ITEMS = {
    "무색 투명 페트병": {
        "category": "플라스틱 재활용",
        "keywords": ["투명 페트", "투명페트", "생수병", "페트병"],
        "disposal": "내용물을 비우고 라벨을 제거한 뒤 가능한 한 압착하여 뚜껑을 닫아 투명 페트병 전용 수거함에 배출합니다. 지역별 배출 방식이 다를 수 있습니다.",
        "science": "페트병 몸체는 주로 PET(폴리에틸렌 테레프탈레이트)라는 열가소성 폴리에스터입니다. PET는 에스터 결합을 포함하는 고분자이며, 선별·세척·분쇄를 거쳐 재생 원료로 만들 수 있습니다. 투명 페트병을 다른 플라스틱과 구분하면 고품질 재생 원료를 확보하는 데 유리합니다.",
        "environment": "새 원료로 PET를 생산해야 하는 수요를 일부 대체하고, 폐기물 매립·소각 부담을 낮추는 데 기여할 수 있습니다. 실제 재활용 여부와 품질은 오염 정도와 선별·재활용 시설에 좌우됩니다.",
        "personal": "분리배출 표시를 확인하고 재질별로 구분하는 습관을 기를 수 있습니다. 깨끗한 용기를 비우고 정리하는 과정에서 생활 공간의 위생 관리에도 도움이 됩니다.",
        "caution": "투명해 보인다고 모든 플라스틱 컵이나 용기가 투명 페트병인 것은 아닙니다. 일회용 컵·트레이 등은 재질이 다를 수 있으므로 일반 플라스틱 등 해당 지역 안내에 따릅니다.",
    },
    "색이 있는 페트병": {
        "category": "플라스틱 재활용",
        "keywords": ["색 페트", "갈색 페트", "초록 페트", "색이 있는 페트"],
        "disposal": "내용물을 비우고 가능한 한 이물질을 제거한 뒤, 투명 페트병 전용 수거함이 아닌 일반 플라스틱류 배출 기준을 확인합니다.",
        "science": "PET라는 고분자 재질은 투명 페트병과 같을 수 있지만, 색소나 첨가제가 들어가면 재생 원료의 색과 용도에 영향을 줄 수 있습니다. 재활용 공정에서는 재질뿐 아니라 색상과 오염 정도도 선별 요소가 됩니다.",
        "environment": "적절한 분리배출은 재생 플라스틱 원료의 품질을 높이고 새 플라스틱 생산에 필요한 원료 수요를 줄이는 데 도움이 됩니다.",
        "personal": "용기의 외관만이 아니라 분리배출 표시와 지역 안내를 확인하는 습관을 익힐 수 있습니다.",
        "caution": "색이 있는 PET를 투명 페트병 전용 수거함에 넣지 않도록 주의합니다. 세부 배출함은 거주 지역 안내를 확인합니다.",
    },
    "플라스틱 용기(PE·PP 등)": {
        "category": "플라스틱 재활용",
        "keywords": ["플라스틱", "샴푸통", "세제통", "플라스틱 용기", "요구르트병"],
        "disposal": "내용물을 비우고 가능한 범위에서 헹군 뒤, 다른 재질의 뚜껑·펌프·라벨 등은 분리 가능한 경우 분리해 배출합니다. 재질 표시와 지역 기준을 확인합니다.",
        "science": "PE(폴리에틸렌)와 PP(폴리프로필렌)는 탄소 원자가 연결된 고분자 사슬로 이루어진 열가소성 수지입니다. 플라스틱마다 밀도, 녹는점, 첨가제 등이 달라 재활용 공정에서 재질별 선별이 중요합니다.",
        "environment": "재질별로 잘 분리된 플라스틱은 세척·분쇄·재가공을 거쳐 재생 원료로 활용될 수 있어 석유계 원료 사용과 폐기물 발생을 줄이는 데 기여합니다.",
        "personal": "제품 뒷면의 재질 표시를 읽는 능력을 기를 수 있습니다. 내용물을 비우는 습관은 악취와 오염을 줄이는 데도 도움이 됩니다.",
        "caution": "복합재질 제품이나 음식물이 제거되지 않는 용기는 재활용이 어려울 수 있습니다. 펌프 등 여러 재질이 결합된 부분은 지역별 안내를 따릅니다.",
    },
    "플라스틱 트레이·배달 용기": {
        "category": "플라스틱 재활용",
        "keywords": ["배달 용기", "배달용기", "플라스틱 트레이", "반찬통"],
        "disposal": "음식물을 비우고 기름기와 이물질을 가능한 범위에서 제거한 뒤 재질 표시를 확인합니다. 깨끗하게 세척되지 않는 경우 재활용품으로 배출하지 못할 수 있습니다.",
        "science": "용기는 PET·PP·PS 등 서로 다른 고분자로 만들어질 수 있습니다. 고분자 종류가 다르면 가열·용융 조건과 물성이 달라 혼합 재활용 시 재생 원료의 품질이 낮아질 수 있습니다.",
        "environment": "음식물 오염을 줄이고 재질별로 배출하면 선별·세척 과정의 부담을 낮추고 재활용 가능한 원료의 회수율을 높이는 데 도움이 됩니다.",
        "personal": "배달 용기를 바로 버리기보다 내용물을 비우고 재질 표시를 확인하는 습관을 만들 수 있습니다. 다회용 용기 선택은 일회용 포장재 사용 자체를 줄이는 방법입니다.",
        "caution": "오염이 심해 세척해도 이물질이 제거되지 않는 용기, 복합재질 용기는 재활용이 어려울 수 있습니다.",
    },
    "비닐 포장재": {
        "category": "비닐·발포수지 재활용",
        "keywords": ["비닐", "과자 봉지", "비닐 포장", "비닐봉지"],
        "disposal": "내용물을 비우고 이물질을 제거합니다. 가능한 한 깨끗하고 마른 상태로 모아 비닐류 수거 기준에 맞게 배출합니다.",
        "science": "포장용 비닐은 PE나 PP 등 얇은 고분자 필름인 경우가 많습니다. 얇고 유연한 구조라 가볍지만, 여러 재질이 겹쳐진 복합 필름은 재질을 분리하기 어려워 재활용 공정에 제약이 생길 수 있습니다.",
        "environment": "재활용 가능한 필름을 올바르게 모으면 원료 회수에 도움이 됩니다. 다만 비닐 사용을 줄이고 재사용하는 것이 폐기물 발생 자체를 줄이는 방법이기도 합니다.",
        "personal": "포장재를 구분하고 오염 여부를 판단하는 생활 속 분류 능력을 높일 수 있습니다.",
        "caution": "음식물이나 기름이 묻어 제거되지 않는 비닐, 여러 재질이 붙은 포장재 등은 지자체 안내에 따라야 합니다.",
    },
    "스티로폼 완충재": {
        "category": "비닐·발포수지 재활용",
        "keywords": ["스티로폼", "발포", "완충재", "택배 완충"],
        "disposal": "테이프·송장·이물질을 제거하고 깨끗한 상태로 배출합니다. 음식물이나 오염이 심한 포장재는 지역 기준을 확인합니다.",
        "science": "흔히 스티로폼이라 부르는 발포 폴리스티렌(EPS)은 폴리스티렌 수지 안에 기체가 많이 포함된 구조입니다. 부피에 비해 질량이 작고 충격을 완화하지만, 부피가 커 수거·운송 효율이 낮을 수 있습니다.",
        "environment": "깨끗한 EPS를 회수하면 재생 플라스틱 원료로 활용할 수 있습니다. 부피를 줄이고 오염을 제거하면 운송과 선별의 부담을 낮추는 데 도움이 됩니다.",
        "personal": "택배 포장재를 정리하고 재질별로 배출하는 습관을 기를 수 있습니다. 포장재가 과도한 제품을 선택하지 않는 소비 습관도 생각해 볼 수 있습니다.",
        "caution": "음식물이 묻은 용기, 코팅·복합재질 제품 등은 재활용이 어려울 수 있습니다. 지역별 배출 기준을 확인합니다.",
    },
    "종이·신문·책자": {
        "category": "종이 재활용",
        "keywords": ["종이", "신문", "책", "책자", "노트"],
        "disposal": "종이 외 비닐 코팅, 스프링, 테이프 등 다른 재질을 제거하고 물기에 젖거나 음식물로 오염되지 않도록 묶어서 배출합니다.",
        "science": "종이의 주요 성분인 셀룰로오스는 포도당 단위가 길게 연결된 다당류입니다. 종이 섬유는 서로 얽히고 수소 결합을 형성해 종이의 강도를 유지합니다. 재활용할 때는 물에 풀어 섬유를 분리하고 잉크와 이물질을 제거합니다.",
        "environment": "폐지를 회수하면 새 펄프 생산에 필요한 목재와 물·에너지 수요를 줄이는 데 기여합니다. 다만 섬유는 재활용 과정에서 짧아지고 약해져 무한히 재활용할 수는 없습니다.",
        "personal": "이면지 사용과 양면 인쇄를 함께 실천하면 종이 구매량과 정리해야 할 폐기물을 줄일 수 있습니다.",
        "caution": "영수증, 코팅지, 기름·음식물에 오염된 종이, 화장지 등은 일반 종이류와 다르게 처리될 수 있습니다.",
    },
    "골판지 상자": {
        "category": "종이 재활용",
        "keywords": ["골판지", "택배 상자", "박스", "상자"],
        "disposal": "택배 송장과 테이프 등 다른 재질을 제거하고 펼쳐서 접은 뒤 배출합니다. 젖거나 기름에 오염된 부분은 제거하고 지역 기준을 확인합니다.",
        "science": "골판지는 종이 섬유를 여러 겹으로 구성하고 가운데 층을 물결 모양으로 만들어 강성과 완충성을 높인 구조입니다. 섬유를 물에 풀어 재생 펄프로 만들 수 있지만, 접착제·테이프·오염물은 공정을 방해할 수 있습니다.",
        "environment": "골판지를 회수하면 새 종이 원료와 제조 에너지 사용을 줄일 수 있습니다. 상자를 재사용하면 재활용 공정에 들어가기 전 제품 수명을 한 번 더 연장할 수 있습니다.",
        "personal": "상자를 재사용하거나 접어 보관하면 생활 공간을 효율적으로 관리하고 포장재 구매를 줄일 수 있습니다.",
        "caution": "택배 송장 개인정보는 배출 전에 가리거나 제거하고, 젖거나 오염된 종이는 재활용 가능 여부를 확인합니다.",
    },
    "종이팩·우유팩": {
        "category": "종이 재활용",
        "keywords": ["종이팩", "우유팩", "멸균팩", "두유팩"],
        "disposal": "내용물을 비우고 물로 헹군 뒤 펼쳐 말려 별도 수거함 또는 지자체가 정한 방법으로 배출합니다. 종이팩 전용 수거 체계가 있는지 확인합니다.",
        "science": "종이팩은 종이 섬유층에 폴리에틸렌 등의 얇은 플라스틱 막이 붙어 있고, 멸균팩은 알루미늄층이 더해지기도 합니다. 여러 재료가 층을 이루므로 일반 종이와 분리해 처리하는 것이 중요합니다.",
        "environment": "종이팩을 별도로 모으면 내부 종이 섬유를 회수해 재생 종이 원료로 활용할 수 있습니다. 일반 폐지와 섞여 회수되지 못하는 것을 줄이는 데 도움이 됩니다.",
        "personal": "우유나 음료를 마신 뒤 팩을 헹구고 말리는 작은 습관으로 분리배출의 정확성을 높일 수 있습니다.",
        "caution": "종이팩은 일반 종이류와 수거 체계가 다를 수 있습니다. 종이팩 전용 수거함이나 주민센터 수거 여부를 확인합니다.",
    },
    "유리병": {
        "category": "유리·금속 재활용",
        "keywords": ["유리병", "유리 용기", "잼 병", "음료 유리"],
        "disposal": "내용물을 비우고 가능한 범위에서 헹군 뒤 뚜껑 등 다른 재질을 분리합니다. 깨진 유리와 판유리 등은 일반 유리병 수거와 다르게 처리해야 합니다.",
        "science": "일반 유리병은 주로 규산염을 기본으로 하는 유리 재료입니다. 유리는 높은 온도에서 녹여 다시 성형할 수 있으며, 색상별로 구분하면 재생 유리의 색과 품질을 관리하기 쉽습니다.",
        "environment": "폐유리를 원료로 다시 사용하면 새 유리 원료의 투입과 제조 에너지 사용을 줄이는 데 도움이 됩니다. 유리는 재활용 과정에서 재료 자체의 성질이 비교적 잘 유지될 수 있습니다.",
        "personal": "유리병을 재사용하거나 올바르게 배출하면 용기 사용과 폐기 과정을 더 신중하게 관리할 수 있습니다.",
        "caution": "깨진 유리, 도자기, 내열 유리, 거울, 전구 등은 일반 유리병과 성분·처리 방식이 달라 별도 안내를 확인해야 합니다.",
    },
    "철·알루미늄 캔": {
        "category": "유리·금속 재활용",
        "keywords": ["캔", "알루미늄", "철캔", "통조림", "음료 캔"],
        "disposal": "내용물을 비우고 헹군 뒤 가능한 한 부피를 줄여 배출합니다. 재질이 다른 뚜껑이나 부착물은 지역 기준에 맞게 분리합니다.",
        "science": "금속은 원자들이 금속 결합을 이루는 재료입니다. 철과 알루미늄은 자석 반응, 밀도 등 물리적 성질이 달라 선별할 수 있습니다. 금속은 녹여 주조하는 방식으로 재활용할 수 있으며, 알루미늄은 원광석에서 새로 생산하는 과정에 많은 전력이 필요합니다.",
        "environment": "금속 회수는 광석 채굴과 제련에 필요한 원료·에너지 수요를 줄이는 데 기여합니다. 특히 알루미늄 재활용은 원광석에서 알루미늄을 추출하는 것보다 에너지 사용을 크게 줄일 수 있습니다.",
        "personal": "캔의 내용물을 비우고 압착하는 과정에서 자원 가치가 있는 금속을 분리해 배출하는 습관을 익힐 수 있습니다.",
        "caution": "부탄가스 등 압력 용기는 일반 캔과 다릅니다. 안전을 위해 지자체의 별도 배출 지침을 따릅니다.",
    },
    "폐건전지·배터리": {
        "category": "전자·특수 품목 재활용",
        "keywords": ["건전지", "배터리", "전지"],
        "disposal": "일반 쓰레기와 섞지 말고 공동주택·주민센터 등에 설치된 전용 수거함 등 지정된 장소에 배출합니다. 제품 종류별 안내를 확인합니다.",
        "science": "전지는 산화·환원 반응을 이용해 화학에너지를 전기에너지로 바꿉니다. 사용 후에도 전지에는 여러 금속과 전해질 성분이 남을 수 있어 적절한 회수·처리가 필요합니다.",
        "environment": "전용 수거 체계로 모으면 재활용 가능한 금속 자원을 회수하고, 부적절한 폐기로 인한 환경 오염 위험을 줄이는 데 도움이 됩니다.",
        "personal": "가정에서 작은 전지를 따로 모아 지정된 장소에 가져가는 습관은 생활 폐기물 관리와 안전 의식을 높입니다.",
        "caution": "전지는 종류별 처리 방식이 다를 수 있습니다. 훼손하거나 임의로 분해하지 말고 지정 수거함과 공식 안내를 이용합니다.",
    },
    "폐가전제품": {
        "category": "전자·특수 품목 재활용",
        "keywords": ["폐가전", "전자제품", "컴퓨터", "휴대폰", "가전"],
        "disposal": "소형·대형 폐가전의 무상 방문 수거 또는 지자체 수거 체계 등 공식 수거 방법을 확인합니다. 임의로 분해하지 않습니다.",
        "science": "전자제품에는 철·알루미늄·구리 같은 금속, 유리, 여러 종류의 플라스틱과 전자부품이 함께 들어 있습니다. 재질이 복합적으로 결합되어 있어 전문 시설에서 해체·선별해야 자원을 회수할 수 있습니다.",
        "environment": "전문 회수·재활용은 금속과 플라스틱 등의 자원을 다시 이용하고, 부적절한 폐기로 인한 유해 물질 누출 위험을 낮추는 데 도움이 됩니다.",
        "personal": "제품을 버리기 전 수리·재사용·공식 수거를 먼저 검토하면 구매 비용과 폐기 부담을 줄일 수 있습니다.",
        "caution": "배터리 내장 제품은 배터리 처리 기준을 확인하고, 개인정보가 저장된 기기는 배출 전에 개인정보 보호 조치를 해야 합니다.",
    },
    "폐식용유": {
        "category": "전자·특수 품목 재활용",
        "keywords": ["폐식용유", "식용유"],
        "disposal": "음식물 찌꺼기 등 이물질이 섞이지 않도록 모아 지자체 또는 민간 재활용 사업자가 마련한 전용 수거함에 배출합니다. 지역 수거 여부를 확인합니다.",
        "science": "식용유의 주성분은 지방산과 글리세롤이 결합한 트라이글리세라이드입니다. 회수된 폐식용유는 정제 과정을 거쳐 비누 원료나 바이오연료 원료 등으로 활용될 수 있습니다.",
        "environment": "폐식용유를 적절히 회수하면 하수관과 수계로 유입되는 기름 오염을 줄이고, 재활용 원료로 다시 이용할 가능성을 높입니다.",
        "personal": "기름을 싱크대에 흘려보내지 않고 식힌 뒤 모아 배출하는 습관은 배수관 관리와 생활 환경 보호에 도움이 됩니다.",
        "caution": "뜨거운 기름을 바로 옮기지 말고 충분히 식혀야 합니다. 수거함이 없는 지역은 지자체 안내를 확인합니다.",
    },
}

# -----------------------------
# 일상 에너지·자원 절약 활동
# -----------------------------
PRACTICES = {
    "사용하지 않는 전자제품의 대기전력 줄이기": {
        "category": "에너지 절약",
        "keywords": ["대기전력", "플러그", "콘센트", "전원 끄기", "전기 끄기", "멀티탭"],
        "science": "일부 전자제품은 주 기능을 사용하지 않는 대기 상태에서도 시계·센서·네트워크 수신 등을 위해 전력을 소비합니다. 전력량은 소비전력(W)에 시간(h)을 곱해 계산하며, 1,000Wh는 1kWh입니다. 전력 수요가 줄면 전력 생산에 필요한 에너지도 줄어들 수 있습니다.",
        "environment": "전력 생산에 화석연료 발전이 포함된 경우 전력 사용량 감소는 연료 연소와 이산화탄소 등 온실가스 배출을 줄이는 데 기여할 수 있습니다.",
        "personal": "전기요금 절약에 도움이 될 수 있고, 사용하지 않는 기기의 전원을 확인하는 생활 습관을 기를 수 있습니다. 단, 냉장고나 네트워크 장비처럼 계속 작동해야 하는 제품은 임의로 끄지 않습니다.",
        "tip": "제품 설명서와 안전을 먼저 확인하고, 장기간 사용하지 않는 기기나 대기전력이 큰 기기부터 점검합니다.",
    },
    "냉난방 온도와 사용 시간 조절하기": {
        "category": "에너지 절약",
        "keywords": ["에어컨", "난방", "냉방", "보일러", "온도", "히터"],
        "science": "실내외 온도 차이가 클수록 건물 안팎으로 열이 이동하는 경향이 커집니다. 냉난방기는 열을 이동시키거나 연료·전기를 사용해 실내 온도를 조절하므로 설정 온도와 가동 시간이 에너지 소비에 영향을 줍니다.",
        "environment": "냉난방 에너지 사용을 줄이면 발전·연료 공급 과정의 온실가스 배출을 줄이는 데 기여할 수 있습니다.",
        "personal": "적절한 실내 온도와 환기를 유지하면 쾌적한 학습·생활 환경을 만드는 데 도움이 됩니다. 지나친 냉난방을 피하면 에너지 비용도 줄일 수 있습니다.",
        "tip": "실내외 온도 차이를 과도하게 벌리지 않고, 사용하지 않는 공간의 냉난방을 줄입니다.",
    },
    "샤워 시간 줄이고 물 절약하기": {
        "category": "자원 절약·재사용",
        "keywords": ["샤워", "물 절약", "수도", "양치", "물 틀어놓"],
        "science": "물을 공급하고 정수·가압·하수 처리하는 과정에는 전기에너지가 사용됩니다. 온수를 만들 때는 물을 가열하는 열에너지도 필요하므로 온수 사용량은 에너지 소비와 연결됩니다.",
        "environment": "물 사용량을 줄이면 취수·정수·송수·하수 처리에 필요한 에너지와 자원 부담을 낮추는 데 도움이 됩니다.",
        "personal": "수도·온수 사용량을 줄여 생활비를 절약할 수 있고, 물을 필요한 만큼 사용하는 습관을 기를 수 있습니다.",
        "tip": "양치 중 물 잠그기, 샤워 시간 점검, 세탁물 모아서 세탁하기처럼 일상에서 지속 가능한 방법을 선택합니다.",
    },
    "잔반과 음식물 쓰레기 줄이기": {
        "category": "자원 절약·재사용",
        "keywords": ["잔반", "음식물", "음식 남기", "먹을 만큼"],
        "science": "식품 생산에는 토지·물·비료·에너지·운송이 필요합니다. 음식물 쓰레기가 산소가 부족한 환경에서 미생물에 의해 분해되면 메탄이 생성될 수 있습니다. 처리 시설에서는 퇴비화·사료화·혐기성 소화 등 다양한 방식이 쓰이며 방식별 환경 영향이 다릅니다.",
        "environment": "먹을 만큼 준비하고 잔반을 줄이면 식품 생산에 투입된 자원의 낭비와 음식물 폐기물 처리 부담을 줄일 수 있습니다.",
        "personal": "필요한 양을 판단하고 식사량을 조절하는 습관을 기를 수 있습니다. 음식물 쓰레기와 처리 비용을 줄이는 데도 도움이 됩니다.",
        "tip": "처음부터 적당량을 담고, 더 먹고 싶을 때 추가로 받는 방식을 활용합니다.",
    },
    "텀블러·다회용 컵 사용하기": {
        "category": "다회용품 사용",
        "keywords": ["텀블러", "다회용 컵", "개인 컵", "일회용 컵"],
        "science": "텀블러도 원료 채취와 제조 과정에서 자원·에너지를 사용합니다. 제품 전 과정 평가에서는 제조·운송·사용·세척·폐기까지 고려합니다. 반복 사용으로 일회용 컵을 실제 대체해야 제조 과정의 환경 부담을 상쇄할 수 있습니다.",
        "environment": "오래 반복해서 사용하면 일회용 컵의 생산과 폐기 수요를 줄이는 데 기여할 수 있습니다. 사용 횟수와 세척 방식에 따라 효과가 달라집니다.",
        "personal": "음료 구매 시 일회용 컵 사용을 줄이고, 개인 물병을 챙기는 습관을 만들 수 있습니다. 장기적으로 일회용품 구매 비용을 줄일 수도 있습니다.",
        "tip": "새 텀블러를 계속 사기보다 이미 가진 컵을 오래 사용하고, 물·세제를 과도하게 쓰지 않는 방식으로 세척합니다.",
    },
    "장바구니와 다회용 가방 사용하기": {
        "category": "다회용품 사용",
        "keywords": ["장바구니", "에코백", "비닐봉지", "다회용 가방"],
        "science": "비닐봉지는 PE 같은 고분자로 만들어지는 경우가 많습니다. 장바구니는 제조할 때 더 많은 재료가 필요할 수도 있으므로, 몇 번 사용했는지와 어떤 일회용 봉투를 대체했는지를 포함한 전 과정 관점에서 비교해야 합니다.",
        "environment": "가지고 있는 장바구니를 여러 번 사용하면 새 비닐봉지의 생산과 폐기 수요를 줄일 수 있습니다.",
        "personal": "장바구니를 미리 가방에 넣어 두면 일회용 봉투를 구매하는 비용을 줄이고 반복 가능한 소비 습관을 형성할 수 있습니다.",
        "tip": "새 장바구니를 계속 구매하기보다 기존 가방을 오래 사용합니다.",
    },
    "가까운 거리는 걷거나 자전거 이용하기": {
        "category": "친환경 이동",
        "keywords": ["걷기", "도보", "자전거", "자동차 대신", "차 대신"],
        "science": "내연기관 자동차는 연료 속 탄화수소를 산소와 반응시켜 에너지를 얻습니다. 완전연소에서는 주로 이산화탄소와 물이 생성되며, 연료에 포함된 탄소가 이산화탄소로 대기 중에 배출됩니다.",
        "environment": "자동차 이동을 걷기나 자전거로 실제 대체하면 연료 소비와 배기관 온실가스·대기오염물질 배출을 줄이는 데 기여할 수 있습니다.",
        "personal": "무리하지 않는 범위의 걷기와 자전거 이용은 일상적인 신체 활동을 늘리는 데 도움이 될 수 있습니다. 이동 시간과 안전한 경로를 고려해야 합니다.",
        "tip": "안전한 보행로와 자전거 도로가 있는 짧은 이동부터 선택합니다.",
    },
    "종이 양면 인쇄·이면지 사용하기": {
        "category": "자원 절약·재사용",
        "keywords": ["양면 인쇄", "이면지", "종이 아끼", "종이 절약"],
        "science": "종이의 주성분인 셀룰로오스는 포도당 단위가 연결된 다당류입니다. 종이 섬유를 만들고 건조하는 과정에는 물과 에너지가 필요하므로, 종이 사용량 자체를 줄이면 원료와 제조 공정의 부담도 줄어듭니다.",
        "environment": "같은 정보를 더 적은 종이로 표현하면 펄프 생산에 필요한 목재와 물·에너지 사용을 줄이는 데 도움이 됩니다.",
        "personal": "인쇄 용지 구매와 보관 공간을 줄이고, 자료를 필요한 만큼만 출력하는 습관을 기를 수 있습니다.",
        "tip": "문서의 양면 인쇄를 기본으로 설정하고, 한쪽 면만 사용한 종이는 메모나 연습용으로 다시 활용합니다.",
    },
}

# 계층형 활동 탐색 구조 정의 (대분류 -> 소분류 -> 세부 항목)
ACTIVITY_TREE = {
    "♻️ 재활용": {
        "desc": "재질별 특성을 이해하고 올바르게 분리배출하는 활동입니다.",
        "subcategories": {
            "📄 종이 재활용": {
                "kind": "item",
                "entries": ["종이·신문·책자", "골판지 상자", "종이팩·우유팩"],
            },
            "🧴 플라스틱 재활용": {
                "kind": "item",
                "entries": [
                    "무색 투명 페트병",
                    "색이 있는 페트병",
                    "플라스틱 용기(PE·PP 등)",
                    "플라스틱 트레이·배달 용기",
                ],
            },
            "🛍️ 비닐·발포수지 재활용": {
                "kind": "item",
                "entries": ["비닐 포장재", "스티로폼 완충재"],
            },
            "🥫 유리·금속 재활용": {
                "kind": "item",
                "entries": ["유리병", "철·알루미늄 캔"],
            },
            "🔋 전자·특수 품목 재활용": {
                "kind": "item",
                "entries": ["폐건전지·배터리", "폐가전제품", "폐식용유"],
            },
        },
    },
    "⚡ 에너지 절약": {
        "desc": "전기와 열에너지 소비를 줄여 발전 과정의 온실가스를 줄이는 활동입니다.",
        "subcategories": {
            "🔌 전기·대기전력 절약": {
                "kind": "practice",
                "entries": ["사용하지 않는 전자제품의 대기전력 줄이기"],
            },
            "🌡️ 냉난방 에너지 절약": {
                "kind": "practice",
                "entries": ["냉난방 온도와 사용 시간 조절하기"],
            },
        },
    },
    "💧 자원 절약·재사용": {
        "desc": "물, 식량, 종이, 일회용품 사용 자체를 줄여 생산과 폐기 부담을 낮추는 활동입니다.",
        "subcategories": {
            "🚰 물·식량·종이 절약": {
                "kind": "practice",
                "entries": [
                    "샤워 시간 줄이고 물 절약하기",
                    "잔반과 음식물 쓰레기 줄이기",
                    "종이 양면 인쇄·이면지 사용하기",
                ],
            },
            "🥤 다회용품 사용": {
                "kind": "practice",
                "entries": [
                    "텀블러·다회용 컵 사용하기",
                    "장바구니와 다회용 가방 사용하기",
                ],
            },
        },
    },
    "🚲 친환경 이동": {
        "desc": "화석연료 기반 이동을 줄이고 탄소 배출이 적은 교통수단을 선택하는 활동입니다.",
        "subcategories": {
            "🚶 도보·자전거 이용": {
                "kind": "practice",
                "entries": ["가까운 거리는 걷거나 자전거 이용하기"],
            },
        },
    },
}

# 입력 문장을 어떤 활동으로 해석할지 연결하는 규칙
KEYWORD_MAP = []
for item_name, item in ITEMS.items():
    for keyword in item["keywords"]:
        KEYWORD_MAP.append((keyword, "item", item_name))
for practice_name, practice in PRACTICES.items():
    for keyword in practice["keywords"]:
        KEYWORD_MAP.append((keyword, "practice", practice_name))
KEYWORD_MAP.sort(key=lambda x: len(x[0]), reverse=True)


# -----------------------------
# 공통 출력 함수
# -----------------------------
def show_hero(kicker, title, description):
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


def show_explanation(title, data, item_mode=False):
    st.markdown(
        f"""
        <div class="info-card">
            <span class="tag">{data['category']}</span>
            <h3>{title}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if item_mode:
        st.markdown("**올바른 배출 방법**")
        st.write(data["disposal"])
        st.markdown("**물리·화학적 원리**")
        st.write(data["science"])
        st.markdown("**환경에 미치는 영향**")
        st.write(data["environment"])
        st.markdown("**나에게 미치는 영향**")
        st.write(data["personal"])
        st.warning(f"배출 시 주의할 점: {data['caution']}")
    else:
        st.markdown("**물리·화학적 원리**")
        st.write(data["science"])
        st.markdown("**환경에 미치는 영향**")
        st.write(data["environment"])
        st.markdown("**나에게 미치는 영향**")
        st.write(data["personal"])
        st.info(f"실천 팁: {data['tip']}")


def analyze_user_action(user_text):
    text = user_text.strip().lower()
    for keyword, kind, name in KEYWORD_MAP:
        if keyword.lower() in text:
            if kind == "item":
                return ("item", name, ITEMS[name])
            return ("practice", name, PRACTICES[name])
    return None


# -----------------------------
# 사이드바: 고등학생 학습 설정
# -----------------------------
with st.sidebar:
    st.markdown("## 🌿 환경 행동의 과학")
    st.caption("일상 속 환경보호 활동을 과학으로 분석합니다.")
    page = st.radio(
        "탐색 메뉴",
        ["환경 활동 탐색", "실천 소감 게시판", "자료 출처와 안내"],
        label_visibility="visible",
    )
    st.divider()
    st.markdown("### 학습 대상")
    grade = st.selectbox("학년", ["고등학교 1학년", "고등학교 2학년", "고등학교 3학년"])
    st.caption("고등학교 통합과학·화학·물리·생명과학에서 다루는 개념과 연결해 설명합니다.")
    st.divider()
    st.markdown(
        "<div class='small-note'>배출 방법은 지자체와 수거 시설에 따라 달라질 수 있습니다. 실제 배출 전에는 거주 지역의 최신 안내를 확인하세요.</div>",
        unsafe_allow_html=True,
    )

# -----------------------------
# 상단 공통 영역
# -----------------------------
show_hero(
    "SCIENCE BEHIND EVERYDAY ACTIONS",
    "환경 행동의 과학",
    "재활용과 에너지·자원 절약은 어떤 과학적 원리로 환경을 보호할까요? 종류별 버튼을 눌러 세부 내용을 탐색하거나, 내가 실천한 활동을 직접 입력해 원리와 영향을 확인해 보세요.",
)

# =============================================================
# 페이지 1: 환경 활동 탐색 (계층형 버튼 탐색 + 직접 입력 분석 분리)
# =============================================================
if page == "환경 활동 탐색":
    # 1. 종류별 버튼 탐색 영역
    st.subheader("1. 종류별 환경보호 활동 탐색하기")
    st.caption("아래에서 원하는 활동 종류 버튼을 누르면 세부 분류와 과학적 설명이 차례대로 열립니다.")

    if "selected_main_cat" not in st.session_state:
        st.session_state["selected_main_cat"] = "♻️ 재활용"
    if "selected_sub_cat" not in st.session_state:
        st.session_state["selected_sub_cat"] = "📄 종이 재활용"
    if "selected_entry" not in st.session_state:
        st.session_state["selected_entry"] = "종이·신문·책자"

    # 1단계: 대분류 버튼 가로 배치
    main_cats = list(ACTIVITY_TREE.keys())
    main_cols = st.columns(len(main_cats))
    for idx, m_cat in enumerate(main_cats):
        is_selected = st.session_state["selected_main_cat"] == m_cat
        with main_cols[idx]:
            if st.button(
                m_cat,
                key=f"main_btn_{idx}",
                type="primary" if is_selected else "secondary",
                use_container_width=True,
            ):
                st.session_state["selected_main_cat"] = m_cat
                first_sub = list(ACTIVITY_TREE[m_cat]["subcategories"].keys())[0]
                st.session_state["selected_sub_cat"] = first_sub
                st.session_state["selected_entry"] = ACTIVITY_TREE[m_cat]["subcategories"][first_sub]["entries"][0]
                st.rerun()

    current_main = st.session_state["selected_main_cat"]
    main_info = ACTIVITY_TREE[current_main]
    st.info(f"**{current_main}**: {main_info['desc']}")

    # 2단계: 선택된 대분류 아래 세부 분야 버튼 열기
    subcats = list(main_info["subcategories"].keys())
    st.markdown(f"**세부 분야 선택 ({current_main})**")
    sub_cols = st.columns(len(subcats))
    for idx, s_cat in enumerate(subcats):
        is_sub_selected = st.session_state["selected_sub_cat"] == s_cat
        with sub_cols[idx]:
            if st.button(
                s_cat,
                key=f"sub_btn_{current_main}_{idx}",
                type="primary" if is_sub_selected else "secondary",
                use_container_width=True,
            ):
                st.session_state["selected_sub_cat"] = s_cat
                st.session_state["selected_entry"] = main_info["subcategories"][s_cat]["entries"][0]
                st.rerun()

    current_sub = st.session_state["selected_sub_cat"]
    if current_sub not in main_info["subcategories"]:
        current_sub = subcats[0]
        st.session_state["selected_sub_cat"] = current_sub

    sub_info = main_info["subcategories"][current_sub]
    entries = sub_info["entries"]

    # 3단계: 세부 항목 버튼 열기
    st.markdown(f"**상세 항목 선택 ({current_sub})**")
    entry_cols = st.columns(min(len(entries), 4))
    for idx, entry_name in enumerate(entries):
        is_entry_selected = st.session_state["selected_entry"] == entry_name
        with entry_cols[idx % len(entry_cols)]:
            if st.button(
                entry_name,
                key=f"entry_btn_{current_sub}_{idx}",
                type="primary" if is_entry_selected else "secondary",
                use_container_width=True,
            ):
                st.session_state["selected_entry"] = entry_name
                st.rerun()

    current_entry = st.session_state["selected_entry"]
    if current_entry not in entries:
        current_entry = entries[0]
        st.session_state["selected_entry"] = current_entry

    st.markdown("---")
    if sub_info["kind"] == "item":
        show_explanation(current_entry, ITEMS[current_entry], item_mode=True)
    else:
        show_explanation(current_entry, PRACTICES[current_entry], item_mode=False)

    st.divider()

    # 2. 별도 섹션: 자신이 실천한 환경 보호 활동 직접 입력
    st.subheader("2. 내가 실천한 환경 보호 활동 직접 분석하기")
    st.markdown(
        """
        <div class="input-panel">
          <div class="input-title">✍️ 자신이 실천한 환경 보호 활동 입력</div>
          <div class="input-sub">예: 투명 페트병의 라벨을 떼어 분리배출했다 / 사용하지 않는 멀티탭 전원을 껐다 / 종이를 양면으로 인쇄했다</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("my_action_form", clear_on_submit=False):
        user_action = st.text_input(
            "실천한 활동을 입력하세요.",
            placeholder="예: 우유팩을 씻어 말린 뒤 종이팩 수거함에 배출했다.",
            label_visibility="collapsed",
        )
        action_submitted = st.form_submit_button(
            "내 활동의 과학적 영향 알아보기", type="primary", use_container_width=True
        )

    if action_submitted:
        if not user_action.strip():
            st.warning("실천한 환경 보호 활동을 한 문장으로 입력해 주세요.")
            st.session_state["my_action_result"] = None
        else:
            st.session_state["my_action_text"] = user_action.strip()
            st.session_state["my_action_result"] = analyze_user_action(user_action)

    if st.session_state.get("my_action_result") is not None:
        result = st.session_state["my_action_result"]
        st.markdown("#### 내가 입력한 활동 분석 결과")
        st.caption(f"입력한 내용: {st.session_state.get('my_action_text', '')}")
        if result:
            kind, name, data = result
            st.success(f"입력한 활동을 **{name}**과 관련된 실천으로 분류했어요.")
            show_explanation("이 활동에 담긴 과학적 원리와 영향", data, item_mode=(kind == "item"))
        else:
            st.info(
                "입력한 문장에서 관련 품목이나 활동을 정확히 찾지 못했어요. "
                "위쪽의 종류별 버튼을 눌러 가장 가까운 항목을 확인하거나, "
                "'페트병', '종이팩', '대기전력', '잔반', '텀블러'처럼 구체적인 단어를 넣어 다시 입력해 보세요."
            )

# =============================================================
# 페이지 2: 실천 소감 게시판 (학번 + 이름 + 소감 -> DB 영구 저장 및 공개 열람)
# =============================================================
elif page == "실천 소감 게시판":
    st.subheader("📝 환경보호 활동 실천 소감 게시판")
    st.write("실천한 환경보호 활동과 느낀 점을 기록해 다른 학생들과 공유해 보세요.")

    with st.form("reflection_board_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            student_id = st.text_input("학번", placeholder="예: 10315")
        with col2:
            student_name = st.text_input("이름", placeholder="예: 김환경")
        reflection_text = st.text_area(
            "환경보호 활동 소감",
            placeholder="실천한 환경보호 활동 내용과 과학적 원리를 배우며 느낀 점을 자유롭게 적어 주세요.",
            height=130,
        )
        submitted = st.form_submit_button("게시하기", type="primary", use_container_width=True)

    if submitted:
        if not student_id.strip() or not student_name.strip() or not reflection_text.strip():
            st.warning("학번, 이름, 환경보호 활동 소감을 모두 입력해 주세요.")
        else:
            ok, msg = save_board_post(
                student_id.strip(),
                student_name.strip(),
                reflection_text.strip(),
            )
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    st.divider()
    st.markdown("### 전체 게시글 목록")
    posts, is_persistent = load_board_posts()

    if not is_persistent:
        st.caption(
            "※ 외부 데이터베이스(Supabase) 환경변수가 아직 연결되지 않아 현재 접속 세션 기준으로 표시됩니다. "
            "배포 환경의 Secrets에 SUPABASE_URL과 SUPABASE_KEY를 등록하면 모든 이용자의 글이 영구 저장됩니다."
        )

    if not posts:
        st.info("아직 등록된 소감이 없습니다. 첫 번째 환경보호 실천 소감을 남겨 보세요!")
    else:
        st.caption(f"총 {len(posts)}개의 소감이 등록되어 있습니다.")
        for post in posts:
            sid = post.get("student_id", "")
            sname = post.get("student_name", "")
            body = post.get("reflection", "")
            created = str(post.get("created_at", ""))[:16].replace("T", " ")
            st.markdown(
                f"""
                <div class="post-card">
                    <div class="post-meta">🎓 {sid} {sname} &nbsp;|&nbsp; <span style="font-weight:400; color:#687b6e;">{created}</span></div>
                    <div class="post-body">{body}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# =============================================================
# 페이지 3: 자료 출처와 안내
# =============================================================
elif page == "자료 출처와 안내":
    st.subheader("자료 출처")
    st.write("품목별 분리배출 방법과 에너지 절약 원리는 정부·공공기관 자료를 바탕으로 정리했습니다.")
    st.markdown(
        """
        - **기후에너지환경부, 생활폐기물 분리배출 누리집 안내(2025.09.05)**  
          생활폐기물 730개 품목의 분리배출 방법과 지역별 배출 장소·방법을 안내하는 누리집 개설 자료입니다.  
          [자료 확인](https://niwdc.me.go.kr/home/web/newsRead.do?boardId=1762990&boardMasterId=939)
        - **기후에너지환경부, 종이류 재활용품 분리배출 안내**  
          골판지 상자, 신문·책자류의 이물질과 다른 재질 제거 등 종이류 배출 요령을 안내합니다.  
          [자료 확인](https://me.go.kr/home/web/board/read.do?boardId=1310850&boardMasterId=54)
        - **기후에너지환경부, 재질중심 분리배출표시 개선 안내**  
          플라스틱·비닐·캔 등의 재질 표시와 함께 깨끗이 씻기, 라벨 제거 등 배출 방법을 확인하는 데 참고했습니다.  
          [자료 확인](https://www.me.go.kr/home/web/board/read.do?boardId=1396730&boardMasterId=1)
        - **한국에너지공단, 대기전력저감 프로그램**  
          전자제품이 실제로 사용되지 않는 대기 상태에서도 소비하는 전력인 대기전력과 저감 제도를 설명합니다.  
          [자료 확인](https://www.energy.or.kr/front/conts/105002004005000.do)
        - **한국에너지공단, 효율관리제도**  
          대기전력저감 프로그램과 제품별 대기전력 정보 확인에 참고할 수 있습니다.  
          [자료 확인](https://eep.energy.or.kr/electricity/elec_intro.aspx)
        """
    )
    st.divider()
    st.subheader("이 앱의 설명을 읽을 때 주의할 점")
    st.markdown(
        """
        1. **재활용 가능 여부와 실제 재활용은 다릅니다.** 재질이 재활용 가능한 물질이어도 오염, 복합재질, 수거·선별 시설의 차이로 재활용되지 못할 수 있습니다.
        2. **지역별 배출 기준을 확인해야 합니다.** 같은 품목도 지자체와 수거 체계에 따라 배출 방식이 다를 수 있습니다.
        3. **환경 영향은 조건에 따라 달라집니다.** 제품의 재질과 제조 과정, 운송 거리, 사용 횟수, 폐기 방식 등을 함께 고려해야 합니다.
        4. **개인에게 미치는 영향은 일반적인 가능성을 설명한 것입니다.** 실제 비용·건강·생활 습관의 변화는 개인의 상황에 따라 다릅니다.
        """
    )
    st.markdown(
        "[생활폐기물 분리배출 누리집에서 품목별 최신 기준 확인](https://분리배출.kr)",
    )

# -----------------------------
# 푸터
# -----------------------------
st.divider()
st.caption(
    f"🌿 환경 행동의 과학 | 학습 대상: {grade} | 고등학생을 위한 환경·물리·화학 융합 학습 자료. "
    "배출 방법은 지역별로 다를 수 있으므로 실제 배출 전 공식 안내를 확인하세요."
)
