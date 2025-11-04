import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# > static폴더로 분리
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)


# 페이지 제목
st.markdown('<p class="main-header">🏥 HealthMap</p>', unsafe_allow_html=True)

# ========== 1. 증상 입력 섹션 ==========
st.markdown('<p class="section-header">💬 증상 입력</p>', unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])
with col1:
    user_input = st.text_input("", placeholder="예: 두통이 심해요", label_visibility="collapsed")
with col2:
    analyze_btn = st.button("🔍 분석하기", use_container_width=True, type="primary")

if user_input and analyze_btn:
    st.success(f"✅ 입력하신 증상: {user_input}")
    st.info("🤖 백엔드 연동 후 AI 분석 결과가 여기에 표시됩니다.")

st.divider()

# ========== 2. 혈당 트렌드 그래프 ==========
st.markdown('<p class="section-header">📊 건강 데이터 시각화</p>', unsafe_allow_html=True)

# 샘플 데이터
data = [
    {"date": "10-20", "glucose": 112},
    {"date": "10-21", "glucose": 128},
    {"date": "10-22", "glucose": 135},
    {"date": "10-23", "glucose": 142},
    {"date": "10-24", "glucose": 119},
    {"date": "10-25", "glucose": 124},
    {"date": "10-26", "glucose": 138},
    {"date": "10-27", "glucose": 145},
    {"date": "10-28", "glucose": 132},
    {"date": "10-29", "glucose": 126},
]

df = pd.DataFrame(data)
sns.set_style("whitegrid")

# 그래프 생성
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=df, x="date", y="glucose", marker="o", 
                 color=sns.color_palette("crest")[4], linewidth=2.5, markersize=8, ax=ax)
    
    ax.set_title("📈 최근 10일 혈당 추이", fontsize=18, weight="bold", pad=20)
    ax.set_xlabel("날짜", fontsize=12, weight="bold")
    ax.set_ylabel("혈당 (mg/dL)", fontsize=12, weight="bold")
    ax.tick_params(axis='x', rotation=45, labelsize=10)
    ax.tick_params(axis='y', labelsize=10)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    
    st.pyplot(fig, use_container_width=True)

st.divider()

# ========== 3. 사용자 정보 입력 폼 ==========
st.markdown('<p class="section-header">👤 사용자 정보</p>', unsafe_allow_html=True)

with st.form("user_info_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 기본 정보")
        name = st.text_input("이름", placeholder="홍길동")
        age = st.number_input("나이", min_value=0, max_value=120, value=25, step=1)
        height = st.number_input("키 (cm)", min_value=100, max_value=250, value=170, step=1)
        weight = st.number_input("몸무게 (kg)", min_value=30, max_value=200, value=65, step=1)
    
    with col2:
        st.markdown("##### 건강 이력")
        st.caption("당뇨병 진단 이력이 있나요?")
        diagnose = st.radio("진단 이력", ["있음", "없음"], index=1, horizontal=True, label_visibility="collapsed")
        
        st.caption("당뇨병 가족력이 있나요?")
        genetics = st.radio("가족력", ["있음", "없음"], index=1, horizontal=True, label_visibility="collapsed")
        
        diabetes_type = st.selectbox("당뇨 유형", ["선택 안 함", "1형", "2형", "임신성"])
    
    submitted = st.form_submit_button("📝 정보 저장", use_container_width=True, type="primary")

if submitted:
    if name:
        st.success(f"""
        ✅ **{name}님의 정보가 저장되었습니다!**
        - 나이: {age}세
        - 키: {height}cm
        - 체중: {weight}kg
        - 진단 이력: {diagnose}
        - 가족력: {genetics}
        - 당뇨 유형: {diabetes_type}
        """)
    else:
        st.error("⚠️ 이름을 입력해주세요.")

st.divider()

# ========== 4. 추가 기능 ==========
st.markdown('<p class="section-header">⚙️ 추가 기능</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("##### 📁 파일 업로드")
    uploaded_file = st.file_uploader("건강 데이터 파일", type=['csv', 'xlsx'], label_visibility="collapsed")
    if uploaded_file:
        st.success("✅ 파일이 업로드되었습니다!")

with col2:
    st.markdown("##### 🎯 혈당 목표 설정")
    target_glucose = st.slider("목표 혈당 (mg/dL)", min_value=80, max_value=180, value=120, step=5)
    st.info(f"목표: {target_glucose} mg/dL")

with col3:
    st.markdown("##### 📋 데이터 필터")
    data_filter = st.multiselect("표시할 데이터", ["혈당", "혈압", "체중", "운동량"], default=["혈당"])




# 사이드바
with st.sidebar:
    st.markdown("### 🌐 언어 설정")
    lang = st.selectbox("언어 선택", ["한국어", "English", "日本語"])
    
    st.markdown("### ℹ️ 버전 정보")
    st.text("MyHealthMap v1.0")
