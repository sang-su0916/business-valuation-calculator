import streamlit as st
import pandas as pd
import locale
import numpy as np

# 숫자 형식화를 위한 로케일 설정
try:
    locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'ko_KR')
    except:
        locale.setlocale(locale.LC_ALL, '')

# 숫자 형식화 함수 - 천원 단위로 표시
def format_number(num):
    try:
        if num >= 1000000:  # 백만원 이상은 천원 단위로 표시
            return f"{num/1000:,.0f}천원"
        else:
            return f"{num:,}원"
    except:
        return str(num)

# 원본 숫자 형식화 함수 (원 단위)
def format_original(num):
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
    .result-card {
        background-color: #ffffff;
        border-radius: 5px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .tax-amount {
        font-size: 28px;
        font-weight: bold;
        color: #333;
        margin: 10px 0;
    }
    .tax-rate {
        color: #28a745;
        font-weight: bold;
    }
    .sidebar-guide {
        background-color: #e8f4f8;
        padding: 10px 15px;
        border-radius: 5px;
        margin-top: 10px;
        font-size: 0.9em;
        border-left: 3px solid #4dabf7;
    }
    .warning-note {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px 15px;
        border-radius: 5px;
        margin-top: 20px;
        border-left: 3px solid #ffc107;
    }
    .comparison-table {
        width: 100%;
        margin: 20px 0;
        border-collapse: collapse;
    }
    .comparison-table th {
        background-color: #f8f9fa;
        padding: 8px;
        text-align: left;
    }
    .comparison-table td {
        padding: 8px;
        border-top: 1px solid #dee2e6;
    }
    .future-indicator {
        color: #007bff;
        font-weight: bold;
    }
    .rate-info {
        font-size: 0.9em;
        color: #666;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# 페이지 헤더
st.title("미래 세금 계산")

# 상속증여세 계산 함수 (누진세율 적용)
def calculate_inheritance_tax(value):
    # 상속증여세 누진세율 적용
    tax_brackets = [
        (100000000, 0.1),       # 1억 이하: 10%
        (500000000, 0.2),       # 1억 초과 5억 이하: 20%
        (1000000000, 0.3),      # 5억 초과 10억 이하: 30%
        (3000000000, 0.4),      # 10억 초과 30억 이하: 40%
        (float('inf'), 0.5)     # 30억 초과: 50%
    ]
    
    tax = 0
    remaining = value
    prev_limit = 0
    
    for limit, rate in tax_brackets:
        if remaining > 0:
            taxable = min(remaining, limit - prev_limit)
            tax += taxable * rate
            remaining -= taxable
            prev_limit = limit
            if remaining <= 0:
                break
    
    return tax

# 양도소득세 계산 함수 (누진세율 적용)
def calculate_transfer_tax(gain):
    # 기본공제 250만원 적용
    taxable_gain = max(0, gain - 2500000)
    
    # 3억 이하: 22%, 3억 초과: 27.5%
    if taxable_gain <= 300000000:
        tax = taxable_gain * 0.22
    else:
        tax = 300000000 * 0.22 + (taxable_gain - 300000000) * 0.275
    
    return tax

# 청산소득세 계산 함수 (법인세 + 배당소득세)
def calculate_liquidation_tax(income):
    # 법인세 누진세율 적용
    corporate_tax = 0
    
    if income <= 200000000:  # 2억 이하
        corporate_tax = income * 0.1
    elif income <= 20000000000:  # 2억 초과 200억 이하
        corporate_tax = 200000000 * 0.1 + (income - 200000000) * 0.2
    elif income <= 300000000000:  # 200억 초과 3000억 이하
        corporate_tax = 200000000 * 0.1 + (20000000000 - 200000000) * 0.2 + (income - 20000000000) * 0.22
    else:  # 3000억 초과
        corporate_tax = 200000000 * 0.1 + (20000000000 - 200000000) * 0.2 + (300000000000 - 20000000000) * 0.22 + (income - 300000000000) * 0.25
    
    # 배당소득세 계산
    after_tax = income - corporate_tax
    dividend_tax = after_tax * 0.154
    
    return corporate_tax, dividend_tax, corporate_tax + dividend_tax

# 세금 계산 함수
def calculate_tax_details(value, owned_shares, share_price):
    if not value:
        return None
    
    owned_value = value["ownedValue"]
    
    # 상속증여세 (누진세율 적용)
    inheritance_tax = calculate_inheritance_tax(owned_value)
    
    # 양도소득세 (누진세율 적용)
    acquisition_value = owned_shares * share_price
    transfer_profit = owned_value - acquisition_value
    transfer_tax = calculate_transfer_tax(transfer_profit)
    
    # 청산소득세 계산 (법인세 + 배당소득세)
    corporate_tax, dividend_tax, total_liquidation_tax = calculate_liquidation_tax(owned_value)
    
    return {
        "inheritanceTax": inheritance_tax,
        "transferTax": transfer_tax,
        "corporateTax": corporate_tax,
        "liquidationTax": dividend_tax,
        "acquisitionValue": acquisition_value,
        "transferProfit": transfer_profit,
        "totalTax": total_liquidation_tax
    }

if not st.session_state.get('future_evaluated', False):
    st.warning("먼저 '미래 주식가치' 페이지에서 평가를 진행해주세요.")
    st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>미래 주식가치</b> 메뉴를 클릭하여 미래 주식가치 평가를 먼저 진행하세요.</div>", unsafe_allow_html=True)
else:
    future_stock_value = st.session_state.future_stock_value
    stock_value = st.session_state.stock_value
    company_name = st.session_state.company_name
    owned_shares = st.session_state.owned_shares
    share_price = st.session_state.share_price
    growth_rate = future_stock_value["growthRate"]
    future_years = future_stock_value["futureYears"]
    
    # 세금 계산
    future_tax_details = calculate_tax_details(future_stock_value, owned_shares, share_price)
    current_tax_details = calculate_tax_details(stock_value, owned_shares, share_price)
    
    # 예측 정보 요약
    target_year = 2025 + future_years  # 현재 연도 + 미래 예측 연도
    
    st.markdown(f"""
    <div class="info-box">
        <h4>미래 세금 계산 정보</h4>
        <p>현재 가치와 예측된 미래 가치에 기반한 세금을 비교합니다.</p>
        <ul>
            <li><b>기준 시점:</b> 2025년</li>
            <li><b>예측 시점:</b> {target_year}년 ({future_years}년 후)</li>
            <li><b>적용 성장률:</b> 연 {growth_rate}% (복리)</li>
        </ul>
        <p>※ 미래 세금은 현행 세법을 기준으로 계산되었으며, 향후 세법 변경에 따라 달라질 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 평가된 주식 가치 정보
    with st.expander("미래 주식 가치", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**회사명:** {company_name}")
            st.markdown(f"**예측 기간:** {future_years}년")
            st.markdown(f"**적용 성장률:** 연 {growth_rate}%")
        
        with col2:
            st.markdown(f"**미래 주당 평가액:** {format_number(future_stock_value['finalValue'])}")
            st.markdown(f"**미래 회사 총가치:** {format_number(future_stock_value['totalValue'])}")
            st.markdown(f"**미래 대표이사 보유주식 가치:** {format_number(future_stock_value['ownedValue'])}")
    
    # 세금 계산 결과 설명
    st.markdown("""
    <div class="info-box">
        <h4>세금 계산 결과 안내</h4>
        <p>비상장주식의 미래 가치를 바탕으로 세 가지 경우에 대한 세금을 계산했습니다:</p>
        <ul>
            <li><b>증여세</b>: 미래 시점에 주식을 증여하는 경우 적용되는 세금 (누진세율 적용)</li>
            <li><b>양도소득세</b>: 미래 시점에 주식을 매각할 때 발생하는 세금 (3억 기준 세율 구분)</li>
            <li><b>청산소득세</b>: 미래 시점에 법인을 청산할 때 지분 가치에 대한 세금 (법인세 + 배당소득세)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 세금 계산 결과 - 현재와 미래 비교
    st.subheader("현재 vs 미래 세금 비교")
    
    # 현재/미래 세금 비교 테이블
    comparison_data = [
        ["증여세 (누진세율)", format_number(current_tax_details['inheritanceTax']), format_number(future_tax_details['inheritanceTax'])],
        ["양도소득세 (22%~27.5%)", format_number(current_tax_details['transferTax']), format_number(future_tax_details['transferTax'])],
        ["청산소득세 (법인세+배당세)", format_number(current_tax_details['totalTax']), format_number(future_tax_details['totalTax'])]
    ]
    
    st.markdown("""
    <table class="comparison-table">
        <thead>
            <tr>
                <th>세금 유형</th>
                <th>현재 (2025년)</th>
                <th>미래</th>
            </tr>
        </thead>
        <tbody>
    """, unsafe_allow_html=True)
    
    for row in comparison_data:
        st.markdown(f"""
        <tr>
            <td>{row[0]}</td>
            <td>{row[1]}</td>
            <td class="future-indicator">{row[2]}</td>
        </tr>
        """, unsafe_allow_html=True)
    
    st.markdown("</tbody></table>", unsafe_allow_html=True)
    
    # 세율 정보 표시
    st.markdown("""
    <div class="rate-info">
        <p><b>적용 세율 정보:</b></p>
        <ul>
            <li><b>증여세</b>: 1억 이하 10%, 1억~5억 20%, 5억~10억 30%, 10억~30억 40%, 30억 초과 50% (누진세율)</li>
            <li><b>양도소득세</b>: 3억 이하 22%, 3억 초과 27.5% (기본공제 250만원 적용)</li>
            <li><b>법인세</b>: 2억 이하 10%, 2억~200억 20%, 200억~3000억 22%, 3000억 초과 25% (배당소득세 15.4% 추가)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 세금 증가율 표시
    inheritance_increase = (future_tax_details['inheritanceTax'] / current_tax_details['inheritanceTax'] - 1) * 100
    transfer_increase = (future_tax_details['transferTax'] / current_tax_details['transferTax'] - 1) * 100
    liquidation_increase = (future_tax_details['totalTax'] / current_tax_details['totalTax'] - 1) * 100
    
    st.markdown(f"""
    <div class="info-box">
        <h4>세금 증가 예상</h4>
        <ul>
            <li><b>증여세:</b> <span class="future-indicator">+{inheritance_increase:.1f}%</span> 증가</li>
            <li><b>양도소득세:</b> <span class="future-indicator">+{transfer_increase:.1f}%</span> 증가</li>
            <li><b>청산소득세:</b> <span class="future-indicator">+{liquidation_increase:.1f}%</span> 증가</li>
        </ul>
        <p>기업 가치의 성장에 따라 세금 부담도 증가합니다. 누진세율이 적용되는 증여세의 경우 가치 증가 비율보다 세금 증가 비율이 더 높을 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 세금 최적화 조언
    current_min_tax = min(current_tax_details['inheritanceTax'], current_tax_details['transferTax'], current_tax_details['totalTax'])
    future_min_tax = min(future_tax_details['inheritanceTax'], future_tax_details['transferTax'], future_tax_details['totalTax'])
    
    current_best_option = ""
    if current_min_tax == current_tax_details['inheritanceTax']:
        current_best_option = "증여세"
    elif current_min_tax == current_tax_details['transferTax']:
        current_best_option = "양도소득세"
    else:
        current_best_option = "청산소득세"
        
    future_best_option = ""
    if future_min_tax == future_tax_details['inheritanceTax']:
        future_best_option = "증여세"
    elif future_min_tax == future_tax_details['transferTax']:
        future_best_option = "양도소득세"
    else:
        future_best_option = "청산소득세"
    
    st.markdown(f"""
    <div class="info-box">
        <h4>세금 최적화 참고사항</h4>
        <ul>
            <li>현재 기준으로는 <b>{current_best_option}</b>가 세금 부담이 가장 적습니다.</li>
            <li>미래({future_years}년 후) 기준으로는 <b>{future_best_option}</b>가 세금 부담이 가장 적을 것으로 예상됩니다.</li>
        </ul>
        <p>주의: 이는 단순 세율 비교이며, 실제 세금 계획은 개인 상황, 자산 구성, 사업 목적 등을 고려해 전문가와 상담해야 합니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 세부 내역
    with st.expander("미래 세금 계산 세부내역", expanded=False):
        details_df = pd.DataFrame({
            "항목": [
                "증여세 과세표준", 
                "양도소득 취득가액", 
                "양도소득 차익", 
                "법인세 과세표준", 
                "법인세액", 
                "배당소득", 
                "배당소득세"
            ],
            "현재 금액": [
                format_original(stock_value["ownedValue"]),
                format_original(current_tax_details["acquisitionValue"]),
                format_original(current_tax_details["transferProfit"]),
                format_original(stock_value["ownedValue"]),
                format_original(current_tax_details["corporateTax"]),
                format_original(stock_value["ownedValue"] - current_tax_details["corporateTax"]),
                format_original(current_tax_details["liquidationTax"])
            ],
            "미래 금액": [
                format_original(future_stock_value["ownedValue"]),
                format_original(future_tax_details["acquisitionValue"]),
                format_original(future_tax_details["transferProfit"]),
                format_original(future_stock_value["ownedValue"]),
                format_original(future_tax_details["corporateTax"]),
                format_original(future_stock_value["ownedValue"] - future_tax_details["corporateTax"]),
                format_original(future_tax_details["liquidationTax"])
            ]
        })
        
        st.dataframe(
            details_df,
            column_config={
                "항목": st.column_config.TextColumn("항목"),
                "현재 금액": st.column_config.TextColumn("현재 금액 (원)"),
                "미래 금액": st.column_config.TextColumn("미래 금액 (원)"),
            },
            hide_index=True,
            use_container_width=True
        )
        
        st.markdown("""
        <div class="info-box">
            <h4>계산 방법 상세 설명</h4>
            <p><b>증여세 계산:</b></p>
            <ul>
                <li>과세표준을 구간별 누진세율에 따라 계산합니다.</li>
                <li>1억 이하: 10%, 1억~5억: 20%, 5억~10억: 30%, 10억~30억: 40%, 30억 초과: 50%</li>
                <li>예: 35억원의 경우 = (1억×10%)+(4억×20%)+(5억×30%)+(20억×40%)+(5억×50%) = 15억 3천만원</li>
            </ul>
            <p><b>양도소득세 계산:</b></p>
            <ul>
                <li>양도차익 = 양도가액 - 취득가액</li>
                <li>과세표준 = 양도차익 - 기본공제 250만원</li>
                <li>3억 이하: 22%, 3억 초과: 27.5%의 세율 적용</li>
            </ul>
            <p><b>청산소득세 계산:</b></p>
            <ul>
                <li>법인세: 2억 이하 10%, 2억~200억 20%, 200억~3000억 22%, 3000억 초과 25%</li>
                <li>배당소득세: (잔여재산 - 법인세) × 15.4%</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # 참고사항
    st.markdown("""
    <div class="warning-note">
        <p>※ 이 계산기의 세금 계산은 참고용으로만 사용하시기 바랍니다.</p>
        <p>※ 실제 세금은 개인 상황, 보유기간, 대주주 여부 등에 따라 달라질 수 있으며, 미래 세법이 변경될 수 있습니다.</p>
        <p>※ 정확한 세금 계산과 절세 방안은 반드시 세무사나 회계사와 상담하시기 바랍니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 버튼 행
    col1, col2 = st.columns(2)
    with col1:
        if st.button("미래 주식가치로 돌아가기", use_container_width=True):
            try:
                st.switch_page("4_미래_주식가치.py")
            except:
                st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>미래 주식가치</b> 메뉴를 클릭하여 이동하세요.</div>", unsafe_allow_html=True)
    
    with col2:
        if st.button("처음부터 다시 계산하기", type="primary", use_container_width=True):
            # 세션 상태 초기화
            st.session_state.evaluated = False
            st.session_state.future_evaluated = False
            st.session_state.stock_value = None
            st.session_state.future_stock_value = None
            try:
                st.switch_page("1_비상장주식_평가.py")
            except:
                st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>비상장주식 평가</b> 메뉴를 클릭하여 이동하세요.</div>", unsafe_allow_html=True)
