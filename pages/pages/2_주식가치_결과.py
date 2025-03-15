import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 숫자 형식화 함수
def format_number(num):
    return f"{int(num):,}"

# 페이지 헤더
st.title("주식가치 평가 결과")

# 결과 확인
if not st.session_state.get('evaluated', False):
    st.warning("먼저 '비상장주식 평가' 페이지에서 평가를 진행해주세요.")
    if st.button("비상장주식 평가 페이지로 이동"):
        st.switch_page("pages/1_비상장주식_평가.py")
else:
    stock_value = st.session_state.stock_value
    company_name = st.session_state.company_name
    total_equity = st.session_state.total_equity
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 회사명: {company_name}")
    with col2:
        st.markdown(f"### 적용 평가방식: {stock_value['methodText']}")
    
    st.markdown("---")
    
    st.subheader("주요 계산결과")
    
    # 결과 표 생성
    results_df = pd.DataFrame({
        "항목": [
            "1주당 순자산가치", 
            "1주당 손익가치", 
            "영업권 고려 후 자산가치", 
            "최종 주당 평가액", 
            "회사 총 주식가치", 
            "대표이사 보유주식 가치"
        ],
        "금액 (원)": [
            format_number(stock_value["netAssetPerShare"]),
            format_number(stock_value["incomeValue"]),
            format_number(stock_value["assetValueWithGoodwill"]),
            format_number(stock_value["finalValue"]),
            format_number(stock_value["totalValue"]),
            format_number(stock_value["ownedValue"])
        ]
    })
    
    # 스타일링된 데이터프레임 표시
    st.dataframe(
        results_df,
        column_config={
            "항목": st.column_config.TextColumn("항목"),
            "금액 (원)": st.column_config.TextColumn("금액 (원)", width="large"),
        },
        hide_index=True,
        use_container_width=True,
        height=280
    )
    
    # 증가율 정보 표시
    st.info(f"자본총계({format_number(total_equity)}원) 대비 평가 회사가치는 **{stock_value['increasePercentage']}%**로 평가되었습니다.")
    
    # 차트 표시
    col1, col2 = st.columns(2)
    with col1:
        # 원형 차트 생성
        labels = ['순자산가치', '영업권 가치']
        values = [stock_value["netAssetPerShare"], stock_value["assetValueWithGoodwill"] - stock_value["netAssetPerShare"]]
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
        fig.update_layout(title_text='주당 가치 구성')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 막대 차트 생성
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['순자산가치', '손익가치', '최종평가액'],
            y=[stock_value["netAssetPerShare"], stock_value["incomeValue"], stock_value["finalValue"]],
            marker_color=['lightblue', 'lightgreen', 'coral']
        ))
        fig.update_layout(title_text='주요 가치 비교 (주당)')
        st.plotly_chart(fig, use_container_width=True)
    
    # 버튼 행
    col1, col2 = st.columns(2)
    with col1:
        if st.button("현시점 세금 계산하기", type="primary", use_container_width=True):
            st.switch_page("pages/3_현시점_세금계산.py")
    
    with col2:
        if st.button("미래 주식가치 계산하기", type="primary", use_container_width=True):
            st.switch_page("pages/4_미래_주식가치.py")
