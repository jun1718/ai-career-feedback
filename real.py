from datetime import datetime
import streamlit as st
import json
import os
from datetime import date
import openai
import streamlit as st
import os

os.environ["OPENAI_API_KEY"] = st.secrets["API_KEY"]
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 스타일 정의
def local_css():
    st.markdown("""
    <style>
        /* 기본 스타일 */
        body {
            font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
            background-color: #FFFFFF;
        }
        
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        
        /* 헤더 및 텍스트 스타일 */
        h1, .main-header {
            color: #3271ff;
            font-weight: 700;
            font-size: 2.2rem;
            margin-bottom: 1rem;
        }
        
        h2, h3, .sub-header {
            color: #3271ff;
            font-size: 1.4rem;
            font-weight: 600;
            margin: 1.5rem 0 1rem 0;
        }
        
        .caption {
            color: #6B7280;
            font-size: 1rem;
            margin-bottom: 2rem;
        }
        
        /* 버튼 스타일 */
        .stButton>button {
            background-color: #3271ff;
            color: white;
            border-radius: 8px;
            transition: all 0.3s;
            border: none;
            padding: 0.5rem 1rem;
            font-size: 0.95rem;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(50, 113, 255, 0.2);
        }
        
        .stButton>button:hover {
            background-color: #2056cc;
            box-shadow: 0 4px 8px rgba(50, 113, 255, 0.3);
            transform: translateY(-1px);
        }
        
        .stButton>button:disabled {
            background-color: #E5E7EB;
            color: #9CA3AF;
            box-shadow: none;
        }
        
        /* 컨테이너 스타일 */
        [data-testid="stContainer"], [data-testid="stVerticalBlock"] {
            border-radius: 12px;
        }
        
        /* 입력 폼 스타일 */
        textarea, input[type="text"], select, .stSelectbox, .stTextInput {
            border-radius: 8px !important;
            border: 1px solid #E5E7EB !important;
            padding: 0.75rem !important;
            font-size: 0.95rem !important;
            transition: all 0.3s;
        }
        
        textarea:focus, input[type="text"]:focus, select:focus {
            border-color: #3271ff !important;
            box-shadow: 0 0 0 3px rgba(50, 113, 255, 0.2) !important;
        }
        
        /* 컬럼 헤더 */
        .column-header {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #3271ff;
            border-bottom: 2px solid #3271ff;
            padding-bottom: 0.5rem;
        }
        
        /* 카드 스타일 */
        .info-box {
            background-color: #F9FAFB;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            border-left: 4px solid #3271ff;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        }
        
        .story-box {
            background-color: #F0F7FF;
            border-left-color: #3271ff;
        }
        
        .advice-box {
            background-color: #F0F9FF;
            border-left-color: #3271ff;
        }
        
        /* 폼 스타일 */
        .stForm {
            background-color: #FFFFFF;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            border: 1px solid #E5E7EB;
        }
        
        /* 경고 및 성공 메시지 */
        .stAlert {
            border-radius: 8px;
        }
        
        .stAlert p {
            font-size: 0.95rem;
        }
        
        /* 모바일 최적화 */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 1rem;
            }
            
            h1, .main-header {
                font-size: 1.8rem;
            }
            
            .stButton>button {
                padding: 0.4rem 0.8rem;
                font-size: 0.9rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

if "curr_page" not in st.session_state:
    st.session_state.curr_page = "intro"

def load_profile_data():
    """저장된 프로필 데이터 불러오기"""
    if os.path.exists('profile_data.json'):
        try:
            with open('profile_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"프로필 데이터 로드 오류: {e}")
            return {}
    return {}

def load_daily_data():
    filename = 'daily_data.json'
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        return {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"daily 데이터 로드 오류: {e}")
        return {}

if "profiles" not in st.session_state:
    # 저장된 프로필 데이터 불러오기
    profiles = load_profile_data()
    st.session_state.profiles = profiles

if "daily_data" not in st.session_state:
    daily_data = load_daily_data()
    st.session_state.daily_data = daily_data

roleplays = {
    'task': {"display_name":'오늘의 업무 등록하기', 'emoji': '🏦'},
    'feedback': {'display_name':'커리어 피드백 받기', 'emoji': '☕️'},
}


# 드롭다운 옵션 정의
INDUSTRIES = [
    "IT/소프트웨어",
    "금융/보험",
    "제조/생산",
    "의료/바이오",
    "유통/물류",
    "건설/부동산",
    "서비스업",
    "교육",
    "미디어/콘텐츠",
    "기타"
]

POSITIONS = {
    "IT/소프트웨어": ["백엔드개발", "프론트엔드개발", "풀스택개발", "앱개발", "데이터엔지니어", "데이터분석가", "QA/테스터", "DevOps", "보안엔지니어", "PM/PO"],
    "금융/보험": ["재무분석", "투자운용", "리스크관리", "회계", "세무", "금융상품개발", "애널리스트", "자산관리"],
    "제조/생산": ["생산관리", "품질관리", "공정관리", "설비관리", "자재관리", "공장운영", "R&D"],
    "건설/부동산": ["건축설계", "시공", "감리", "철근조립", "안전관리", "부동산개발", "부동산중개"],
    "기타": ["마케팅", "영업", "인사", "총무", "기획", "디자인", "고객관리"]
}


def save_profile(name, position, industry, career_experience, career_goal, desired_industry):
    profiles = st.session_state.profiles

    st.session_state.profiles[name] = {
        "position": position,
        "industry": industry,
        "career_experience": career_experience,
        "career_goal": career_goal,
        "desired_industry": desired_industry
    }
    save_json_data(profiles, 'profile')

def save_daily(name, today_task_content, emotion, retrospective, importance):
    daily_data = st.session_state.daily_data

    # 오늘 날짜 YYYY-MM-DD
    today = date.today().isoformat()
    entry = {today: {
        "today_task_content": today_task_content,
        "emotion": emotion,
        "retrospective": retrospective,
        "importance": importance
    }}

    # st.session_state.daily_data가 없으면 생성
    if "daily_data" not in st.session_state:
        st.session_state.daily_data = {}

    daily_data = st.session_state.daily_data

    if name in daily_data:
        found = False
        for idx, date_entry in enumerate(daily_data[name]):
            if today in date_entry:
                daily_data[name][idx] = entry   # 기존 일자 덮어쓰기
                found = True
                break
        if not found:
            # 오늘 일자가 없다면 추가가
            daily_data[name].append(entry)
    else:
        daily_data[name] = [entry]

    save_json_data(daily_data, 'daily')

def get_position_options(industry):
    """산업에 따른 직무 옵션 반환"""
    return POSITIONS.get(industry, POSITIONS["기타"])

def save_json_data(dic_data, data_type):

    try:
        with open(f'{data_type}_data.json', 'w', encoding='utf-8') as f:
            json.dump(dic_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"json 데이터 저장 오류: {e}")
        return False

def go_to_page(role_play):
    st.session_state['curr_page'] = role_play

def roleplay_start(roleplay):
    st.session_state['roleplay'] = roleplay
    st.session_state['roleplay_info'] = roleplays[roleplay]
    go_to_page(roleplay)



def display_roleplay(roleplay, roleplay_info, key):
    with st.container(border=True):
        st.write(f"**{roleplay_info['display_name']}**")
        st.write(roleplay_info['emoji'])
        st.button("시작", key=f"btn_start_role_ply_{key}", on_click=roleplay_start, kwargs=dict(roleplay=roleplay))


curr_page = st.session_state["curr_page"]

def profile_action():
    profiles = st.session_state.profiles
    daily_data = st.session_state.daily_data

    # CSS 적용
    local_css()

    # 헤더 영역
    st.markdown('<h1 class="main-header">👤 커리어 프로필 입력</h1>', unsafe_allow_html=True)
    st.markdown('<p class="caption">성장 분석을 위한 프로필 정보를 입력해주세요</p>', unsafe_allow_html=True)

    # 구분선
    st.markdown("<hr style='margin: 1rem 0 2rem 0; border: none; height: 1px; background-color: #E5E7EB;'>", unsafe_allow_html=True)

    # 프로필 생성 카드
    st.markdown("""
    <div style="background-color: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05); 
                border: 1px solid #F3F4F6; margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="background-color: #EBF5FF; border-radius: 12px; width: 48px; height: 48px; 
                        display: flex; align-items: center; justify-content: center; margin-right: 1rem;">
                <span style="font-size: 24px;">📝</span>
            </div>
            <h3 style="margin: 0; color: #3271ff; font-size: 1.3rem;">새 프로필 생성</h3>
        </div>
        <p style="color: #4B5563; font-size: 0.95rem; margin-bottom: 0.5rem;">
            커리어 분석을 위한 기본 정보를 입력해주세요. 이 정보는 AI의 분석 및 제안에 활용됩니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 프로필 입력 폼
    with st.form("new_profile_form", border=False):
        st.markdown('<h3 style="color: #3271ff; margin-top: 0; font-size: 1.2rem;">기본 정보</h3>', unsafe_allow_html=True)

        # 이름 입력
        name = st.text_input("이름", placeholder="이름을 입력하세요", help="프로필을 식별하기 위한 이름입니다.")

        st.markdown('<h3 style="color: #3271ff; margin-top: 1.5rem; font-size: 1.2rem;">현재 직무 정보</h3>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            # 업종 선택 (드롭다운)
            selected_industry = st.selectbox(
                "현재 업종",
                options=INDUSTRIES,
                help="현재 종사하고 있는 업종을 선택하세요."
            )

            # 업종에 따른 직무 옵션 가져오기
            position_options = get_position_options(selected_industry)

            # 직무 선택 (드롭다운)
            selected_position = st.selectbox(
                "현재 직무",
                options=position_options,
                help="현재 담당하고 있는 직무를 선택하세요."
            )

        with col2:
            # 경력 및 희망 업종 정보 입력
            desired_industry = st.selectbox(
                "희망 업종",
                options=INDUSTRIES,
                help="향후 이직하거나 발전하고 싶은 업종을 선택하세요."
            )

        st.markdown('<h3 style="color: #3271ff; margin-top: 1.5rem; font-size: 1.2rem;">경력 및 목표</h3>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            # 경력 입력
            career_experience = st.text_area(
                "경력 상세",
                placeholder="예: 2년 2개월 동안 자바개발을 담당했으며, 백오피스 시스템과 고객 관리 시스템을 구축했습니다...",
                height=150,
                help="이전 경력과 주요 업무 경험을 간략하게 기술하세요."
            )

        with col2:
            # 커리어 목표 입력
            career_goal = st.text_area(
                "커리어 목표",
                placeholder="예: 5년 내 IT 부서 팀장으로 승진하고, 10년 내 기술 이사 직급에 도달하는 것이 목표입니다...",
                height=150,
                help="앞으로 이루고 싶은 커리어 목표와 방향성을 자유롭게 기술하세요."
            )

        # 제출 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("프로필 생성하기", use_container_width=True)

        # 폼 제출 처리
        if submitted:
            if not name:
                st.error("⚠️ 이름을 입력해주세요.")
            else:
                # 새 프로필 정보 저장
                save_profile(name, selected_position, selected_industry, career_experience, career_goal, desired_industry)

                # 성공 메시지와 함께 애니메이션 효과
                st.success(f"✅ {name}님의 프로필이 성공적으로 생성되었습니다!")
                st.balloons()

                # 1.5초 후 인트로 페이지로 리디렉션
                import time
                time.sleep(1.5)
                go_to_page("intro")
                st.rerun()

    # 홈으로 돌아가기 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("이전 페이지로 돌아가기", use_container_width=True):
            go_to_page("intro")
            st.rerun()

def task_action():
    profiles = st.session_state.profiles
    daily_data = st.session_state.daily_data

    # session_state 초기화
    if "step" not in st.session_state:
        st.session_state.step = 1
    if "task" not in st.session_state:
        st.session_state.task = ""
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = ""
    if "emotion" not in st.session_state:
        st.session_state.emotion = ""
    if "reflection" not in st.session_state:
        st.session_state.reflection = ""

    # CSS 적용
    local_css()

    # 헤더 영역
    st.markdown("<h1 class='main-header'>📝 오늘의 한줄</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='caption'><b>{date.today().strftime('%Y년 %m월 %d일')}</b> 기록을 시작해볼까요?</p>", unsafe_allow_html=True)

    # 구분선
    st.markdown("<hr style='margin: 1rem 0 2rem 0; border: none; height: 1px; background-color: #E5E7EB;'>", unsafe_allow_html=True)

    # 컨텐츠 영역
    col_form, col_summary = st.columns([3, 2], gap="large")

    # 오른쪽: 입력 요약
    with col_summary:
        st.markdown("""
        <div style="background-color: #F0F7FF; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #3271ff; 
                   box-shadow: 0 2px 6px rgba(50, 113, 255, 0.1);">
            <h3 style="margin-top: 0; color: #3271ff; font-size: 1.2rem; border-bottom: 1px solid #E5E7EB; 
                      padding-bottom: 0.5rem; margin-bottom: 1rem;">
                📋 오늘 기록 요약
            </h3>
        """, unsafe_allow_html=True)

        # 입력 단계별 상태 표시
        steps = [
            {"name": "업무", "key": "task", "icon": "✅"},
            {"name": "난이도", "key": "difficulty", "icon": "🔄"},
            {"name": "감정", "key": "emotion", "icon": "😊"},
            {"name": "회고", "key": "reflection", "icon": "💭"}
        ]

        for step in steps:
            value = st.session_state.get(step["key"], "")
            if value:
                status = f"<span style='color: #3271ff; font-weight: 500;'>{value}</span>"
                if step["key"] == "difficulty":
                    # 난이도에 따라 다른 이모지 표시
                    difficulty_icons = {
                        "매우 쉬움": "😌", "쉬움": "🙂", "보통": "😐",
                        "어려움": "😓", "매우 어려움": "😰"
                    }
                    icon = difficulty_icons.get(value, step["icon"])
                else:
                    icon = step["icon"]
            else:
                status = "<span style='color: #9CA3AF;'>미입력</span>"
                icon = "⬜"

            st.markdown(f"<p style='margin-bottom: 0.8rem;'><b>{icon} {step['name']}:</b> {status}</p>",
                        unsafe_allow_html=True)

        # 단계 진행률 표시
        progress = 0
        if st.session_state.step == 'done':
            progress = 100
        else:
            # 1~4단계: 각 25% 증가
            progress = min(100, (st.session_state.step - 1) * 25)

        st.markdown(f"""
        <div style="margin-top: 1.5rem;">
            <p style="margin-bottom: 0.5rem; font-size: 0.9rem; color: #4B5563;">진행률: {progress}%</p>
            <div style="background-color: #E5E7EB; border-radius: 9999px; height: 8px; width: 100%;">
                <div style="background-color: #3271ff; border-radius: 9999px; height: 8px; width: {progress}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # 홈으로 돌아가기 버튼
        if st.button("홈으로 돌아가기", use_container_width=True, key="go_home"):
            go_to_page("home")
            st.rerun()

    # 왼쪽: 입력 폼
    with col_form:
        st.markdown("""
        <div style="background-color: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                   border: 1px solid #E5E7EB;">
        """, unsafe_allow_html=True)

        task = ""
        difficulty = ""
        emotion = ""
        reflection = ""

        def next_step(current_value, key, next_step_num):
            if current_value.strip():
                st.session_state[key] = current_value
                st.session_state.step = next_step_num
            else:
                st.warning("❗내용을 입력해주세요!")

        if st.session_state.step == 'done':
            st.markdown("""
            <div style="text-align: center; padding: 2rem 0;">
                <div style="font-size: 64px; margin-bottom: 1rem;">🎉</div>
                <h2 style="color: #3271ff; margin-bottom: 1rem;">기록 완료!</h2>
                <p style="color: #4B5563; font-size: 1rem; margin-bottom: 1.5rem;">
                    오늘의 경력 관리 기록이 성공적으로 저장되었습니다.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()

        elif st.session_state.step == 5:
            name = st.session_state.name
            save_daily(
                name,
                st.session_state.task,
                st.session_state.emotion,
                st.session_state.reflection,
                st.session_state.difficulty
            )
            st.session_state.step = 'done'
            st.rerun()


        else:
            if st.session_state.step == 1:
                st.markdown('<h3 style="color: #3271ff; margin-top: 0;">1️⃣ 오늘, 가장 기억하고 싶은 업무를 떠올려볼까요?</h3>', unsafe_allow_html=True)
                task = st.text_area(
                    "업무 입력",
                    value=st.session_state.task,
                    placeholder="예) 신규 서비스 아이디어 회의 진행",
                    label_visibility="collapsed",
                    height=150,
                    key="task_input")
                if st.button("다음 단계로", key="next1", use_container_width=True):
                    next_step(task, "task", 2)
                    st.rerun()

            elif st.session_state.step == 2:
                st.markdown('<h3 style="color: #3271ff; margin-top: 0;">2️⃣ 이 업무의 난이도는 어땠나요?</h3>', unsafe_allow_html=True)

                # 시각적으로 개선된 라디오 버튼
                difficulty_options = ["매우 쉬움", "쉬움", "보통", "어려움", "매우 어려움"]
                difficulty_emojis = ["😌", "🙂", "😐", "😓", "😰"]

                st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)

                cols = st.columns(5)
                selected_idx = difficulty_options.index(st.session_state.difficulty) if st.session_state.difficulty in difficulty_options else 2

                for i, (option, emoji) in enumerate(zip(difficulty_options, difficulty_emojis)):
                    with cols[i]:
                        is_selected = i == selected_idx
                        bg_color = "#EBF5FF" if is_selected else "white"
                        border_color = "#3271ff" if is_selected else "#E5E7EB"

                        st.markdown(f"""
                        <div style="text-align: center; padding: 0.8rem 0.5rem; border-radius: 8px; 
                                  border: 2px solid {border_color}; background-color: {bg_color}; cursor: pointer;"
                             onclick="document.querySelector('#{option.replace(' ', '_')}').click();">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{emoji}</div>
                            <div style="font-size: 0.8rem; color: {'#3271ff' if is_selected else '#4B5563'};">
                                {option}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                # 실제 선택을 위한 숨겨진 라디오 버튼
                difficulty = st.radio(
                    "난이도 선택",
                    difficulty_options,
                    index=selected_idx,
                    label_visibility="collapsed",
                    horizontal=True,
                    key="difficulty_input")

                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("이전", key="prev2"):
                        st.session_state.step = 1
                        st.rerun()
                with col2:
                    if st.button("다음 단계로", key="next2", use_container_width=True):
                        st.session_state.difficulty = difficulty
                        st.session_state.step = 3
                        st.rerun()

            elif st.session_state.step == 3:
                st.markdown('<h3 style="color: #3271ff; margin-top: 0;">3️⃣ 그 일을 하면서 어떤 감정을 느꼈나요?</h3>', unsafe_allow_html=True)

                # 감정 입력에 도움이 되는 힌트 추가
                st.markdown("""
                <div style="background-color: #F9FAFB; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem; font-size: 0.9rem;">
                    <p style="margin: 0; color: #4B5563;">
                        <b>💡 도움말:</b> 성취감, 보람, 답답함, 성장감, 불안함, 자신감 등 업무에서 느낀 감정을 표현해보세요.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                emotion = st.text_area(
                    "감정 입력",
                    value=st.session_state.emotion,
                    placeholder="예) 긴장했지만 발표 후 뿌듯함을 느꼈다.",
                    label_visibility="collapsed",
                    height=120,
                    key="emotion_input")

                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("이전", key="prev3"):
                        st.session_state.step = 2
                        st.rerun()
                with col2:
                    if st.button("다음 단계로", key="next3", use_container_width=True):
                        next_step(emotion, "emotion", 4)
                        st.rerun()

            elif st.session_state.step == 4:
                st.markdown('<h3 style="color: #3271ff; margin-top: 0;">4️⃣ 오늘의 업무를 돌아보며, 느낀 점을 기록해볼까요?</h3>', unsafe_allow_html=True)

                # 회고 입력에 도움이 되는 힌트 추가
                st.markdown("""
                <div style="background-color: #F9FAFB; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem; font-size: 0.9rem;">
                    <p style="margin: 0; color: #4B5563;">
                        <b>💡 도움말:</b> 배운 점, 잘한 점, 개선할 점, 다음에 시도해볼 것 등을 생각해보세요.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                reflection = st.text_area(
                    "회고 입력",
                    value=st.session_state.reflection,
                    placeholder="예) 발표 준비가 철저해서 성공적이었지만, 시간 관리는 더 필요하다 느꼈다.",
                    label_visibility="collapsed",
                    height=150,
                    key="reflection_input")

                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("이전", key="prev4"):
                        st.session_state.step = 3
                        st.rerun()
                with col2:
                    if st.button("✅ 기록 저장하기", key="save", use_container_width=True):
                        next_step(reflection, "reflection", 5)
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

def intro_action():
    profiles = st.session_state.profiles
    daily_data = st.session_state.daily_data

    # 커스텀 CSS 적용
    local_css()

    # 세션 상태에 따라 다른 화면 표시
    if "show_main" not in st.session_state:
        st.session_state.show_main = False

    if not st.session_state.show_main:
        # 초기 시작 화면 (이미지와 시작하기 버튼만 표시)
        container = st.container()
        with container:
            st.markdown("""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-top: 2rem;">
                <img src="https://ifh.cc/g/4y51bf.jpg" style="max-width: 80%; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);">
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("시작하기", use_container_width=True, key="start_button",
                             type="primary", help="클릭하면 메인 화면으로 이동합니다"):
                    st.session_state.show_main = True
                    st.rerun()
    else:
        # 메인 화면 (로그인 및 프로필 생성)
        st.markdown("<h1 class='main-header'>나만의 커리어 번역기 🧙</h1>", unsafe_allow_html=True)
        st.markdown("<p class='caption'>당신의 물경력, 멋쟁이 불경력으로 번역해 드립니다.</p>", unsafe_allow_html=True)

        # 구분선
        st.markdown("<hr style='margin: 2rem 0; border: none; height: 1px; background-color: #E5E7EB;'>", unsafe_allow_html=True)

        # 로그인 카드
        st.markdown("""
        <div style="background-color: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); border: 1px solid #F3F4F6;">
            <h2 style="margin-top: 0; color: #3271ff; font-size: 1.5rem;">👋 시작하기</h2>
        </div>
        """, unsafe_allow_html=True)

        input_name = st.text_input("이름을 입력하세요", key="input_name",
                                   placeholder="이름을 입력해주세요")

        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("접속하기", use_container_width=True, disabled=(not input_name),
                         key="login_button"):
                if input_name in profiles:
                    st.session_state["user_name"] = input_name
                    st.session_state.name = input_name
                    go_to_page("home")
                    st.rerun()
                else:
                    st.warning("⚠️ 아직 등록된 프로필이 없습니다. 아래에서 프로필을 생성해 주세요!")
        with col2:
            if st.button("프로필 생성", use_container_width=True, disabled=(not input_name),
                         key="create_profile_button"):
                if input_name in profiles:
                    st.error("⚠️ 이미 동일한 이름의 프로필이 있습니다. 다른 이름을 입력해 주세요!")
                else:
                    go_to_page("profile")
                    st.rerun()

        # 기능 소개 카드
        st.markdown("<h3 style='margin-top: 3rem;'>주요 기능</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="background-color: #F0F7FF; padding: 1.5rem; border-radius: 12px; height: 100%;">
                <h3 style="margin-top: 0; color: #3271ff; font-size: 1.2rem;">✍️ 일일 업무 기록</h3>
                <p style="color: #4B5563; font-size: 0.95rem;">
                    매일의 업무 내용과 감정, 회고를 기록하고 업무 패턴을 파악해보세요.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style="background-color: #F0F7FF; padding: 1.5rem; border-radius: 12px; height: 100%;">
                <h3 style="margin-top: 0; color: #3271ff; font-size: 1.2rem;">🧙 커리어 분석 및 피드백</h3>
                <p style="color: #4B5563; font-size: 0.95rem;">
                    AI가 기록된 업무를 분석하여 커리어 성장 방향을 제안합니다.
                </p>
            </div>
            """, unsafe_allow_html=True)

def home_action():
    # CSS 적용
    local_css()

    # 헤더 영역
    st.markdown("<h1 class='main-header'>커리어 대시보드 🚀</h1>", unsafe_allow_html=True)

    if "name" in st.session_state:
        st.markdown(f"<p class='caption'><b>{st.session_state.name}</b>님의 커리어 관리 대시보드입니다.</p>", unsafe_allow_html=True)

    # 구분선
    st.markdown("<hr style='margin: 1.5rem 0; border: none; height: 1px; background-color: #E5E7EB;'>", unsafe_allow_html=True)

    # 업무 데이터 요약 계산
    name = st.session_state.get("name", "")
    daily_data = st.session_state.daily_data
    task_count = 0
    recent_tasks = []

    if name in daily_data:
        task_entries = daily_data[name]
        task_count = len(task_entries)

        # 최근 3개의 업무 추출
        for entry in task_entries[-3:]:  # 가장 최근 3개 항목
            for date, task_data in entry.items():
                task_content = task_data.get("today_task_content", "")
                if len(task_content) > 30:
                    task_content = task_content[:30] + "..."
                recent_tasks.append({"date": date, "content": task_content})

    # 진행률 계산
    progress_percentage = min(task_count * 10, 100)

    # 대시보드 레이아웃 개선
    col_stats, col_graph = st.columns([1, 1], gap="large")

    # 왼쪽 열: 업무 통계
    with col_stats:
        with st.container():
            # 헤더
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown('<div style="background-color: #EBF5FF; border-radius: 12px; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center;"><span style="font-size: 24px;">📊</span></div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<h3 style="margin: 0; color: #3271ff; font-size: 1.2rem; padding-top: 12px;">나의 업무 통계</h3>', unsafe_allow_html=True)

            # 통계 컨테이너
            with st.container(border=False):
                st.markdown('')  # 여백
                # 총 등록 업무
                col_label, col_value = st.columns([3, 1])
                with col_label:
                    st.markdown('<p style="color: #4B5563; font-size: 0.95rem;">총 등록한 업무</p>', unsafe_allow_html=True)
                with col_value:
                    st.markdown(f'<p style="color: #3271ff; font-weight: 600; font-size: 1.2rem; text-align: right;">{task_count}개</p>', unsafe_allow_html=True)

                # 진행률 바
                st.progress(progress_percentage / 100)
                st.markdown('')  # 여백

                # 최근 기록
                st.markdown('<p style="color: #4B5563; font-size: 0.95rem; font-weight: 500; margin-bottom: 0.5rem;">최근 기록:</p>', unsafe_allow_html=True)

                if recent_tasks:
                    for task in recent_tasks:
                        col_date, col_content = st.columns([1, 3])
                        with col_date:
                            st.markdown(f'<p style="color: #6B7280; font-size: 0.85rem;">{task["date"]}</p>', unsafe_allow_html=True)
                        with col_content:
                            st.markdown(f'<p style="color: #111827; font-size: 0.9rem;">{task["content"]}</p>', unsafe_allow_html=True)
                else:
                    st.info("아직 등록된 업무가 없습니다")

    # 오른쪽 열: 경력 요약
    with col_graph:
        with st.container():
            # 헤더
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown('<div style="background-color: #EBF5FF; border-radius: 12px; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center;"><span style="font-size: 24px;">✨</span></div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<h3 style="margin: 0; color: #3271ff; font-size: 1.2rem; padding-top: 12px;">나의 경력 한눈에 보기</h3>', unsafe_allow_html=True)

            # 통계 컨테이너
            with st.container(border=False):
                st.markdown('')  # 여백
                # 상태 메시지
                status_emoji = "🚀" if task_count > 0 else "📝"
                status_message = f"지금까지 {task_count}개의 업무를 기록했습니다!" if task_count > 0 else "첫 번째 업무를 등록해보세요!"
                status_desc = "계속해서 업무를 기록하고 커리어를 성장시켜보세요!" if task_count > 0 else "업무 기록을 통해 커리어 여정을 시작하세요."

                st.markdown(f'<div style="text-align: center; padding: 1rem 0;">', unsafe_allow_html=True)
                st.markdown(f'<p style="color: #4B5563; font-size: 0.95rem; margin-bottom: 1rem;">{status_message}</p>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size: 64px; margin-bottom: 1rem;">{status_emoji}</div>', unsafe_allow_html=True)
                st.markdown(f'<p style="color: #6B7280; font-size: 0.9rem;">{status_desc}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    # 주요 기능 카드 영역
    st.markdown("<h2 style='color: #3271ff; margin: 1rem 0 1.5rem 0; font-size: 1.4rem;'>무엇을 도와드릴까요?</h2>", unsafe_allow_html=True)

    cols = st.columns(2, gap="large")

    # 업무 기록 카드
    with cols[0]:
        with st.container(border=True):
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown('<div style="background-color: #EBF5FF; border-radius: 12px; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center;"><span style="font-size: 24px;">📝</span></div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<h3 style="margin: 0; color: #3271ff; font-size: 1.2rem; padding-top: 12px;">오늘의 한줄</h3>', unsafe_allow_html=True)

            st.markdown('<p style="color: #4B5563; font-size: 0.95rem; margin: 1rem 0;">오늘 수행한 주요 업무와 그 과정에서의 감정, 회고를 기록하세요.</p>', unsafe_allow_html=True)

            if st.button("업무 기록하기", use_container_width=True, key="task_button"):
                roleplay_start('task')
                st.rerun()

    # 커리어 피드백 카드
    with cols[1]:
        with st.container(border=True):
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown('<div style="background-color: #EBF5FF; border-radius: 12px; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center;"><span style="font-size: 24px;">🧙</span></div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<h3 style="margin: 0; color: #3271ff; font-size: 1.2rem; padding-top: 12px;">커리어 피드백 받기</h3>', unsafe_allow_html=True)

            st.markdown('<p style="color: #4B5563; font-size: 0.95rem; margin: 1rem 0;">기록된 업무를 AI가 분석하여 커리어 성장 방향을 제안합니다.</p>', unsafe_allow_html=True)

            if st.button("피드백 받기", use_container_width=True, key="feedback_button"):
                roleplay_start('feedback')
                st.rerun()

    # 프로필 관리 영역
    st.markdown("<h2 style='color: #3271ff; margin: 2.5rem 0 1.5rem 0; font-size: 1.4rem;'>프로필 관리</h2>", unsafe_allow_html=True)

    # 프로필 카드
    with st.container(border=True):
        col1, col2 = st.columns([1, 5])
        with col1:
            st.markdown('<div style="background-color: #EBF5FF; border-radius: 12px; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center;"><span style="font-size: 24px;">👤</span></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<h3 style="margin: 0; color: #3271ff; font-size: 1.2rem; padding-top: 12px;">내 프로필 관리</h3>', unsafe_allow_html=True)

        st.markdown('<p style="color: #4B5563; font-size: 0.95rem; margin: 1rem 0 1.5rem 0;">커리어 프로필을 업데이트하고 관리하세요.</p>', unsafe_allow_html=True)

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("프로필 수정", use_container_width=True, key="edit_profile_button"):
                go_to_page("profile")
                st.rerun()
        with col2:
            if st.button("로그아웃", use_container_width=True, key="logout_button"):
                go_to_page("intro")
                st.rerun()

def feedback_action():
    name = st.session_state.name

    # 헤더 표시
    st.markdown('<h1 style="text-align: center; color: #3271ff; margin-bottom: 2rem;">커리어 성장 피드백 받기</h1>', unsafe_allow_html=True)

    # 상단 정보 영역
    st.markdown("""
    <div style="background-color: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); margin-bottom: 2rem; border: 1px solid #E5E7EB;">
    """, unsafe_allow_html=True)

    # 프로필 정보 표시
    if name in st.session_state.profiles:
        profile = st.session_state.profiles[name]
        st.markdown(f"""
        <h3 style="margin-top: 0; font-size: 1.2rem;">👤 {name}님의 프로필</h3>
        <p><strong>현재 직무:</strong> {profile.get('industry', '정보 없음')} > {profile.get('position', '정보 없음')}</p>
        <p><strong>희망 업종:</strong> {profile.get('desired_industry', '정보 없음')}</p>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ 프로필 정보를 찾을 수 없습니다. 프로필을 먼저 생성해주세요.")

    # 데일리 데이터 확인
    daily_data = st.session_state.daily_data.get(name, [])
    has_daily_data = len(daily_data) > 0

    # 업무 기록 유무에 따라 다른 메시지 표시
    if not has_daily_data:
        st.markdown("""
        <div style="background-color: #FEF9C3; padding: 0.8rem; border-radius: 8px; font-size: 0.9rem; margin-bottom: 1rem;">
            <p style="margin: 0; color: #854D0E;">
                <b>⚠️ 참고:</b> 업무 기록이 없어 프로필 정보만 기반으로 분석이 진행됩니다. 더 정확한 분석을 위해 업무 기록을 추가해보세요.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background-color: #F9FAFB; padding: 0.8rem; border-radius: 8px; font-size: 0.9rem;">
            <p style="margin: 0; color: #4B5563;">
                <b>💡 참고:</b> 더 많은 업무 기록을 입력할수록 더 정확한 분석 결과를 제공합니다.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 자기소개서 설정 초기화 - 이미 있는 경우에는 초기화하지 않음
    if "cover_letter_position" not in st.session_state:
        st.session_state.cover_letter_position = ""
    if "cover_letter_prompt" not in st.session_state:
        st.session_state.cover_letter_prompt = "지원 동기와 입사 후 포부를 기술해주세요."

    # 분석 시작 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit_button = st.button("✨ 커리어 분석 시작하기", use_container_width=True, key="analyze_button")

    # 결과 영역
    story_response_text = ""
    cover_letter_text = ""

    if submit_button:
        # 분석 중 상태 표시
        st.markdown("""
        <div style="background-color: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); margin: 2rem 0; border: 1px solid #E5E7EB;">
            <h3 style="margin-top: 0; font-size: 1.2rem;">분석 진행 중...</h3>
        """, unsafe_allow_html=True)

        # 진행 상태 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.markdown("<p style='color: #3271ff;'><b>🔍 업무 기록 데이터 분석 중...</b></p>", unsafe_allow_html=True)

        # OpenAI API 클라이언트 초기화
        from openai import OpenAI
        client = OpenAI()

        # 프로필 정보
        profile = st.session_state.profiles.get(name, {})
        profile_json = json.dumps(profile, ensure_ascii=False)

        # 업무 경험 추출
        keyword = ""

        if has_daily_data:
            # 데일리 데이터에서 중요 키워드 추출
            tasks = []
            for entry in daily_data:
                # 각 데일리 데이터 항목에서 필요한 정보 추출
                tasks.append({
                    "task": entry.get("today_task_content", ""),
                    "emotion": entry.get("emotion", ""),
                    "retrospective": entry.get("retrospective", ""),
                    "importance": entry.get("importance", "")
                })

            # 업무 데이터 JSON 형식으로 변환
            tasks_json = json.dumps(tasks, ensure_ascii=False)

            # 시스템 프롬프트 정의
            system_prompt = """
            너는 프로페셔널한 커리어 코치이다. 유저의 데일리 업무 기록과 프로필 정보를 분석하여 커리어 스토리를 재구성해야 한다.
            
            다음 지침을 따라 분석을 진행한다:
            1. 유저의 데일리 업무 기록에서 가장 중요한 키워드를 추출한다.
            2. 추출된 키워드를 바탕으로 업무 패턴을 파악한다.
            3. 업무 패턴과 프로필 정보를 기반으로 유저의 커리어 스토리를 구성한다.
            
            커리어 스토리 구성 시 다음 요소를 포함하도록 한다:
            - 주요 업무 분야와 직무 역량
            - 업무 처리 방식이나 스타일의 특징
            - 전문성이나 특기를 보여주는 부분
            - 업무에서의 강점과 기여도
            - 주요 성과나 인정받은 부분
            
            결과 포맷:
            - 총 500자 내외의 스토리 형식으로 작성한다.
            - 부정적 표현보다는 긍정적이고 전문적인 표현을 사용한다.
            - 업무 기록 내용을 토대로 실제 직무 경험을 근거로 서술한다.
            - 단순 나열이 아닌 내러티브가 있는 스토리텔링 방식으로 작성한다.
            - 1인칭이 아닌 3인칭 객관적 시점으로 서술한다.
            """

            # 유저 프롬프트 정의
            user_prompt = f"프로필 정보: {profile_json}\n\n업무 기록 데이터: {tasks_json}"

            # 진행 상태 업데이트
            progress_bar.progress(20)
            status_text.markdown("<p style='color: #3271ff;'><b>🔄 업무 패턴 분석 중...</b></p>", unsafe_allow_html=True)

            # 키워드 추출 API 호출
            keyword_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "유저의 업무 기록 데이터를 분석하여 가장 핵심적인 업무 내용, 역량, 특징을 400자 내로 요약하세요."},
                    {"role": "user", "content": f"업무 기록 데이터: {tasks_json}"}
                ],
                temperature=0.3
            )

            keyword = keyword_response.choices[0].message.content

            # 진행 상태 업데이트
            progress_bar.progress(30)
            status_text.markdown("<p style='color: #3271ff;'><b>📊 커리어 스토리 구성 중...</b></p>", unsafe_allow_html=True)

            # 스토리 생성 API 호출
            story_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )

            story_response_text = story_response.choices[0].message.content

            # 진행 상태 업데이트
            status_text.markdown("<p style='color: #3271ff;'><b>📝 자기소개서 작성 중...</b></p>", unsafe_allow_html=True)
            progress_bar.progress(50)

            # 자기소개서 작성을 위한 시스템 프롬프트
            cover_letter_system_prompt = """
            너는 취업 지원서의 자기소개서를 작성하는 전문가야.
            입력된 프로필 정보, 업무 경험, 지원 직무, 자기소개서 항목을 바탕으로 매력적이고 경쟁력 있는 자기소개서를 작성해줘.
            
            아래 지침을 반드시 모두 따라야 해:
            1. 실제 지원 항목과 같은 형식으로 작성하되, 기본적인 지원 동기와 포부를 중심으로 작성해.
            2. 주어진 프로필 정보와 업무 경험을 적극 활용하되, 실제 경험에 기반한 구체적인 사례를 포함해.
            3. 자기소개서 항목에 맞춰 핵심 역량과 경험을 드러내는 문장으로 구성해.
            4. 지원 직무와 관련된 전문성을 강조하되, 경력/학력 위주가 아닌 강점과 기여 가능성을 부각해.
            5. 800자 내외로 작성하되, 필요에 따라 2~3개 단락으로 나눠 가독성을 높여줘.
            6. 상투적인 표현은 피하고, 진정성 있고 차별화된 내용으로 작성해.
            7. 전체 문장은 공손하고 전문적인 어투로 작성해.
            8. 결론 부분에서는 입사 후 기여할 수 있는 부분을 간략히 언급해.
            """

            # 자기소개서 작성을 위한 유저 프롬프트
            cover_letter_user_prompt = f"프로필 정보: {profile_json}\n업무 경험: {keyword}\n지원 직무: {st.session_state.cover_letter_position}\n자기소개서 항목: {st.session_state.cover_letter_prompt}"

            # 자기소개서 API 호출
            cover_letter_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": cover_letter_system_prompt},
                    {"role": "user", "content": cover_letter_user_prompt}
                ],
                temperature=0.7
            )

            cover_letter_text = cover_letter_response.choices[0].message.content

            # 진행 상태 업데이트
            status_text.markdown("<p style='color: #3271ff;'><b>🚀 성장 방향 분석 중...</b></p>", unsafe_allow_html=True)
            progress_bar.progress(80)

            # 프로필 데이터 준비
            result = f"유저의 프로필 및 목표: {profile_json}\n유저의 요약된 업무 정보: {story_response_text}"

            # 업무 기록 유무에 따라 다른 프롬프트 사용
            if has_daily_data:
                advice_system_prompt = """
                너는 커리어 코칭 전문가야.
                아래 입력된 유저의 프로필과 커리어 목표와 실제로 이 유저의 요약된 업무 정보를 이용해서
                이 사람이 커리어 목표에 더 가까워지기 위해 추가로 해야 할 것들을 제안해줘.
                
                지침:
                1. 제목, 소제목, 헤더를 만들지마. 글자 크기 조정 문법은 쓰지마.
                2. 1, 2, 3과 같은 번호를 붙여 레벨링도 하지마.
                3. 필요시 이모티콘과 볼드 처리로 강조해줘
                4. 제안은 간결하고 구체적으로 작성해
                5. 3가지 내용을 다뤄줘
                    1) 첫번째는 커리어 목표를 고려해서 현재의 업무에서 도전할 수 있는 부분을 알려줘.
                    2) 두번째는 희망 업종을 고려해서 커리어 개발을 위해 일상적으로 할 수 있는 변화를 넣어
                    3) 세번째는 커리어 전문가로서 동기부여, 마음가짐 부분에 조언해줘 
                6. 현재의 직무와, 경력에 기반해서, 이 사람이 희망 직무, 업종에 가기 위한 조언을 스토리 안에 자연스럽게 포함해.           
                7. 각각의 제안 옆에 간단한 이유(1문장)를 추가해.
                8. 따뜻하고 긍정적인 말투를 사용해.
                9. 700자 내외로 적어줘
                10. 맨 마지막에는 "조금씩 쌓아가며 성장하는 당신을 응원합니다."로 마무리해.
                """
            else:
                # 업무 기록이 없는 경우 프로필 기반 조언 프롬프트
                advice_system_prompt = """
                너는 커리어 코칭 전문가야.
                아래 입력된 유저의 프로필과 커리어 목표를 바탕으로 이 사람이 커리어 목표에 더 가까워지기 위해 추가로 해야 할 것들을 제안해줘.
                
                지침:
                1. 제목, 소제목, 헤더를 만들지마. 글자 크기 조정 문법은 쓰지마.
                2. 1, 2, 3과 같은 번호를 붙여 레벨링도 하지마.
                3. 필요시 이모티콘과 볼드 처리로 강조해줘
                4. 제안은 간결하고 구체적으로 작성해
                5. 다음 5가지 내용을 다뤄줘:
                    1) 현재 직무에서 전문성을 높이기 위한 구체적인 스킬 개발 방향
                    2) 희망 업종으로 전환/성장하기 위해 필요한 역량과 준비사항
                    3) 현재 직무와 희망 업종을 연결할 수 있는 커리어 브릿지 전략 
                    4) 자기 개발을 위한 추천 학습 및 네트워킹 활동
                    5) 커리어 전문가로서 이 사람의 상황에 맞는 동기부여 조언
                6. 각각의 제안 옆에 간단한 이유(1문장)를 추가해.
                7. 따뜻하고 긍정적인 말투를 사용해.
                8. 700자 내외로 적어줘
                9. 맨 마지막에는 "조금씩 쌓아가며 성장하는 당신을 응원합니다."로 마무리해.
                """

            # 성장 방향 제안 API 호출
            advice_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": advice_system_prompt},
                    {"role": "user", "content": result}
                ],
                temperature=0.7
            )

            advice_response_text = advice_response.choices[0].message.content

            # 진행 상태 완료
            status_text.markdown("<p style='color: #10B981;'><b>✅ 분석 완료!</b></p>", unsafe_allow_html=True)
            progress_bar.progress(100)

            # 탭으로 결과 표시
            tab1, tab2, tab3 = st.tabs(["📈 재구성된 커리어 스토리", "📝 자기소개서", "🚀 성장 제안"])

            with tab1:
                st.markdown("""
                <div style="margin-top: 1rem;">
                    <h2 style="color: #3271ff; font-size: 1.4rem; margin-bottom: 1rem;">
                        <span style="margin-right: 0.5rem;">📈</span> 재구성된 커리어 스토리
                    </h2>
                    <div style="background-color: #F0F7FF; padding: 1.5rem; border-radius: 12px; 
                              border-left: 4px solid #3271ff; box-shadow: 0 2px 6px rgba(50, 113, 255, 0.1);">
                    {}
                </div>
                </div>
                """.format(story_response_text), unsafe_allow_html=True)

            with tab2:
                st.markdown("""
                <div style="margin-top: 1rem;">
                    <h2 style="color: #3271ff; font-size: 1.4rem; margin-bottom: 1rem;">
                        <span style="margin-right: 0.5rem;">📝</span> 자기소개서
                    </h2>
                </div>
                """, unsafe_allow_html=True)

                # 자기소개서 설정 입력 영역
                st.markdown("### 자기소개서 설정")
                col1, col2 = st.columns(2)
                with col1:
                    new_position = st.text_input("지원 직무",
                                                 value=st.session_state.cover_letter_position,
                                                 placeholder="예: 백엔드 개발자, 데이터 엔지니어",
                                                 key="cl_position_input")

                with col2:
                    new_prompt = st.text_input("자기소개서 항목",
                                               value=st.session_state.cover_letter_prompt,
                                               placeholder="예: 지원 동기와 입사 후 포부를 기술해주세요.",
                                               key="cl_prompt_input")

                # session_state 값을 폼 외부에서 즉시 업데이트 (key 변경)
                st.session_state.cover_letter_position = new_position
                st.session_state.cover_letter_prompt = new_prompt

                # 자기소개서 재생성 버튼
                if st.button("자기소개서 재생성", key="regenerate_cover_letter", use_container_width=True):
                    with st.spinner("자기소개서 재생성 중..."):
                        # 자기소개서 재생성 API 호출
                        updated_cover_letter_user_prompt = f"프로필 정보: {profile_json}\n업무 경험: {keyword}\n지원 직무: {st.session_state.cover_letter_position}\n자기소개서 항목: {st.session_state.cover_letter_prompt}"

                        updated_cover_letter_response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": cover_letter_system_prompt},
                                {"role": "user", "content": updated_cover_letter_user_prompt}
                            ],
                            temperature=0.7
                        )

                        cover_letter_text = updated_cover_letter_response.choices[0].message.content
                        st.rerun()

                # 자기소개서 내용 표시
                st.markdown("""
                <div style="background-color: #F0F7FF; padding: 1.5rem; border-radius: 12px; 
                          border-left: 4px solid #3271ff; box-shadow: 0 2px 6px rgba(50, 113, 255, 0.1);">
                    {}
                </div>
                """.format(cover_letter_text), unsafe_allow_html=True)

            with tab3:
                st.markdown("""
                <div style="margin-top: 1rem;">
                    <h2 style="color: #3271ff; font-size: 1.4rem; margin-bottom: 1rem;">
                        <span style="margin-right: 0.5rem;">🚀</span> 커리어 목표를 향한 성장 제안
                    </h2>
                    <div style="background-color: #F0F9FF; padding: 1.5rem; border-radius: 12px; 
                              border-left: 4px solid #3271ff; box-shadow: 0 2px 6px rgba(50, 113, 255, 0.1);">
                        {}
                    </div>
                </div>
                """.format(advice_response_text), unsafe_allow_html=True)

            # 축하 효과
            st.balloons()
            st.snow()

            # 시각적 구분선
            st.markdown("<hr style='margin: 3rem 0 1.5rem 0; border: none; height: 1px; background-color: #E5E7EB;'>", unsafe_allow_html=True)

            # 결과 저장 및 공유 영역
            st.markdown("""
            <div style="text-align: center; margin: 2rem 0;">
                <h3 style="color: #3271ff; margin-bottom: 1rem; font-size: 1.2rem;">분석 결과 저장</h3>
                <p style="color: #4B5563; font-size: 0.9rem; margin-bottom: 1rem;">
                    💡 분석 결과를 저장하시려면 스크린샷을 찍어두세요 📸
                </p>
            </div>
            """, unsafe_allow_html=True)

            # 홈으로 돌아가기 버튼
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("홈으로 돌아가기", use_container_width=True, key="go_home_button"):
                    go_to_page("home")
                    st.rerun()

    else:
        # 분석 예시 이미지 (선택 사항)
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            st.markdown("""
            <div style="text-align: center; margin: 2rem 0; opacity: 0.8;">
                <img src="https://cdn-icons-png.flaticon.com/512/2681/2681003.png" style="width: 180px; margin-bottom: 1rem;">
                <p style="color: #6B7280; font-size: 0.9rem;">
                    분석을 시작하려면 위의 버튼을 클릭하세요
                </p>
            </div>
            """, unsafe_allow_html=True)

            # 홈으로 돌아가기 버튼
            if st.button("홈으로 돌아가기", use_container_width=True, key="go_home_button2"):
                go_to_page("home")
                st.rerun()



if curr_page == "intro":
    intro_action()
elif curr_page == "home":
    home_action()
elif curr_page == "profile":
    profile_action()
elif curr_page == "task":
    task_action()
elif curr_page == "feedback":
    feedback_action()






# st.title("🔮팔랑팔랑")
# st.caption("오늘 있었떤 일을 들려줘!")
#
# keyword = st.text_area("오늘 가장 기록하고 싶은 업무 뭐야?  ✍️")
#
# if keyword:
#     with st.spinner("AI - 오늘의 경력 세분화중"):
#         user_input = ""
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {"role": "system", "content": """
#                 너는 커리어 스토리를 멋지게 작성하는 전문 작가야.
#                 아래 입력된 유저의 프로필과 업무 경험을 바탕으로,
#                 도전정신, 갈등관리능력, 리더십, 창의성 같은 키워드를 중심으로
#                 멋지고 전문성 있게 스토리를 작성해.
#
#                 아래 지침을 반드시 모두 따라야 해.
#
#                 1. 결과물은 "당신의 업무를 재구성하면 이렇게 됩니다:"로 시작해.
#                 2. 유저의 문장을 단순 요약하지 말고, '능력'과 '강점' 중심으로 새롭게 재해석해.
#                 3. 이름, 직무, 업종, 경력, 희망업종, 커리어목표 등 모든 프로필 정보를 반드시 스토리 안에 자연스럽게 포함해.
#                 4. 오늘 수행한 업무(2페이지)의 중요도, 감정, 회고를 스토리 안에 자연스럽게 녹여내야 해.
#                 5. 최소 2개 이상의 능력 키워드를 찾아서 문장 안에서 자연스럽게 강조해.
#                 6. 전체 문장은 따뜻하고 긍정적인 존댓말 톤으로 작성해.
#                 7. 마지막 문장은 "이런 강점을 바탕으로 당신은 커리어 목표에 꾸준히 다가가고 있습니다."로 마무리해.
#                 """},
#                 {"role": "user", "content": user_input}
#             ],
#             temperature=0.7
#         )
#         # st.write(response.output_text)
#         # st.image(img_response.data[0].url)
#         st.image(img_response.data[0].url)