import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# 페이지 제목 및 채팅창
st.set_page_config(page_title="MyHealthMap", layout="wide", page_icon="🏥")
st.title("MyHealthMap")
user_input = st.text_input("증상을 입력하세요", placeholder="예: 두통이 심해요")

if user_input:
    st.success(f"입력하신 증상: {user_input}")
    st.info("백엔드 연동 후 AI 분석 결과가 여기에 표시됩니다.")



# 더미 데이터
data = [
    {"date": "25-10-20", "glucose": 112},
    {"date": "25-10-21", "glucose": 128},
    {"date": "25-10-22", "glucose": 135},
    {"date": "25-10-23", "glucose": 142},
    {"date": "25-10-24", "glucose": 119},
    {"date": "25-10-25", "glucose": 124},
    {"date": "25-10-26", "glucose": 138},
    {"date": "25-10-27", "glucose": 145},
    {"date": "25-10-28", "glucose": 132},
    {"date": "25-10-29", "glucose": 126},
]

# 혈당 추이 그래프
df = pd.DataFrame(data)                                  # pd.read_sql()
sns.set(style="whitegrid", context="paper")              # context는 talk → paper로 변경
fig, ax = plt.subplots(figsize=(4, 2))
sns.lineplot(data=df, x="date", y="glucose", marker="o", hue = None, color=sns.color_palette("crest")[4], ax=ax)
ax.set_title("📈10-day-bloodsugar-trend", fontsize=16, weight="bold")
ax.set_xlabel("날짜")
ax.set_ylabel("혈당(mg/dL)")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig, use_container_width=False)


# # 마크다운(http) 추가
# st.markdown("""
#     <style>
#     .element-container:nth-child(1) > div > div > div > div {
#         width: 400px !important;
#     }
#     </style>
#     """, unsafe_allow_html=True)

# # st랑 같이 쓰는거라 plt.show() 대신 fig를 st.에서 화면에 표시
# st.pyplot(fig, use_container_width=False)



# 요소(element)
st.button("클릭")
st.multiselect("선택", ["1형", "2형", "임신성"])
st.slider("값 조절", min_value=1, max_value=200, value=None, step=1)
st.file_uploader("파일 업로드 (의무기록지 등)")
# st.number_input("숫자 입력")
# st.text_input("텍스트 입력")
# st.text_area("여러 줄 입력")   
# st.date_input("날짜")
# st.time_input("시간")
# st.color_picker("색상 선택")



# 1️⃣ 폼 정의
# : 나이 신장 체중 당뇨진단이력 가족력
with st.form("my_form"):
    name = st.text_input("이름을 입력하세요")
    age = st.number_input("나이", 0, 100, 25)
    height = st.number_input("키(cm)를 입력하세요")#, min_value=100, max_value=220, value=None, step=1)
    weight = st.number_input("몸무게(kg)를 입력하세요")
    st.caption("당뇨병 진단이력이 있나요?")
    diagnose = st.radio("선택", ["있음", "없음"], index=None, key="diagnose")
    st.caption("당뇨병 가족력이 있나요?")
    genetics = st.radio("선택", ["있음", "없음"], index=None, key="genetics")
    lang = st.sidebar.selectbox("언어 선택", ["Python", "Java", "Kotlin"])
    submitted = st.form_submit_button("제출")

# 2️⃣ 제출 버튼을
if submitted:
    st.success(f"{name}님, 나이 {age}세, 키 {height}cm, 체중 {weight}kg, 진단이력 {diagnose}, 가족력 {genetics}으로 입력되었습니다✅")
