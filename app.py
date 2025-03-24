import streamlit as st

st.set_page_config(
    page_title="기업가치 약식 평가계산기",
    page_icon="💼",
    layout="wide"
)

# 사이드바 스타일 커스터마이징
st.markdown("""
<style>
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    span.css-10trblm.e16nr0p30 {
        color: #262730;
        font-weight: bold;
    }
    section[data-testid="stSidebar"] div.element-container div.stButton button {
        background-color: #ffffff;
        color: #262730;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px 15px;
        width: 100%;
        text-align: center;
        margin-bottom: 10px;
        font-weight: bold;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    section[data-testid="stSidebar"] div.element-container div.stButton button:hover {
        background-color: #f8f9fa;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
    }
    [data-testid="stSidebarNav"] {
        background-color: #f0f2f6;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    [data-testid="stSidebarNav"] ul {
        padding-left: 20px;
    }
    [data-testid="stSidebarNav"] li {
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 메인 콘텐츠
st.title("기업가치 약식 평가계산기")
st.markdown("상속세 및 증여세법에 따른 비상장주식 평가와 세금 계산")
st.markdown("---")

st.markdown("""
## 안내

이 앱은 비상장주식의 가치평가와 세금 계산을 도와주는 도구입니다.

### 사용 방법
왼쪽 사이드바에서 원하는 기능을 선택하세요:

1. **비상장주식 평가**: 회사 정보와 재무 데이터를 입력하여 주식 가치를 평가합니다.
2. **주식가치 결과**: 평가된 주식 가치 결과를 확인합니다.
3. **현시점 세금계산**: 평가된 주식에 대한 상속세, 증여세, 양도소득세 등을 계산합니다.
4. **미래 주식가치**: 성장률을 적용하여 미래 시점의 주식 가치를 예측합니다.
5. **미래 세금계산**: 미래 시점의 예상 세금을 계산합니다.

### 참고사항
- 이 계산기는 참고용으로만 사용하시고, 정확한 세금 계산을 위해서는 전문가와 상담하시기 바랍니다.
- 상속세 및 증여세법 시행령 제54조에 근거한 계산 방식을 사용합니다.
""")

st.info("왼쪽 사이드바의 페이지 목록에서 원하는 메뉴를 선택하세요.")
