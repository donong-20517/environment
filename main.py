import os
import re
from datetime import datetime, timezone, timedelta
import streamlit as st

# ============================================================
# ECO-SCIENCE LAB: 일상 행동의 과학적 메커니즘 분석 플랫폼
# 대상: 고등학교 1~3학년 (통합과학 · 화학 · 물리학 · 생명과학 · 지구과학)
# 실행: streamlit run main.py
# ============================================================

st.set_page_config(
    page_title="ECO-SCIENCE LAB | 환경 메커니즘 아카이브",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Supabase 외부 DB 연결 (영구 저장용)
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
                .limit(150)
                .execute()
            )
            return res.data or [], True
        except Exception as e:
            st.warning(f"외부 데이터베이스 조회 오류로 임시 세션 데이터를 표시합니다: {e}")
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
            return True, "데이터베이스에 기록이 영구 저장되었습니다."
        except Exception as e:
            return False, f"데이터베이스 저장 실패 (테이블/권한 확인 필요): {e}"

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
    return True, "현재 세션에 게시글이 등록되었습니다. (영구 공유를 위해 Supabase Secrets를 연결하세요.)"


# -----------------------------
# 모던 에디토리얼 & 다크 슬레이트-에메랄드 UI 스타일
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .stApp {
        background-color: #f4f6f8;
        color: #111827;
    }
    .main .block-container {
        max-width: 1180px;
        padding-top: 1.8rem;
        padding-bottom: 4rem;
    }

    /* 상단 배너 (모던 아카데믹 대시보드 스타일) */
    .lab-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 55%, #064e3b 100%);
        border-radius: 20px;
        padding: 2.1rem 2.4rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 12px 28px -10px rgba(15, 23, 42, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .lab-kicker {
        font-family: 'JetBrains Mono', monospace;
        color: #34d399;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .lab-title {
        color: #f8fafc;
        font-size: 2.15rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin: 0 0 0.55rem 0;
        line-height: 1.25;
    }
    .lab-subtitle {
        color: #cbd5e1;
        font-size: 0.98rem;
        line-height: 1.65;
        margin: 0;
        max-width: 820px;
    }

    /* 섹션 카드 & 분석 리포트 카드 */
    .report-header-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #059669;
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin: 0.8rem 0 1rem 0;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
    }
    .badge-pill {
        display: inline-block;
        background: #ecfdf5;
        color: #047857;
        border: 1px solid #a7f3d0;
        border-radius: 6px;
        padding: 0.2rem 0.6rem;
        font-size: 0.78rem;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }
    .report-title {
        color: #0f172a;
        font-size: 1.35rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }

    .analysis-block {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.02);
    }
    .analysis-label {
        font-size: 0.95rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.55rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .analysis-text {
        color: #334155;
        font-size: 0.95rem;
        line-height: 1.78;
        margin: 0;
    }

    /* 게시판 카드 */
    .post-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #0f172a;
        border-radius: 12px;
        padding: 1.15rem 1.4rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
    }
    .post-meta {
        color: #0f172a;
        font-weight: 700;
        font-size: 0.92rem;
        margin-bottom: 0.45rem;
    }
    .post-time {
        color: #64748b;
        font-weight: 500;
        font-size: 0.82rem;
        margin-left: 0.5rem;
    }
    .post-body {
        color: #334155;
        line-height: 1.7;
        font-size: 0.95rem;
        white-space: pre-wrap;
    }

    div.stButton > button {
        border-radius: 10px;
        font-weight: 600
