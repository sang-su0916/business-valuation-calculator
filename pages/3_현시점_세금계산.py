import streamlit as st
import pandas as pd
import locale
import numpy as np
from datetime import datetime

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

# 간단한 숫자 형식화 함수
def simple_format(num):
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
    .rate-info {
        font-size: 0.9em;
        color: #666;
        margin: 5px 0;
    }
    .tax-description {
        color: #555;
        font-size: 0.9em;
        margin-top: 5px;
        padding: 5px 0;
        border-top: 1px solid #eee;
    }
    .summary-box {
        background-color: #e9f7ef;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
    }
    .calculation-box {
        background-color: #f0f8ff;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
    }
    .calculation-formula {
        font-family: monospace;
        color: #0066cc;
        font-weight: bold;
        margin: 5px 0;
    }
    .tax-info-section {
        background-color: #f0f7fb;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
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
    .tax-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 0.5rem;
    }
    .tax-amount-big {
        font-size: 1.8rem;
        font-weight: bold;
        color: #333;
        margin: 1rem 0;
    }
    .tax-option {
        color: #28a745;
        font-weight: bold;
    }
    .tax-card {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 15px 0;
    }
    .evaluated-value {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .value-display {
        display: flex;
        justify-content: space-between;
        margin: 5px 0;
    }
    .value-label {
        font-weight: bold;
        color: #555;
    }
    .value-amount {
        color: #0066cc;
    }
    .tax-analysis {
        background-color: #f0f9ff;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
    }
    .tax-calculation-step {
        background-color: #e6f3ff;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# 페이지 헤더
st.title("현시점 세금 계산")

# 상속증여세 계산 함수 (누진세율 적용)
def calculate_inheritance_tax(value):
    # 상속증여세 누진세율 적용 (2025년 기준)
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
    
    # 누진세율 계산 과정 저장
    calculation_steps = []
    step_details = []
    
    for limit, rate in tax_brackets:
        if remaining > 0:
            taxable = min(remaining, limit - prev_limit)
            step_tax = taxable * rate
            tax += step_tax
            
            # 계산 과정 저장
            if taxable > 0:
                if prev_limit == 0:
                    step_details.append({
                        "range": f"1억원 이하",
                        "amount": taxable,
                        "rate": rate,
                        "tax": step_tax
                    })
                elif prev_limit == 100000000:
                    step_details.append({
                        "range": f"1억원~5억원",
                        "amount": taxable,
                        "rate": rate,
                        "tax": step_tax
                    })
                elif prev_limit == 500000000:
                    step_details.append({
                        "range": f"5억원~10억원",
                        "amount": taxable,
                        "rate": rate,
                        "tax": step_tax
                    })
                elif prev_limit == 1000000000:
                    step_details.append({
                        "range": f"10억원~30억원",
                        "amount": taxable,
                        "rate": rate,
                        "tax": step_tax
                    })
                else:
                    step_details.append({
                        "range": f"30억원 초과",
                        "amount": taxable,
                        "rate": rate,
                        "tax": step_tax
                    })
                
                calculation_steps.append(f"{simple_format(taxable)}원 × {rate*100:.0f}% = {simple_format(step_tax)}원")
            
            remaining -= taxable
            prev_limit = limit
            if remaining <= 0:
                break
    
    # 실효세율 계산
    effective_rate = (tax / value) * 100 if value > 0 else 0
    
    return tax, calculation_steps, effective_rate, step_details

# 양도소득세 계산 함수 (누진세율 적용)
def calculate_transfer_tax(gain, acquisition_value):
    # 기본공제 250만원 적용
    taxable_gain = max(0, gain - 2500000)
    
    calculation_steps = []
    tax_formula = []
    
    tax_formula.append(f"과세표준: {simple_format(gain)} - 2,500,000 = {simple_format(taxable_gain)}원")
    
    # 3억 이하: 22%, 3억 초과: 27.5%
    if taxable_gain <= 300000000:
        tax = taxable_gain * 0.22
        tax_formula.append(f"세액: {simple_format(taxable_gain)} × 22% = {simple_format(tax)}원")
    else:
        tax_below_300m = 300000000 * 0.22
        tax_above_300m = (taxable_gain - 300000000) * 0.275
        tax = tax_below_300m + tax_above_300m
        
        tax_formula.append(f"3억원 이하: 300,000,000 × 22% = {simple_format(tax_below_300m)}원")
        tax_formula.append(f"3억원 초과: {simple_format(taxable_gain - 300000000)} × 27.5% = {simple_format(tax_above_300m)}원")
        tax_formula.append(f"합계: {simple_format(tax)}원")
    
    # 실효세율 계산
    effective_rate = (tax / gain) * 100 if gain > 0 else 0
    
    return tax, tax_formula, effective_rate

# 청산소득세 계산 함수 (법인세 + 배당소득세) - 2025년 세율 적용
def calculate_liquidation_tax(income, acquisition_value):
    # 법인세 누진세율 적용 (2025년 기준)
    corporate_tax = 0
    
    tax_formula = []
    
    # 법인세 계산 (일반법인의 경우)
    # 오류가 발생한 조건문 수정
    if income <= 200000000:  # 2억 이하
        corporate_tax = income * 0.09  # 9%
        tax_formula.append(f"법인세: 2억원 × 9% = {simple_format(corporate_tax)}원")
    else:  # 2억 초과
        corporate_tax = 200000000 * 0.09 + (income - 200000000) * 0.19  # 2억 초과분 19%
        tax_formula.append(f"법인세: 2억원 × 9% + ({simple_format(income - 200000000)} × 19%) = {simple_format(corporate_tax)}원")
    
    # 배당소득세 계산
    after_tax = income - corporate_tax
    dividend_tax = after_tax * 0.154  # 15.4%
    tax_formula.append(f"배당소득세: ({simple_format(income)} - {simple_format(corporate_tax)}) × 15.4% = {simple_format(dividend_tax)}원")
    
    total_tax = corporate_tax + dividend_tax
    tax_formula.append(f"총 세금: {simple_format(corporate_tax)} + {simple_format(dividend_tax)} = {simple_format(total_tax)}원")
    
    # 실효세율 계산
    effective_rate = (total_tax / income) * 100 if income > 0 else 0
    
    return corporate_tax, dividend_tax, total_tax, tax_formula, effective_rate

# 세금 계산 함수
def calculate_tax_details(value, owned_shares, share_price):
    if not value:
        return None
    
    owned_value = value["ownedValue"]
    
    # 상속증여세 (누진세율 적용)
    inheritance_tax, inheritance_steps, inheritance_rate, inheritance_details = calculate_inheritance_tax(owned_value)
    
    # 양도소득세 (누진세율 적용)
    acquisition_value = owned_shares * share_price
    transfer_profit = owned_value - acquisition_value
    transfer_tax, transfer_formula, transfer_rate = calculate_transfer_tax(transfer_profit, acquisition_value)
    
    # 청산소득세 계산 (법인세 + 배당소득세)
    corporate_tax, dividend_tax, total_liquidation_tax, liquidation_formula, liquidation_rate = calculate_liquidation_tax(owned_value, acquisition_value)
    
    after_tax_value = owned_value - corporate_tax
    
    return {
        "inheritanceTax": inheritance_tax,
        "transferTax": transfer_tax,
        "corporateTax": corporate_tax,
        "liquidationTax": dividend_tax,
        "acquisitionValue": acquisition_value,
        "transferProfit": transfer_profit,
        "afterTaxValue": after_tax_value,
        "totalTax": total_liquidation_tax,
        "inheritanceSteps": inheritance_steps,
        "transferFormula": transfer_formula,
        "liquidationFormula": liquidation_formula,
        "inheritanceRate": inheritance_rate,
        "transferRate": transfer_rate,
        "liquidationRate": liquidation_rate,
        "inheritanceDetails": inheritance_details,
        "ownedValue": owned_value  # 명시적으로 owned_value 추가
    }

if not st.session_state.get('evaluated', False):
    st.warning("먼저 '비상장주식 평가' 페이지에서 평가를 진행해주세요.")
    st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>비상장주식 평가</b> 메뉴를 클릭하여 평가를 먼저 진행하세요.</div>", unsafe_allow_html=True)
else:
    stock_value = st.session_state.stock_value
    company_name = st.session_state.company_name
    owned_shares = st.session_state.owned_shares
    share_price = st.session_state.share_price
    eval_date = st.session_state.get('eval_date', None) or datetime.now().date()
    
    # 세금 계산
    current_tax_details = calculate_tax_details(stock_value, owned_shares, share_price)
    
    # 평가된 주식 가치 정보 표시 (이미지 1의 상단 섹션과 유사하게 구성)
    st.markdown("<div class='evaluated-value'>", unsafe_allow_html=True)
    st.markdown("<h3>평가된 주식 가치</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='value-display'><span class='value-label'>회사명:</span> <span class='value-amount'>{company_name}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='value-display'><span class='value-label'>주당 평가액:</span> <span class='value-amount'>{simple_format(stock_value['finalValue'])}원</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='value-display'><span class='value-label'>평가 기준일:</span> <span class='value-amount'>{eval_date.strftime('%Y년 %m월 %d일')}</span></div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"<div class='value-display'><span class='value-label'>회사 총가치:</span> <span class='value-amount'>{simple_format(stock_value['totalValue'])}원</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='value-display'><span class='value-label'>대표이사 보유주식 가치:</span> <span class='value-amount'>{simple_format(stock_value['ownedValue'])}원</span></div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 세금 계산 결과 표시 (이미지 1의 중앙 섹션과 유사하게 구성)
    st.subheader("세금 계산 결과")
    
    col1, col2, col3 = st.columns(3)
    
    # 증여세 카드
    with col1:
        st.markdown("<div class='tax-card'>", unsafe_allow_html=True)
        st.markdown("<h4>증여세</h4>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-amount-big'>{simple_format(current_tax_details['inheritanceTax'])}원</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-option'>적용 세율: 누진세율 (10%~50%)</div>", unsafe_allow_html=True)
        st.markdown("<p>주식을 타인에게 무상으로 증여할 경우 발생하는 세금입니다. 증여 받은 사람이 납부합니다.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 양도소득세 카드
    with col2:
        st.markdown("<div class='tax-card'>", unsafe_allow_html=True)
        st.markdown("<h4>양도소득세</h4>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-amount-big'>{simple_format(current_tax_details['transferTax'])}원</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-option'>적용 세율: 3억 이하 22%, 초과 27.5%</div>", unsafe_allow_html=True)
        st.markdown("<p>주식을 매각하여 발생한 이익(양도차익)에 대해 부과되는 세금입니다. 기본공제 250만원이 적용됩니다.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 청산소득세 카드
    with col3:
        st.markdown("<div class='tax-card'>", unsafe_allow_html=True)
        st.markdown("<h4>청산소득세</h4>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-amount-big'>{simple_format(current_tax_details['totalTax'])}원</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-option'>법인세 + 배당소득세 15.4%</div>", unsafe_allow_html=True)
        st.markdown("<p>법인 청산 시 발생하는 세금으로, 법인세와 잔여재산 분배에 따른 배당소득세로 구성됩니다.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 세금 계산 방법 세부내역 섹션
    with st.expander("양도소득세 계산 세부내역"):
        st.markdown("<div class='calculation-box'>", unsafe_allow_html=True)
        st.markdown(f"<p class='calculation-formula'>과세표준: {simple_format(current_tax_details['transferProfit'])} - 2,500,000 = {simple_format(current_tax_details['transferProfit']-2500000)}원</p>", unsafe_allow_html=True)
        
        taxable_gain = current_tax_details['transferProfit'] - 2500000
        if taxable_gain <= 300000000:
            st.markdown(f"<p class='calculation-formula'>{simple_format(taxable_gain)} × 22% = {simple_format(taxable_gain * 0.22)}원</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p class='calculation-formula'>3억원 이하: 300,000,000 × 22% = {simple_format(300000000*0.22)}원</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='calculation-formula'>3억원 초과: {simple_format(taxable_gain-300000000)} × 27.5% = {simple_format((taxable_gain-300000000)*0.275)}원</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='calculation-formula'>합계: {simple_format(current_tax_details['transferTax'])}원</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 청산소득세 계산 세부내역
    with st.expander("청산소득세 계산 세부내역"):
        st.markdown("<div class='calculation-box'>", unsafe_allow_html=True)
        # 이 부분을 수정하여 조건문 오류 방지
        owned_value = current_tax_details['ownedValue']
        if owned_value <= 200000000:  # 2억 이하
            corporate_tax = owned_value * 0.09  # 9%
            st.markdown(f"<p class='calculation-formula'>법인세: {simple_format(owned_value)} × 9% = {simple_format(corporate_tax)}원</p>", unsafe_allow_html=True)
        else:  # 2억 초과
            corporate_tax = 200000000 * 0.09 + (owned_value - 200000000) * 0.19  # 2억 초과분 19%
            st.markdown(f"<p class='calculation-formula'>법인세: 2억원 × 9% + ({simple_format(owned_value - 200000000)} × 19%) = {simple_format(corporate_tax)}원</p>", unsafe_allow_html=True)
        
        after_tax = owned_value - corporate_tax
        dividend_tax = after_tax * 0.154  # 15.4%
        st.markdown(f"<p class='calculation-formula'>배당소득세: ({simple_format(owned_value)} - {simple_format(corporate_tax)}) × 15.4% = {simple_format(dividend_tax)}원</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='calculation-formula'>총 세금: {simple_format(corporate_tax)} + {simple_format(dividend_tax)} = {simple_format(corporate_tax + dividend_tax)}원</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 세금 비교 분석 (이미지 1의 하단 섹션과 유사하게 구성)
    st.markdown("<div class='tax-analysis'>", unsafe_allow_html=True)
    st.markdown("<h3>세금 비교 분석</h3>", unsafe_allow_html=True)
    st.markdown("<p>위 세금 계산 결과를 바탕으로 자산 처분 방법에 따른 세금 부담을 비교할 수 있습니다:</p>", unsafe_allow_html=True)
    
    # 세금 부담 순서 결정
    taxes = [
        {"name": "증여세", "amount": current_tax_details['inheritanceTax'], "rate": current_tax_details['inheritanceRate']},
        {"name": "양도소득세", "amount": current_tax_details['transferTax'], "rate": current_tax_details['transferRate']},
        {"name": "청산소득세", "amount": current_tax_details['totalTax'], "rate": current_tax_details['liquidationRate']}
    ]
    
    # 세금 부담 순으로 정렬
    sorted_taxes = sorted(taxes, key=lambda x: x["amount"])
    lowest_tax = sorted_taxes[0]["name"]
    
    st.markdown("<ul>", unsafe_allow_html=True)
    for tax in sorted_taxes:
        if tax["name"] == lowest_tax:
            st.markdown(f"<li><b>{tax['name']}</b>는 <b>{simple_format(tax['amount'])}원</b>으로, 세금 부담이 가장 적습니다.</li>", unsafe_allow_html=True)
        else:
            st.markdown(f"<li>{tax['name']}는 {simple_format(tax['amount'])}원입니다.</li>", unsafe_allow_html=True)
    st.markdown("</ul>", unsafe_allow_html=True)
    
    st.markdown("<p>상황에 따라 가장 유리한 방법을 선택하는 것이 중요합니다. 다음 사항을 고려하세요:</p>", unsafe_allow_html=True)
    st.markdown("<ul>", unsafe_allow_html=True)
    st.markdown("<li>증여세는 높은 누진세율이 적용됩니다만, 한 번에 세금 부담을 해결할 수 있습니다.</li>", unsafe_allow_html=True)
    st.markdown("<li>양도소득세는 취득가액과 기본공제가 적용되어 실제 세금 부담이 낮아질 수 있습니다.</li>", unsafe_allow_html=True)
    st.markdown("<li>청산소득세는 법인세와 배당소득세가 이중으로 과세되나, 법인 규모에 따라 유리할 수 있습니다.</li>", unsafe_allow_html=True)
    st.markdown("</ul>", unsafe_allow_html=True)
    
    st.markdown("<p><i>주의: 실제 세금은 개인 상황, 보유기간, 대주주 여부 등에 따라 달라질 수 있습니다.</i></p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 버튼 행
    col1, col2 = st.columns(2)
    with col1:
        if st.button("주식가치 결과로 돌아가기", use_container_width=True):
            try:
                st.switch_page("2_주식가치_결과.py")
            except:
                st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>주식가치 결과</b> 메뉴를 클릭하여 이동하세요.</div>", unsafe_allow_html=True)
    
    with col2:
        if st.button("미래 주식가치 계산하기", type="primary", use_container_width=True):
            try:
                st.switch_page("4_미래_주식가치.py")
            except:
                st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>미래 주식가치</b> 메뉴를 클릭하여 이동하세요.</div>", unsafe_allow_html=True)
