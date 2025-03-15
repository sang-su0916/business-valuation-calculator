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
    .tax-card {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
    }
    .tax-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .tax-amount {
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }
    .tax-rate {
        color: #28a745;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .tax-description {
        color: #555;
        font-size: 0.95em;
        margin: 10px 0;
    }
    .sidebar-guide {
        background-color: #e8f4f8;
        padding: 10px 15px;
        border-radius: 5px;
        margin-top: 10px;
        font-size: 0.9em;
        border-left: 3px solid #4dabf7;
    }
    .tax-info-section {
        background-color: #f0f7fb;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    .calculation-box {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .calculation-step {
        font-family: monospace;
        margin: 5px 0;
    }
    .bullet-item {
        margin-left: 20px;
        position: relative;
    }
    .bullet-item:before {
        content: "•";
        position: absolute;
        left: -15px;
    }
    .note-text {
        color: #6c757d;
        font-size: 0.9em;
        font-style: italic;
    }
    .blue-text {
        color: #0066cc;
        font-weight: bold;
    }
    .tax-compare-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
    }
    .tax-compare-table th, .tax-compare-table td {
        border: 1px solid #dee2e6;
        padding: 8px 12px;
        text-align: left;
    }
    .tax-compare-table th {
        background-color: #f8f9fa;
    }
    .analysis-section {
        background-color: #e9f7ef;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# 페이지 헤더
st.title("미래 세금 계산")

# 상속증여세 계산 함수 (누진세율 적용)
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
    calculation_steps = []
    
    for limit, rate in tax_brackets:
        if remaining > 0:
            taxable = min(remaining, limit - prev_limit)
            step_tax = taxable * rate
            tax += step_tax
            
            # 계산 과정 저장
            if taxable > 0:
                if prev_limit == 0:
                    bracket_name = "1억원 이하"
                elif prev_limit == 100000000:
                    bracket_name = "1억원~5억원"
                elif prev_limit == 500000000:
                    bracket_name = "5억원~10억원"
                elif prev_limit == 1000000000:
                    bracket_name = "10억원~30억원"
                else:
                    bracket_name = "30억원 초과"
                
                calculation_steps.append({
                    "bracket": bracket_name,
                    "amount": taxable,
                    "rate": rate,
                    "tax": step_tax
                })
            
            remaining -= taxable
            prev_limit = limit
            if remaining <= 0:
                break
    
    # 실효세율 계산
    effective_rate = (tax / value) * 100 if value > 0 else 0
    
    return tax, calculation_steps, effective_rate

# 양도소득세 계산 함수
def calculate_transfer_tax(gain, acquisition_value):
    # 기본공제 250만원 적용
    taxable_gain = max(0, gain - 2500000)
    
    calculation_steps = []
    calculation_steps.append({"description": "양도차익 계산", "detail": f"양도가액({simple_format(gain)}원) - 취득가액({simple_format(acquisition_value)}원) = {simple_format(gain)}원"})
    calculation_steps.append({"description": "기본공제", "detail": f"2,500,000원"})
    calculation_steps.append({"description": "과세표준", "detail": f"{simple_format(taxable_gain)}원"})
    
    # 3억 이하: 22%, 3억 초과: 27.5%
    if taxable_gain <= 300000000:
        tax = taxable_gain * 0.22
        calculation_steps.append({"description": "세액 계산", "detail": f"{simple_format(taxable_gain)}원 × 22% = {simple_format(tax)}원"})
    else:
        tax_below_300m = 300000000 * 0.22
        tax_above_300m = (taxable_gain - 300000000) * 0.275
        tax = tax_below_300m + tax_above_300m
        
        calculation_steps.append({"description": "3억원 이하", "detail": f"300,000,000원 × 22% = {simple_format(tax_below_300m)}원"})
        calculation_steps.append({"description": "3억원 초과", "detail": f"{simple_format(taxable_gain - 300000000)}원 × 27.5% = {simple_format(tax_above_300m)}원"})
        calculation_steps.append({"description": "합계", "detail": f"{simple_format(tax)}원"})
    
    # 실효세율 계산
    effective_rate = (tax / gain) * 100 if gain > 0 else 0
    
    return tax, calculation_steps, effective_rate

# 청산소득세 계산 함수
def calculate_liquidation_tax(income, acquisition_value, is_family_corp=False):
    calculation_steps = []
    calculation_steps.append({"description": "청산소득금액", "detail": f"{simple_format(income)}원 (잔여재산 - 자기자본 {simple_format(acquisition_value)}원)"})
    
    # 법인세 계산
    if is_family_corp:
        # 가족법인
        if income <= 20000000000:
            corporate_tax = income * 0.19
            calculation_steps.append({"description": "법인세(가족법인, 200억 이하)", "detail": f"{simple_format(income)}원 × 19% = {simple_format(corporate_tax)}원"})
        elif income <= 300000000000:
            corporate_tax = 20000000000 * 0.19 + (income - 20000000000) * 0.21
            calculation_steps.append({"description": "법인세(가족법인)", "detail": f"200억원 × 19% + {simple_format(income - 20000000000)}원 × 21% = {simple_format(corporate_tax)}원"})
        else:
            corporate_tax = 20000000000 * 0.19 + (300000000000 - 20000000000) * 0.21 + (income - 300000000000) * 0.24
            calculation_steps.append({"description": "법인세(가족법인)", "detail": f"200억원 × 19% + 2,800억원 × 21% + {simple_format(income - 300000000000)}원 × 24% = {simple_format(corporate_tax)}원"})
    else:
        # 일반법인
        if income <= 200000000:
            corporate_tax = income * 0.09
            calculation_steps.append({"description": "법인세(2억 이하)", "detail": f"{simple_format(income)}원 × 9% = {simple_format(corporate_tax)}원"})
        elif income <= 20000000000:
            corporate_tax = 200000000 * 0.09 + (income - 200000000) * 0.19
            calculation_steps.append({"description": "법인세", "detail": f"2억원 × 9% + {simple_format(income - 200000000)}원 × 19% = {simple_format(corporate_tax)}원"})
        elif income <= 300000000000:
            corporate_tax = 200000000 * 0.09 + (20000000000 - 200000000) * 0.19 + (income - 20000000000) * 0.21
            calculation_steps.append({"description": "법인세", "detail": f"2억원 × 9% + 198억원 × 19% + {simple_format(income - 20000000000)}원 × 21% = {simple_format(corporate_tax)}원"})
        else:
            corporate_tax = 200000000 * 0.09 + (20000000000 - 200000000) * 0.19 + (300000000000 - 20000000000) * 0.21 + (income - 300000000000) * 0.24
            calculation_steps.append({"description": "법인세", "detail": f"2억원 × 9% + 198억원 × 19% + 2,800억원 × 21% + {simple_format(income - 300000000000)}원 × 24% = {simple_format(corporate_tax)}원"})
    
    # 배당소득세 계산
    after_tax = income - corporate_tax
    dividend_tax = after_tax * 0.154
    calculation_steps.append({"description": "배당소득세", "detail": f"({simple_format(income)}원 - {simple_format(corporate_tax)}원) × 15.4% = {simple_format(dividend_tax)}원"})
    
    total_tax = corporate_tax + dividend_tax
    calculation_steps.append({"description": "총 세금", "detail": f"{simple_format(corporate_tax)}원 + {simple_format(dividend_tax)}원 = {simple_format(total_tax)}원"})
    
    # 실효세율 계산
    effective_rate = (total_tax / income) * 100 if income > 0 else 0
    
    return corporate_tax, dividend_tax, total_tax, calculation_steps, effective_rate

# 미래 가치 계산 함수
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
    
    # 미래 세금 계산 정보
    st.markdown("<div class='tax-info-section'>", unsafe_allow_html=True)
    st.markdown("<h3>미래 세금 계산 정보</h3>", unsafe_allow_html=True)
    st.markdown("<p>현재 가치와 예측된 미래 가치에 기반한 세금을 비교합니다.</p>", unsafe_allow_html=True)
    
    # 기준 시점
    st.markdown("<div class='bullet-item'>기준 시점: <span class='blue-text'>2025년</span></div>", unsafe_allow_html=True)
    
    # 예측 시점 (10년 후)
    years = 10
    future_date = eval_date + timedelta(days=365 * years)
    st.markdown(f"<div class='bullet-item'>예측 시점: <span class='blue-text'>{future_date.year}년 ({years}년 후)</span></div>", unsafe_allow_html=True)
    
    # 성장률 선택
    growth_rate = st.slider("적용 성장률 (%)", min_value=1, max_value=50, value=10, step=1)
    st.markdown(f"<div class='bullet-item'>적용 성장률: <span class='blue-text'>연 {growth_rate}% (복리)</span></div>", unsafe_allow_html=True)
    
    # 가족법인 여부
    is_family_corp = st.checkbox("가족법인 여부 (부동산임대업 주업, 지배주주 50% 초과, 상시근로자 5명 미만)", 
                          help="2025년부터 가족법인(부동산임대업 등 주업)에 대해서는 법인세 최저세율이 19%로 적용됩니다")
    
    st.markdown("<p class='note-text'>※ 미래 세금은 현행 세법을 기준으로 계산되었으며, 향후 세법 변경에 따라 달라질 수 있습니다.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 미래 회사 가치 계산
    future_value = calculate_future_value(stock_value, growth_rate, years)
    
    # 미래 주식가치 정보
    with st.expander("미래 주식 가치", expanded=True):
        st.markdown("<div class='tax-info-section'>", unsafe_allow_html=True)
        st.markdown(f"<div>회사명: <b>{company_name}</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div>예측 기간: <b>{years}년</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div>적용 성장률: <b>연 {growth_rate}%</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div>미래 주당 평가액: <b>{simple_format(future_value['finalValue'])}원</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div>미래 회사 총가치: <b>{simple_format(future_value['totalValue'])}원</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div>미래 대표이사 보유주식 가치: <b>{simple_format(future_value['ownedValue'])}원</b></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 현재와 미래 세금 계산
    current_ownership_value = stock_value["ownedValue"]
    future_ownership_value = future_value["ownedValue"]
    acquisition_value = owned_shares * share_price
    
    # 현재 세금 계산
    current_inheritance_tax, current_inheritance_steps, current_inheritance_rate = calculate_inheritance_tax(current_ownership_value)
    current_transfer_tax, current_transfer_steps, current_transfer_rate = calculate_transfer_tax(current_ownership_value - acquisition_value, acquisition_value)
    current_corporate_tax, current_dividend_tax, current_liquidation_tax, current_liquidation_steps, current_liquidation_rate = calculate_liquidation_tax(current_ownership_value, acquisition_value, is_family_corp)
    
    # 미래 세금 계산
    future_inheritance_tax, future_inheritance_steps, future_inheritance_rate = calculate_inheritance_tax(future_ownership_value)
    future_transfer_tax, future_transfer_steps, future_transfer_rate = calculate_transfer_tax(future_ownership_value - acquisition_value, acquisition_value)
    future_corporate_tax, future_dividend_tax, future_liquidation_tax, future_liquidation_steps, future_liquidation_rate = calculate_liquidation_tax(future_ownership_value, acquisition_value, is_family_corp)
    
    # 세금 계산 결과
    st.header("미래 세금 계산 결과")
    
    col1, col2, col3 = st.columns(3)
    
    # 증여세 카드
    with col1:
        st.markdown("<div class='tax-card'>", unsafe_allow_html=True)
        st.markdown("<h3>증여세</h3>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-amount'>{simple_format(future_inheritance_tax)}원</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-rate'>적용 세율: 누진세율 (10%~50%)</div>", unsafe_allow_html=True)
        st.markdown("<div class='tax-description'>주식을 타인에게 무상으로 증여할 경우 발생하는 세금입니다. 증여 받은 사람이 납부합니다.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 양도소득세 카드
    with col2:
        st.markdown("<div class='tax-card'>", unsafe_allow_html=True)
        st.markdown("<h3>양도소득세</h3>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-amount'>{simple_format(future_transfer_tax)}원</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-rate'>적용 세율: 3억 이하 22%, 초과 27.5%</div>", unsafe_allow_html=True)
        st.markdown("<div class='tax-description'>주식을 매각하여 발생한 이익(양도차익)에 대해 부과되는 세금입니다. 기본공제 250만원이 적용됩니다.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 청산소득세 카드
    with col3:
        st.markdown("<div class='tax-card'>", unsafe_allow_html=True)
        st.markdown("<h3>청산소득세</h3>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-amount'>{simple_format(future_liquidation_tax)}원</div>", unsafe_allow_html=True)
        if is_family_corp:
            st.markdown(f"<div class='tax-rate'>법인세(19~24%) + 배당세 15.4%</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='tax-rate'>법인세(9~24%) + 배당세 15.4%</div>", unsafe_allow_html=True)
        st.markdown("<div class='tax-description'>법인 청산 시 발생하는 세금으로, 법인세와 잔여재산 분배에 따른 배당소득세로 구성됩니다.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 미래 증여세 계산 세부내역
    with st.expander("증여세 계산 세부내역"):
        st.markdown("<div class='calculation-box'>", unsafe_allow_html=True)
        st.markdown(f"<p>과세표준: {simple_format(future_ownership_value)}원</p>", unsafe_allow_html=True)
        
        for step in future_inheritance_steps:
            st.markdown(f"<div class='calculation-step'>{step['bracket']}: {simple_format(step['amount'])}원 × {int(step['rate']*100)}% = {simple_format(step['tax'])}원</div>", unsafe_allow_html=True)
        
        st.markdown(f"<p><b>총 증여세: {simple_format(future_inheritance_tax)}원</b> (실효세율: {future_inheritance_rate:.1f}%)</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 미래 양도소득세 계산 세부내역
    with st.expander("양도소득세 계산 세부내역"):
        st.markdown("<div class='calculation-box'>", unsafe_allow_html=True)
        
        for step in future_transfer_steps:
            st.markdown(f"<div class='calculation-step'>{step['description']}: {step['detail']}</div>", unsafe_allow_html=True)
        
        st.markdown(f"<p><b>총 양도소득세: {simple_format(future_transfer_tax)}원</b> (실효세율: {future_transfer_rate:.1f}%)</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 미래 청산소득세 계산 세부내역
    with st.expander("청산소득세 계산 세부내역"):
        st.markdown("<div class='calculation-box'>", unsafe_allow_html=True)
        
        for step in future_liquidation_steps:
            st.markdown(f"<div class='calculation-step'>{step['description']}: {step['detail']}</div>", unsafe_allow_html=True)
        
        st.markdown(f"<p><b>총 청산소득세: {simple_format(future_liquidation_tax)}원</b> (실효세율: {future_liquidation_rate:.1f}%)</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 현재 vs 미래 세금 비교
    st.markdown("<h2>현재 vs 미래 세금 비교</h2>", unsafe_allow_html=True)
    
    # 세금 비교 테이블
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
    inheritance_increase = (future_inheritance_tax / current_inheritance_tax - 1) * 100
    st.markdown(f"""
    <tr>
        <td>증여세 (누진세율)</td>
        <td>{simple_format(current_inheritance_tax)}원</td>
        <td class="blue-text">{simple_format(future_inheritance_tax)}원</td>
    </tr>
    """, unsafe_allow_html=True)
    
    # 양도소득세 비교 행
    transfer_increase = (future_transfer_tax / current_transfer_tax - 1) * 100
    st.markdown(f"""
    <tr>
        <td>양도소득세 (22%~27.5%)</td>
        <td>{simple_format(current_transfer_tax)}원</td>
        <td class="blue-text">{simple_format(future_transfer_tax)}원</td>
    </tr>
    """, unsafe_allow_html=True)
    
    # 청산소득세 비교 행
    liquidation_increase = (future_liquidation_tax / current_liquidation_tax - 1) * 100
    st.markdown(f"""
    <tr>
        <td>청산소득세 (법인세+배당세)</td>
        <td>{simple_format(current_liquidation_tax)}원</td>
        <td class="blue-text">{simple_format(future_liquidation_tax)}원</td>
    </tr>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        </tbody>
    </table>
    """, unsafe_allow_html=True)
    
    # 세금 비교 분석
    st.markdown("<div class='analysis-section'>", unsafe_allow_html=True)
    st.markdown("<h3>세금 비교 분석</h3>", unsafe_allow_html=True)
    
    # 최적의 세금 옵션 찾기 (현재)
    current_min_tax = min(current_inheritance_tax, current_transfer_tax, current_liquidation_tax)
    
    if current_min_tax == current_inheritance_tax:
        current_best = "증여세"
    elif current_min_tax == current_transfer_tax:
        current_best = "양도소득세"
    else:
        current_best = "청산소득세"
    
    # 최적의 세금 옵션 찾기 (미래)
    future_min_tax = min(future_inheritance_tax, future_transfer_tax, future_liquidation_tax)
    
    if future_min_tax == future_inheritance_tax:
        future_best = "증여세"
    elif future_min_tax == future_transfer_tax:
        future_best = "양도소득세"
    else:
        future_best = "청산소득세"
    
    st.markdown(f"<div>현재 기준으로는 <b>{current_best}</b>가 세금 부담이 가장 적습니다.</div>", unsafe_allow_html=True)
    st.markdown(f"<div>미래 기준으로는 <b>{future_best}</b>가 세금 부담이 가장 적을 것으로 예상됩니다.</div>", unsafe_allow_html=True)
    
    # 세금 증가율 표시
    st.markdown("<h4>세금 증가 예상</h4>", unsafe_allow_html=True)
    st.markdown(f"<div>증여세: <b>+{inheritance_increase:.1f}%</b> 증가</div>", unsafe_allow_html=True)
    st.markdown(f"<div>양도소득세: <b>+{transfer_increase:.1f}%</b> 증가</div>", unsafe_allow_html=True)
    st.markdown(f"<div>청산소득세: <b>+{liquidation_increase:.1f}%</b> 증가</div>", unsafe_allow_html=True)
    
    st.markdown("<p>기업 가치의 성장에 따라 세금 부담도 증가합니다. 누진세율이 적용되는 증여세의 경우 가치 증가 비율보다 세금 증가 비율이 더 높을 수 있습니다.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 적용 세율 정보
    with st.expander("적용 세율 정보"):
        st.markdown("<div class='tax-info-section'>", unsafe_allow_html=True)
        st.markdown("<h4>증여세율</h4>", unsafe_allow_html=True)
        st.markdown("<ul>", unsafe_allow_html=True)
        st.markdown("<li>1억 이하: 10%</li>", unsafe_allow_html=True)
        st.markdown("<li>1억~5억: 20%</li>", unsafe_allow_html=True)
        st.markdown("<li>5억~10억: 30%</li>", unsafe_allow_html=True)
        st.markdown("<li>10억~30억: 40%</li>", unsafe_allow_html=True)
        st.markdown("<li>30억 초과: 50%</li>", unsafe_allow_html=True)
        st.markdown("</ul>", unsafe_allow_html=True)
        
        st.markdown("<h4>양도소득세율</h4>", unsafe_allow_html=True)
        st.markdown("<ul>", unsafe_allow_html=True)
        st.markdown("<li>3억 이하: 22%</li>", unsafe_allow_html=True)
        st.markdown("<li>3억 초과: 27.5%</li>", unsafe_allow_html=True)
        st.markdown("<li>기본공제: 250만원</li>", unsafe_allow_html=True)
        st.markdown("</ul>", unsafe_allow_html=True)
        
        st.markdown("<h4>법인세율 (2025년 기준)</h4>", unsafe_allow_html=True)
        st.markdown("<ul>", unsafe_allow_html=True)
        if is_family_corp:
            st.markdown("<li>가족법인 200억 이하: 19%</li>", unsafe_allow_html=True)
            st.markdown("<li>200억~3,000억: 21%</li>", unsafe_allow_html=True)
            st.markdown("<li>3,000억 초과: 24%</li>", unsafe_allow_html=True)
        else:
            st.markdown("<li>2억 이하: 9%</li>", unsafe_allow_html=True)
            st.markdown("<li>2억~200억: 19%</li>", unsafe_allow_html=True)
            st.markdown("<li>200억~3,000억: 21%</li>", unsafe_allow_html=True)
            st.markdown("<li>3,000억 초과: 24%</li>", unsafe_allow_html=True)
        st.markdown("<li>배당소득세: 15.4%</li>", unsafe_allow_html=True)
        st.markdown("</ul>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 참고사항
    st.markdown("<div class='tax-info-section'>", unsafe_allow_html=True)
    st.markdown("<p>※ 이 계산기의 세금 계산은 참고용으로만 사용하시기 바랍니다.</p>", unsafe_allow_html=True)
    st.markdown("<p>※ 실제 세금은 개인 상황, 보유기간, 대주주 여부, 사업 형태 등에 따라 달라질 수 있습니다.</p>", unsafe_allow_html=True)
    st.markdown("<p>※ 미래 가치 예측은 단순 성장률 적용으로 실제 기업 가치 변동과는 차이가 있을 수 있습니다.</p>", unsafe_allow_html=True)
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
