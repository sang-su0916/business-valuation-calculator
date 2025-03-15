import streamlit as st

st.set_page_config(
    page_title="기업가치 약식 평가계산기",
    page_icon="💼",
    layout="wide"
)

# 페이지 이동 함수
def navigate_to(page):
    if page == "비상장주식 평가":
        st.switch_page("1_비상장주식_평가.py")
    elif page == "주식가치 결과":
        st.switch_page("2_주식가치_결과.py")
    elif page == "현시점 세금계산":
        st.switch_page("3_현시점_세금계산.py")
    elif page == "미래 주식가치":
        st.switch_page("4_미래_주식가치.py")
    elif page == "미래 세금계산":
        st.switch_page("5_미래_세금계산.py")

# 사이드바에 버튼 추가
with st.sidebar:
    st.title("메뉴")
    st.button("비상장주식 평가", on_click=navigate_to, args=("비상장주식 평가",), use_container_width=True)
    st.button("주식가치 결과", on_click=navigate_to, args=("주식가치 결과",), use_container_width=True)
    st.button("현시점 세금계산", on_click=navigate_to, args=("현시점 세금계산",), use_container_width=True)
    st.button("미래 주식가치", on_click=navigate_to, args=("미래 주식가치",), use_container_width=True)
    st.button("미래 세금계산", on_click=navigate_to, args=("미래 세금계산",), use_container_width=True)

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

st.info("왼쪽 사이드바의 버튼을 클릭하여 원하는 메뉴로 이동하세요.")
