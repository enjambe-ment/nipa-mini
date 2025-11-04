import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(
    page_title="HealthMap - 당뇨 건강 관리",
    layout="wide",
    page_icon="🏥",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS - 더욱 세련된 디자인
st.markdown("""
    <style>
    /* 메인 컨테이너 스타일 */
    .main {
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* 헤더 스타일 */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(120deg, #1f77b4, #2ecc71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        text-align: center;
        color: #5a6c7d;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    
    /* 섹션 헤더 */
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        padding: 0.8rem 1.5rem;
        background: linear-gradient(90deg, #e8f4f8, transparent);
        border-left: 5px solid #1f77b4;
        border-radius: 5px;
    }
    
    /* 카드 스타일 */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    /* 메트릭 카드 */
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Streamlit 기본 요소 스타일 오버라이드 */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
    }
    
    /* 사이드바 스타일 */
    .css-1d391kg {
        background: linear-gradient(180deg, #1f77b4 0%, #2ecc71 100%);
    }
    
    /* 입력 필드 스타일 */
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #1f77b4;
        box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ==================== 메인 헤더 ====================
st.markdown('<p class="main-header">🏥 HealthMap</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI 기반 당뇨병 건강 관리 플랫폼</p>', unsafe_allow_html=True)

# ==================== 1. 증상 입력 섹션 ====================
st.markdown('<p class="section-header">💬 증상 분석</p>', unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    user_input = st.text_input(
        "증상 입력",
        placeholder="예: 요즘 갈증이 심하고 소변을 자주 봐요...",
        label_visibility="collapsed",
        key="symptom_input"
    )
with col2:
    analyze_btn = st.button(
        "🔍 AI 분석",
        use_container_width=True,
        type="primary",
        key="analyze_button"
    )

if user_input and analyze_btn:
    with st.spinner("AI가 증상을 분석하고 있습니다..."):
        st.success(f"✅ 입력하신 증상: **{user_input}**")
        st.info("🤖 **AI 분석 결과**: 백엔드 API 연동 후 상세한 분석 결과가 여기에 표시됩니다.")
        
        # 분석 결과 예시 (추후 실제 데이터로 대체)
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("위험도", "중간", "⚠️")
        with col_b:
            st.metric("유사 증상", "342건", "+12")
        with col_c:
            st.metric("권장 검사", "혈당", "필수")

st.divider()

# ==================== 2. 건강 데이터 대시보드 ====================
st.markdown('<p class="section-header">📊 건강 데이터 대시보드</p>', unsafe_allow_html=True)

# 통계 카드
stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
with stat_col1:
    st.metric(
        label="평균 혈당",
        value="130 mg/dL",
        delta="-5 mg/dL",
        delta_color="inverse"
    )
with stat_col2:
    st.metric(
        label="측정 횟수",
        value="10회",
        delta="+2회"
    )
with stat_col3:
    st.metric(
        label="목표 달성률",
        value="70%",
        delta="+15%"
    )
with stat_col4:
    st.metric(
        label="위험 알림",
        value="2건",
        delta="-1건",
        delta_color="inverse"
    )

st.markdown("<br>", unsafe_allow_html=True)

# 혈당 그래프
data = [
    {"date": "10-20", "glucose": 112, "type": "정상"},
    {"date": "10-21", "glucose": 128, "type": "정상"},
    {"date": "10-22", "glucose": 135, "type": "경계"},
    {"date": "10-23", "glucose": 142, "type": "경계"},
    {"date": "10-24", "glucose": 119, "type": "정상"},
    {"date": "10-25", "glucose": 124, "type": "정상"},
    {"date": "10-26", "glucose": 138, "type": "경계"},
    {"date": "10-27", "glucose": 145, "type": "경계"},
    {"date": "10-28", "glucose": 132, "type": "경계"},
    {"date": "10-29", "glucose": 126, "type": "정상"},
]

df = pd.DataFrame(data)

# 그래프 컬럼 레이아웃
graph_col1, graph_col2 = st.columns([3, 1])

with graph_col1:
    # Seaborn 스타일 설정
    sns.set_style("whitegrid")
    sns.set_context("notebook", font_scale=1.1)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 라인 플롯
    sns.lineplot(
        data=df,
        x="date",
        y="glucose",
        marker="o",
        color="#1f77b4",
        linewidth=3,
        markersize=10,
        ax=ax
    )
    
    # 정상 범위 표시
    ax.axhspan(70, 130, alpha=0.15, color='green', label='정상 범위')
    ax.axhspan(130, 180, alpha=0.15, color='orange', label='경계 범위')
    
    ax.set_title("📈 최근 10일 혈당 추이", fontsize=20, weight="bold", pad=20)
    ax.set_xlabel("날짜", fontsize=14, weight="bold")
    ax.set_ylabel("혈당 (mg/dL)", fontsize=14, weight="bold")
    ax.tick_params(axis='x', rotation=45, labelsize=11)
    ax.tick_params(axis='y', labelsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', fontsize=10)
    
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

with graph_col2:
    st.markdown("##### 📋 데이터 요약")
    st.markdown(f"""
    **최고 혈당**: {df['glucose'].max()} mg/dL  
    **최저 혈당**: {df['glucose'].min()} mg/dL  
    **평균 혈당**: {df['glucose'].mean():.1f} mg/dL  
    **표준편차**: {df['glucose'].std():.1f}
    
    ---
    
    **정상**: {len(df[df['type']=='정상'])}회  
    **경계**: {len(df[df['type']=='경계'])}회  
    **위험**: 0회
    """)

st.divider()

# ==================== 3. 사용자 정보 관리 ====================
st.markdown('<p class="section-header">👤 건강 프로필 관리</p>', unsafe_allow_html=True)

with st.form("user_info_form", clear_on_submit=False):
    form_col1, form_col2 = st.columns(2)
    
    with form_col1:
        st.markdown("##### 📝 기본 정보")
        name = st.text_input("이름", placeholder="홍길동")
        age = st.number_input("나이", min_value=1, max_value=120, value=30, step=1)
        
        height_weight_col = st.columns(2)
        with height_weight_col[0]:
            height = st.number_input("키 (cm)", min_value=100, max_value=250, value=170, step=1)
        with height_weight_col[1]:
            weight = st.number_input("몸무게 (kg)", min_value=30, max_value=200, value=65, step=1)
        
        # BMI 자동 계산
        if height > 0 and weight > 0:
            bmi = weight / ((height / 100) ** 2)
            st.info(f"💡 BMI: {bmi:.1f} kg/m²")
    
    with form_col2:
        st.markdown("##### 🏥 건강 이력")
        
        diabetes_type = st.selectbox(
            "당뇨 유형",
            ["해당 없음", "1형 당뇨", "2형 당뇨", "임신성 당뇨", "기타"]
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        diagnose_col = st.columns([1, 2])
        with diagnose_col[0]:
            st.caption("진단 이력")
        with diagnose_col[1]:
            diagnose = st.radio(
                "진단",
                ["있음", "없음"],
                index=1,
                horizontal=True,
                label_visibility="collapsed",
                key="diagnose"
            )
        
        genetics_col = st.columns([1, 2])
        with genetics_col[0]:
            st.caption("가족력")
        with genetics_col[1]:
            genetics = st.radio(
                "가족력",
                ["있음", "없음"],
                index=1,
                horizontal=True,
                label_visibility="collapsed",
                key="genetics"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        medication = st.text_area(
            "복용 중인 약물",
            placeholder="예: 메트포르민 500mg, 하루 2회",
            height=100
        )
    
    submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
    with submit_col2:
        submitted = st.form_submit_button(
            "💾 프로필 저장",
            use_container_width=True,
            type="primary"
        )

if submitted:
    if name:
        st.balloons()
        st.success(f"""
        ✅ **{name}님의 건강 프로필이 안전하게 저장되었습니다!**
        
        **기본 정보**
        - 나이: {age}세 | 키: {height}cm | 체중: {weight}kg
        - BMI: {bmi:.1f} kg/m²
        
        **건강 이력**
        - 당뇨 유형: {diabetes_type}
        - 진단 이력: {diagnose} | 가족력: {genetics}
        - 복용 약물: {medication if medication else '없음'}
        """)
    else:
        st.error("⚠️ 이름을 입력해주세요.")

st.divider()

# ==================== 4. 추가 기능 ====================
st.markdown('<p class="section-header">⚙️ 데이터 관리</p>', unsafe_allow_html=True)

tool_col1, tool_col2, tool_col3 = st.columns(3)

with tool_col1:
    st.markdown("##### 📁 데이터 가져오기")
    uploaded_file = st.file_uploader(
        "건강 데이터 파일 업로드",
        type=['csv', 'xlsx', 'json'],
        label_visibility="collapsed",
        help="CSV, Excel, JSON 형식을 지원합니다"
    )
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name} 업로드 완료!")
        if st.button("📊 데이터 미리보기", use_container_width=True):
            st.info("파일 내용이 여기에 표시됩니다.")

with tool_col2:
    st.markdown("##### 🎯 목표 설정")
    target_glucose = st.slider(
        "목표 혈당 (mg/dL)",
        min_value=80,
        max_value=180,
        value=120,
        step=5,
        help="권장 공복 혈당: 80-130 mg/dL"
    )
    st.metric("현재 목표", f"{target_glucose} mg/dL", delta="적정 범위")
    
    if st.button("⏰ 알림 설정", use_container_width=True):
        st.info("혈당 측정 알림이 설정되었습니다!")

with tool_col3:
    st.markdown("##### 📤 데이터 내보내기")
    export_format = st.selectbox(
        "내보내기 형식",
        ["CSV", "Excel", "PDF 보고서"],
        label_visibility="collapsed"
    )
    
    date_range = st.date_input(
        "기간 선택",
        value=[],
        help="데이터를 내보낼 기간을 선택하세요"
    )
    
    if st.button("⬇️ 다운로드", use_container_width=True, type="primary"):
        st.success(f"✅ {export_format} 파일이 다운로드되었습니다!")

# ==================== 사이드바 ====================
with st.sidebar:
    st.markdown("### 🌐 설정")
    
    lang = st.selectbox(
        "언어",
        ["한국어", "English", "日本語", "中文"],
        help="인터페이스 언어를 선택하세요"
    )
    
    theme = st.selectbox(
        "테마",
        ["라이트 모드", "다크 모드", "자동"],
        help="화면 테마를 선택하세요"
    )
    
    st.markdown("---")
    
    st.markdown("### 📞 고객 지원")
    st.markdown("""
    **이메일**: support@healthmap.com  
    **전화**: 1588-1234  
    **운영시간**: 평일 09:00-18:00
    """)
    
    st.markdown("---")
    
    st.markdown("### ℹ️ 앱 정보")
    st.markdown("""
    **버전**: 1.2.0  
    **업데이트**: 2025-10-30  
    **개발자**: HealthMap Team
    """)
    
    if st.button("🔄 새로고침", use_container_width=True):
        st.rerun()
    
    if st.button("🚪 로그아웃", use_container_width=True):
        st.warning("로그아웃 기능은 개발 중입니다.")

# ==================== 푸터 ====================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #7f8c8d;'>© 2025 HealthMap. All rights reserved. | "
    "<a href='#' style='color: #3498db;'>개인정보처리방침</a> | "
    "<a href='#' style='color: #3498db;'>이용약관</a></p>",
    unsafe_allow_html=True
)
