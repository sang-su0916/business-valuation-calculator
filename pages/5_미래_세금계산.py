import streamlit as st
import pandas as pd
import locale
import numpy as np
from datetime import datetime, timedelta

# 숫자 형식화를 위한 로케일 설정
try:
    locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'ko_KR')
    except:
        locale.setlocale(locale.LC_ALL, '')

# 숫자 형식화 함수
def simple_format(num):
    try:
        return "{:,}".format(int(num))
    except:
        return str(num)

# CSS 스타일 추가
st.markdown("""
<style>
    .tax-info-section { background-color: #f0f7fb; padding: 15px; border-radius: 5px; margin: 15px 0; }
    .sidebar-guide { background-color: #e8f4f8; padding: 10px 15px; border-radius: 5px; margin-top: 10px; font-size: 0.9em; border-left: 3px solid #4dabf7; }
    .tax-card { background-color: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 15px 0; }
    .tax-amount-big { font-size: 1.8rem; font-weight: bold; color: #333; margin: 1rem 0; }
    .tax-option { color: #28a745; font-weight: bold; }
    .value-display { display: flex; justify-content: space-between; margin: 5px 0; }
    .value-label { font-weight: bold; color: #555; }
    .value-amount { color: #0066cc; }
    .tax-increase { color: #e74c3c; font-weight: bold; }
    .tax-optimize { background-color: #e9fcef; border-radius: 5px; padding: 15px; margin: 15px 0; }
    .warning-box { background-color: #fff3cd; color: #856404; border-left: 4px solid #ffc107; padding: 15px; margin: 15px 0; border-radius: 5px; }
    .tax-compare-table { width: 100%; border-collapse: collapse; margin: 15px 0; }
    .tax-compare-table th, .tax-compare-table td { border: 1px solid #dee2e6; padding: 8px 12px; text-align: left; }
    .tax-compare-table th { background-color: #f8f9fa; }
    .blue-text { color: #0066cc; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 페이지 헤더
st.title("미래 세금 계산")

# 상속증여세 계산 함수
def calculate_inheritance_tax(value):
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
    
    effective_rate = (tax / value) * 100 if value > 0 else 0
    return tax, effective_rate

# 양도소득세 계산 함수
def calculate_transfer_tax(gain, acquisition_value):
    taxable_gain = max(0, gain - 2500000)  # 기본공제 250만원 적용
    
    if taxable_gain <= 300000000:
        tax = taxable_gain * 0.22
    else:
        tax = 300000000 * 0.22 + (taxable_gain - 300000000) * 0.275
    
    effective_rate = (tax / gain) * 100 if gain > 0 else 0
    return tax, effective_rate

# 청산소득세 계산 함수
def calculate_liquidation_tax(income, acquisition_value, is_family_corp=False):
    if is_family_corp:
        # 가족법인
        if income <= 20000000000:  # 200억 이하
            corporate_tax = income * 0.19
        elif income <= 300000000000:  # 200억 초과 3000억 이하
            corporate_tax = 20000000000 * 0.19 + (income - 20000000000) * 0.21
        else:  # 3000억 초과
            corporate_tax = 20000000000 * 0.19 + (300000000000 - 20000000000) * 0.21 + (income - 300000000000) * 0.24
    else:
        # 일반법인
        if income <= 200000000:  # 2억 이하
            corporate_tax = income * 0.09
        elif income <= 20000000000:  # 2억 초과 200억 이하
            corporate_tax = 200000000 * 0.09 + (income - 200000000) * 0.19
        elif income <= 300000000000:  # 200억 초과 3000억 이하
            corporate_tax = 200000000 * 0.09 + (20000000000 - 200000000) * 0.19 + (income - 20000000000) * 0.21
        else:  # 3000억 초과
            corporate_tax = 200000000 * 0.09 + (20000000000 - 200000000) * 0.19 + (300000000000 - 20000000000) * 0.21 + (income - 300000000000) * 0.24
    
    after_tax = income - corporate_tax
    dividend_tax = after_tax * 0.154  # 15.4%
    total_tax = corporate_tax + dividend_tax
    effective_rate = (total_tax / income) * 100 if income > 0 else 0
    
    return corporate_tax, dividend_tax, total_tax, effective_rate

# 세금 계산 함수
def calculate_tax_details(value, owned_shares, share_price, is_family_corp=False):
    if not value:
        return None
    
    owned_value = value["ownedValue"]
    acquisition_value = owned_shares * share_price
    transfer_profit = owned_value - acquisition_value
    
    inheritance_tax, inheritance_rate = calculate_inheritance_tax(owned_value)
    transfer_tax, transfer_rate = calculate_transfer_tax(transfer_profit, acquisition_value)
    corporate_tax, dividend_tax, total_liquidation_tax, liquidation_rate = calculate_liquidation_tax(owned_value, acquisition_value, is_family_corp)
    
    return {
        "inheritanceTax": inheritance_tax,
        "transferTax": transfer_tax,
        "corporateTax": corporate_tax,
        "liquidationTax": dividend_tax,
        "acquisitionValue": acquisition_value,
        "transferProfit": transfer_profit,
        "totalTax": total_liquidation_tax,
        "inheritanceRate": inheritance_rate,
        "transferRate": transfer_rate,
        "liquidationRate": liquidation_rate,
        "ownedValue": owned_value
    }

# 미래 회사 가치 계산
def calculate_future_value(current_value, growth_rate, years):
    future_value = {}
    for key, value in current_value.items():
        if isinstance(value, (int, float)):
            future_value[key] = value * (1 + growth_rate/100) ** years
        else:
            future_value[key] = value
    return future_value

# 메인 코드
if not st.session_state.get('evaluated', False):
    st.warning("먼저 '비상장주식 평가' 페이지에서 평가를 진행해주세요.")
    st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>비상장주식 평가</b> 메뉴를 클릭하여 평가를 먼저 진행하세요.</div>", unsafe_allow_html=True)
else:
    stock_value = st.session_state.stock_value
    company_name = st.session_state.company_name
    owned_shares = st.session_state.owned_shares
    share_price = st.session_state.share_price
    eval_date = st.session_state.get('eval_date', None) or datetime.now().date()
    
    # 미래 세금 계산을 위한 입력 받기
    st.markdown("<div class='tax-info-section'>", unsafe_allow_html=True)
    st.markdown("<h3>미래 세금 계산 정보</h3>", unsafe_allow_html=True)
    st.markdown("<p>현재 가치와 예측된 미래 가치에 기반한 세금을 비교합니다.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='value-display'><span class='value-label'>기준 시점:</span> <span class='value-amount'>2025년</span></div>", unsafe_allow_html=True)
        is_family_corp = st.checkbox("가족법인 여부 (부동산임대업 주업, 지배주주 50% 초과, 상시근로자 5명 미만)", 
                                help="2025년부터 가족법인(부동산임대업 등 주업)에 대해서는 법인세 최저세율이 19%로 적용됩니다")
    
    with col2:
        years = st.number_input("예측 기간(년)", min_value=1, max_value=30, value=10)
        growth_rate = st.slider("적용 성장률 (%)", min_value=1, max_value=50, value=30, step=1)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 현재 세금 계산
    current_tax_details = calculate_tax_details(stock_value, owned_shares, share_price, is_family_corp)
    
    # 미래 회사 가치 계산
    future_date = eval_date + timedelta(days=365 * years)
    future_value = calculate_future_value(stock_value, growth_rate, years)
    
    # 미래 세금 계산
    future_tax_details = calculate_tax_details(future_value, owned_shares, share_price, is_family_corp)
    
    # 미래 세금 계산 정보 표시
    st.markdown("<div class='tax-info-section'>", unsafe_allow_html=True)
    st.markdown("<h3>미래 세금 계산 정보</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='value-display'><span class='value-label'>예측 시점:</span> <span class='value-amount'>{future_date.strftime('%Y년')} ({years}년 후)</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='value-display'><span class='value-label'>적용 성장률:</span> <span class='value-amount'>연 {growth_rate}% (복리)</span></div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"<div class='value-display'><span class='value-label'>미래 주당 평가액:</span> <span class='value-amount'>{simple_format(future_value['finalValue'])}원</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='value-display'><span class='value-label'>미래 회사 총가치:</span> <span class='value-amount'>{simple_format(future_value['totalValue'])}원</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='value-display'><span class='value-label'>미래 대표이사 보유주식 가치:</span> <span class='value-amount'>{simple_format(future_value['ownedValue'])}원</span></div>", unsafe_allow_html=True)
    
    if is_family_corp:
        st.markdown("<div class='warning-box'>가족법인(부동산임대업 주업)으로 청산소득세 계산 시 법인세 최저세율 19% 적용</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 현재 vs 미래 세금 비교 표시
    st.markdown("<h2>현재 vs 미래 세금 비교</h2>", unsafe_allow_html=True)
    
    # 세금 비교 테이블
    st.markdown("<div class='table-container'>", unsafe_allow_html=True)
    st.markdown("""
    <table class="tax-compare-table">
        <thead>
            <tr>
                <th>세금 유형</th>
                <th>현재 (2025년)</th>
                <th>미래</th>
            </tr>
        </thead>
        <tbody>
    """, unsafe_allow_html=True)
    
    # 증여세 비교 행
    inheritance_increase = (future_tax_details['inheritanceTax'] / current_tax_details['inheritanceTax'] - 1) * 100
    st.markdown(f"""
    <tr>
        <td>증여세 (누진세율)</td>
        <td>{simple_format(current_tax_details['inheritanceTax'])}원</td>
        <td class="blue-text">{simple_format(future_tax_details['inheritanceTax'])}원 <span class='tax-increase'>(+{inheritance_increase:.1f}%)</span></td>
    </tr>
    """, unsafe_allow_html=True)
    
    # 양도소득세 비교 행
    transfer_increase = (future_tax_details['transferTax'] / current_tax_details['transferTax'] - 1) * 100
    st.markdown(f"""
    <tr>
        <td>양도소득세 (22%~27.5%)</td>
        <td>{simple_format(current_tax_details['transferTax'])}원</td>
        <td class="blue-text">{simple_format(future_tax_details['transferTax'])}원 <span class='tax-increase'>(+{transfer_increase:.1f}%)</span></td>
    </tr>
    """, unsafe_allow_html=True)
    
    # 청산소득세 비교 행
    liquidation_increase = (future_tax_details['totalTax'] / current_tax_details['totalTax'] - 1) * 100
    st.markdown(f"""
    <tr>
        <td>청산소득세 (법인세+배당세)</td>
        <td>{simple_format(current_tax_details['totalTax'])}원</td>
        <td class="blue-text">{simple_format(future_tax_details['totalTax'])}원 <span class='tax-increase'>(+{liquidation_increase:.1f}%)</span></td>
    </tr>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        </tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 적용 세율 정보
    st.markdown("<div class='tax-info-section'>", unsafe_allow_html=True)
    st.markdown("<h4>적용 세율 정보:</h4>", unsafe_allow_html=True)
    st.markdown("<ul>", unsafe_allow_html=True)
    st.markdown("<li><b>증여세</b>: 1억 이하 10%, 1억~5억 20%, 5억~10억 30%, 10억~30억 40%, 30억 초과 50% (누진세율)</li>", unsafe_allow_html=True)
    st.markdown("<li><b>양도소득세</b>: 3억 이하 22%, 3억 초과 27.5% (기본공제 250만원 적용)</li>", unsafe_allow_html=True)
    if is_family_corp:
        st.markdown("<li><b>법인세</b>: 가족법인 200억 이하 19%, 200억~3,000억 21%, 3,000억 초과 24% (배당소득세 15.4% 추가)</li>", unsafe_allow_html=True)
    else:
        st.markdown("<li><b>법인세</b>: 2억 이하 9%, 2억~200억 19%, 200억~3,000억 21%, 3,000억 초과 24% (배당소득세 15.4% 추가)</li>", unsafe_allow_html=True)
    st.markdown("</ul>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 세금 최적화 참고사항
    st.markdown("<div class='tax-optimize'>", unsafe_allow_html=True)
    st.markdown("<h3>세금 최적화 참고사항</h3>", unsafe_allow_html=True)
    
    # 현재와 미래 기준으로 세금 부담이 가장 낮은 방법 찾기
    current_min_tax = min(current_tax_details['inheritanceTax'], current_tax_details['transferTax'], current_tax_details['totalTax'])
    future_min_tax = min(future_tax_details['inheritanceTax'], future_tax_details['transferTax'], future_tax_details['totalTax'])
    
    if current_min_tax == current_tax_details['inheritanceTax']:
        current_best = "증여세"
    elif current_min_tax == current_tax_details['transferTax']:
        current_best = "양도소득세"
    else:
        current_best = "청산소득세"
        
    if future_min_tax == future_tax_details['inheritanceTax']:
        future_best = "증여세"
    elif future_min_tax == future_tax_details['transferTax']:
        future_best = "양도소득세"
    else:
        future_best = "청산소득세"
    
    st.markdown("<ul>", unsafe_allow_html=True)
    st.markdown(f"<li>현재 기준으로는 <b>{current_best}</b>가 세금 부담이 가장 적습니다.</li>", unsafe_allow_html=True)
    st.markdown(f"<li>미래({years}년 후) 기준으로는 <b>{future_best}</b>가 세금 부담이 가장 적을 것으로 예상됩니다.</li>", unsafe_allow_html=True)
    st.markdown("</ul>", unsafe_allow_html=True)
    
    st.markdown("<p>주의: 이는 단순 세금 비교이며, 실제 의사결정은 개인 상황, 자산 구성, 사업 목표 등을 고려해야 합니다.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 참고사항
    st.markdown("<div class='warning-box'>", unsafe_allow_html=True)
    st.markdown("※ 이 계산기의 세금 계산은 참고용으로만 사용하시기 바랍니다. 실제 세금은 개인 상황, 보유기간, 대주주 여부, 사업 형태 등에 따라 달라질 수 있습니다.", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 버튼 행
    col1, col2 = st.columns(2)
    with col1:
        if st.button("현시점 세금계산으로 돌아가기", use_container_width=True):
            try:
                st.switch_page("3_현시점_세금계산.py")
            except:
                st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>현시점 세금계산</b> 메뉴를 클릭하여 이동하세요.</div>", unsafe_allow_html=True)
    
    with col2:
        if st.button("처음으로 돌아가기", type="primary", use_container_width=True):
            try:
                st.switch_page("1_비상장주식_평가.py")
            except:
                st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>비상장주식 평가</b> 메뉴를 클릭하여 이동하세요.</div>", unsafe_allow_html=True)
