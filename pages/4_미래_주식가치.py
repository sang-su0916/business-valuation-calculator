import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import locale
from datetime import datetime

# 숫자 형식화를 위한 로케일 설정
try:
    locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'ko_KR')
    except:
        locale.setlocale(locale.LC_ALL, '')

# 숫자 형식화 함수
def format_number(num):
    try:
        return "{:,}".format(int(num))
    except:
        return str(num)

# CSS 스타일 추가
st.markdown("""
<style>
    .info-box {
        background-color: #f0f7fb;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
        color: #0c5460;
    }
    .growth-panel {
        background-color: #fff8e1;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
        border-left: 4px solid #ffc107;
    }
    .sidebar-guide {
        background-color: #e8f4f8;
        padding: 10px 15px;
        border-radius: 5px;
        margin-top: 10px;
        font-size: 0.9em;
        border-left: 3px solid #4dabf7;
    }
    .result-highlight {
        font-size: 24px;
        font-weight: bold;
        color: #333;
        margin: 10px 0;
    }
    .percentage-up {
        color: #28a745;
        font-weight: bold;
    }
    .chart-container {
        margin-top: 20px;
        margin-bottom: 30px;
    }
    .explanation-text {
        font-size: 0.95em;
        color: #555;
        margin: 15px 0;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

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
    st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>비상장주식 평가</b> 메뉴를 클릭하여 평가를 먼저 진행하세요.</div>", unsafe_allow_html=True)
else:
    stock_value = st.session_state.stock_value
    company_name = st.session_state.company_name
    total_equity = st.session_state.total_equity
    shares = st.session_state.shares
    owned_shares = st.session_state.owned_shares
    interest_rate = st.session_state.interest_rate
    evaluation_method = st.session_state.evaluation_method
    eval_date = st.session_state.get('eval_date', None)
    
    # 현재 주식 가치 정보 표시
    with st.expander("현재 주식 가치", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**회사명:** {company_name}")
            st.markdown(f"**주당 평가액:** {format_number(stock_value['finalValue'])}원")
        with col2:
            st.markdown(f"**회사 총가치:** {format_number(stock_value['totalValue'])}원")
            st.markdown(f"**적용 평가방식:** {stock_value['methodText']}")
        
        if eval_date:
            st.markdown(f"**평가 기준일:** {eval_date.strftime('%Y년 %m월 %d일')}")
    
    # 미래 가치 예측 설명
    st.markdown("""
    <div class="explanation-text">
        <p>기업 가치는 시간이 지남에 따라 성장할 수 있습니다. 이 페이지에서는 회사의 예상 성장률을 적용하여 
        미래 시점의 주식 가치를 예측합니다. 성장률과 예측 기간을 선택하면 현재 가치를 기준으로 
        미래 가치를 계산합니다.</p>
        <p>계산된 미래 가치는 현재 가치와 함께 비교 차트로 표시되며, 성장에 따른 가치 증가율도 확인할 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("미래 가치 계산 입력")
    
    # 성장률 및 예측 기간 선택
    with st.container():
        st.markdown("<div class='growth-panel'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            growth_rate = st.selectbox(
                "연평균 성장률 (%)",
                [5, 10, 15, 20, 25, 30],
                index=1,  # 기본값 10%
                help="회사의 연평균 성장률 예상치입니다. 과거 실적과 미래 전망을 고려하여 선택하세요."
            )
            st.markdown(f"<small>선택한 성장률 {growth_rate}%는 매년 복리로 적용됩니다.</small>", unsafe_allow_html=True)
        
        with col2:
            future_years = st.selectbox(
                "예측 기간 (년)",
                [5, 10, 15, 20, 30],
                index=1,  # 기본값 10년
                help="미래 가치를 예측할 기간을 선택하세요."
            )
            target_year = datetime.now().year + future_years
            st.markdown(f"<small>{target_year}년 기준으로 예측합니다.</small>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
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
        
        # 예측 요약 정보
        target_year = datetime.now().year + future_years
        st.markdown(f"""
        <div class="info-box">
            <h4>예측 정보 요약</h4>
            <ul>
                <li><b>기준 시점:</b> {datetime.now().year}년</li>
                <li><b>예측 시점:</b> {target_year}년 ({future_years}년 후)</li>
                <li><b>적용 성장률:</b> 연 {growth_rate}% (복리)</li>
                <li><b>적용 평가방식:</b> {future_stock_value['methodText']}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 현재 vs 미래 가치 비교 표시
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div style='text-align: center;'><h4>현재 가치</h4></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='result-highlight' style='text-align: center;'>{format_number(stock_value['finalValue'])}원/주</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center;'>회사 총가치: {format_number(stock_value['totalValue'])}원</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div style='text-align: center;'><h4>미래 가치</h4></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='result-highlight' style='text-align: center;'>{format_number(future_stock_value['finalValue'])}원/주</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center;'>회사 총가치: {format_number(future_stock_value['totalValue'])}원</div>", unsafe_allow_html=True)
        
        # 증가율 정보 표시
        value_increase = (future_stock_value["finalValue"] / stock_value["finalValue"] - 1) * 100
        st.markdown(f"""
        <div style='text-align: center; margin: 20px 0;'>
            <span style='font-size: 18px;'>예상 가치 증가율: </span>
            <span class='percentage-up' style='font-size: 24px;'>+{value_increase:.1f}%</span>
            <span style='font-size: 18px;'> ({future_years}년 후)</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 차트 표시 - 현재와 미래 가치 비교
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['현재', f'{future_years}년 후'],
            y=[stock_value["finalValue"], future_stock_value["finalValue"]],
            marker_color=['lightblue', 'orange'],
            text=[format_number(stock_value["finalValue"]), format_number(future_stock_value["finalValue"])],
            textposition='auto'
        ))
        fig.update_layout(
            title='주당 가치 비교',
            yaxis_title='주당 가치 (원)',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 성장 세부 내역
        with st.expander("미래 가치 계산 세부내역", expanded=False):
            details_df = pd.DataFrame({
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
                details_df,
                column_config={
                    "항목": st.column_config.TextColumn("항목"),
                    "금액 (원)": st.column_config.TextColumn("금액 (원)", width="large"),
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.markdown("""
            <div class="explanation-text">
                <p><b>계산 방법 설명:</b></p>
                <ol>
                    <li>선택한 연평균 성장률을 복리로 적용하여 미래 자본총계와 가중평균 당기순이익을 계산합니다.</li>
                    <li>계산된 미래 자산과 수익을 기반으로 비상장주식 평가방법을 적용합니다.</li>
                    <li>적용된 평가방법에 따라 최종 주당 가치와 회사 총가치를 산출합니다.</li>
                </ol>
                <p>이 예측은 선택한 성장률이 일정하게 유지된다는 가정 하에 계산됩니다. 실제 기업 성장은 다양한 요인에 따라 변동될 수 있습니다.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 미래 세금 계산 버튼
        if st.button("미래 세금 계산하기", type="primary", use_container_width=True):
            try:
                st.switch_page("5_미래_세금계산.py")
            except:
                st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>미래 세금계산</b> 메뉴를 클릭하여 이동하세요.</div>", unsafe_allow_html=True)
