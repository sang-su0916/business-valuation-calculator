import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 숫자 형식화 함수
def format_number(num):
    return f"{int(num):,}"

# 미래 주식가치 계산 함수
def calculate_future_stock_value(stock_value, total_equity, shares, owned_shares, 
                               interest_rate, evaluation_method, growth_rate, future_years):
    if not stock_value:
        return None
    
    # 복리 성장률 적용
    growth_factor = (1 + (growth_rate / 100)) ** future_years
    
    # 미래 자산 및 수익 계산
    future_total_equity = total_equity * growth_factor
    future_weighted_income = stock_value["weightedIncome"] * growth_factor
    
    # 1. 순자산가치 계산
    net_asset_per_share = future_total_equity / shares
    
    # 2. 영업권 계산
    weighted_income_per_share = future_weighted_income / shares
    weighted_income_per_share_50 = weighted_income_per_share * 0.5
    equity_return = (future_total_equity * (interest_rate / 100)) / shares
    annuity_factor = 3.7908
    goodwill = max(0, (weighted_income_per_share_50 - equity_return) * annuity_factor)
    
    # 3. 순자산가치 + 영업권
    asset_value_with_goodwill = net_asset_per_share + goodwill
    
    # 4. 손익가치 계산
    income_value = weighted_income_per_share * (100 / interest_rate)
    
    # 5. 최종가치 계산
    if evaluation_method == "부동산 과다법인":
        # 부동산 과다법인
        stock_value_calc = (asset_value_with_goodwill * 0.6) + (income_value * 0.4)
        net_asset_80_percent = net_asset_per_share * 0.8
        final_value = max(stock_value_calc, net_asset_80_percent)
        method_text = '부동산 과다법인: (자산가치×0.6 + 수익가치×0.4)'
    elif evaluation_method == "순자산가치만 평가":
        # 순자산가치만 적용
        final_value = net_asset_per_share
        method_text = '순자산가치만 평가'
    else:
        # 일반법인
        stock_value_calc = (income_value * 0.6) + (asset_value_with_goodwill * 0.4)
        net_asset_80_percent = net_asset_per_share * 0.8
        final_value = max(stock_value_calc, net_asset_80_percent)
        method_text = '일반법인: (수익가치×0.6 + 자산가치×0.4)'
    
    # 총 가치
    total_value = final_value * shares
    owned_value = final_value * owned_shares
    
    return {
        "netAssetPerShare": net_asset_per_share,
        "assetValueWithGoodwill": asset_value_with_goodwill,
        "incomeValue": income_value,
        "finalValue": final_value,
        "totalValue": total_value,
        "ownedValue": owned_value,
        "methodText": method_text,
        "futureTotalEquity": future_total_equity,
        "futureWeightedIncome": future_weighted_income,
        "growthRate": growth_rate,
        "futureYears": future_years
    }

# 페이지 헤더
st.title("미래 주식가치 예측")

if not st.session_state.get('evaluated', False):
    st.warning("먼저 '비상장주식 평가' 페이지에서 평가를 진행해주세요.")
    if st.button("비상장주식 평가 페이지로 이동"):
        st.switch_page("pages/1_비상장주식_평가.py")
else:
    stock_value = st.session_state.stock_value
    company_name = st.session_state.company_name
    total_equity = st.session_state.total_equity
    shares = st.session_state.shares
    owned_shares = st.session_state.owned_shares
    interest_rate = st.session_state.interest_rate
    evaluation_method = st.session_state.evaluation_method
    
    with st.expander("현재 주식 가치", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**회사명:** {company_name}")
            st.markdown(f"**주당 평가액:** {format_number(stock_value['finalValue'])}원")
        with col2:
            st.markdown(f"**회사 총가치:** {format_number(stock_value['totalValue'])}원")
            st.markdown(f"**적용 평가방식:** {stock_value['methodText']}")
    
    st.markdown("---")
    
    st.subheader("미래 가치 계산 입력")
    
    col1, col2 = st.columns(2)
    
    with col1:
        growth_rate = st.selectbox(
            "연평균 성장률 (%)",
            [5, 10, 15, 20, 25, 30],
            index=1,  # 기본값 10%
            help="회사의 연평균 성장률 예상치"
        )
    
    with col2:
        future_years = st.selectbox(
            "예측 기간 (년)",
            [5, 10, 15, 20, 30],
            index=1,  # 기본값 10년
            help="미래 시점 선택"
        )
    
    if 'future_stock_value' not in st.session_state:
        st.session_state.future_stock_value = None
    if 'future_evaluated' not in st.session_state:
        st.session_state.future_evaluated = False
    
    # 계산 버튼
    if st.button("미래 가치 계산하기", type="primary", use_container_width=True):
        with st.spinner("계산 중..."):
            # 미래 주식 가치 계산
            st.session_state.future_stock_value = calculate_future_stock_value(
                stock_value, total_equity, shares, owned_shares, 
                interest_rate, evaluation_method, growth_rate, future_years
            )
            st.session_state.future_evaluated = True
            
            st.success("계산이 완료되었습니다.")
            st.balloons()
    
    # 미래 가치 결과 표시
    if st.session_state.future_evaluated and st.session_state.future_stock_value:
        future_stock_value = st.session_state.future_stock_value
        
        st.markdown("---")
        st.subheader("미래 주식가치 평가 결과")
        
        # 정보 표시
        st.markdown(f"**예측 기간:** {future_years}년")
        st.markdown(f"**적용 성장률:** 연 {growth_rate}%")
        
        # 결과 표 생성
        results_df = pd.DataFrame({
            "항목": [
                "미래 자본총계", 
                "1주당 순자산가치", 
                "1주당 손익가치", 
                "미래 주당 평가액", 
                "미래 회사 총 주식가치", 
                "미래 대표이사 보유주식 가치"
            ],
            "금액 (원)": [
                format_number(future_stock_value["futureTotalEquity"]),
                format_number(future_stock_value["netAssetPerShare"]),
                format_number(future_stock_value["incomeValue"]),
                format_number(future_stock_value["finalValue"]),
                format_number(future_stock_value["totalValue"]),
                format_number(future_stock_value["ownedValue"])
            ]
        })
        
        st.dataframe(
            results_df,
            column_config={
                "항목": st.column_config.TextColumn("항목"),
                "금액 (원)": st.column_config.TextColumn("금액 (원)", width="large"),
            },
            hide_index=True,
            use_container_width=True,
            height=250
        )
        
        # 증가율 정보 표시
        value_increase = (future_stock_value["finalValue"] / stock_value["finalValue"] - 1) * 100
        st.info(f"현재 주당 가치({format_number(stock_value['finalValue'])}원) 대비 **{value_increase:.1f}%** 증가했습니다.")
        
        # 차트 표시 - 현재와 미래 가치 비교
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['현재', '미래'],
            y=[stock_value["finalValue"], future_stock_value["finalValue"]],
            marker_color=['lightblue', 'orange'],
            text=[format_number(stock_value["finalValue"]), format_number(future_stock_value["finalValue"])],
            textposition='auto'
        ))
        fig.update_layout(title_text='주당 가치 비교')
        st.plotly_chart(fig, use_container_width=True)
        
        # 버튼
        if st.button("미래 세금 계산하기", type="primary", use_container_width=True):
            st.switch_page("pages/5_미래_세금계산.py")
