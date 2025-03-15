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
    .explanation-text {
        font-size: 0.95em;
        color: #555;
        margin: 15px 0;
        line-height: 1.5;
    }
    .summary-box {
        background-color: #e9f7ef;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
    }
    .calculation-example {
        background-color: #e8f4fd;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 10px 0;
        font-weight: bold;
        color: #0066cc;
    }
    .tax-info-section {
        background-color: #f0f7fb;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    .tax-increase {
        color: #ff6b6b;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 페이지 헤더
st.title("현시점 세금 계산")

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
                
                calculation_steps.append(f"{format_original(taxable)}원 × {rate*100:.0f}% = {format_original(step_tax)}원")
            
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
    calculation_steps.append(f"양도차익: {format_original(gain)}원 (양도가액 - 취득가액 {format_original(acquisition_value)}원)")
    calculation_steps.append(f"기본공제: 2,500,000원")
    calculation_steps.append(f"과세표준: {format_original(taxable_gain)}원")
    
    # 3억 이하: 22%, 3억 초과: 27.5%
    if taxable_gain <= 300000000:
        tax = taxable_gain * 0.22
        calculation_steps.append(f"세액: {format_original(taxable_gain)}원 × 22% = {format_original(tax)}원")
    else:
        tax_below_300m = 300000000 * 0.22
        tax_above_300m = (taxable_gain - 300000000) * 0.275
        tax = tax_below_300m + tax_above_300m
        calculation_steps.append(f"3억원 이하: 300,000,000원 × 22% = {format_original(tax_below_300m)}원")
        calculation_steps.append(f"3억원 초과: {format_original(taxable_gain - 300000000)}원 × 27.5% = {format_original(tax_above_300m)}원")
        calculation_steps.append(f"합계: {format_original(tax)}원")
    
    # 실효세율 계산
    effective_rate = (tax / gain) * 100 if gain > 0 else 0
    
    return tax, calculation_steps, effective_rate

# 청산소득세 계산 함수 (법인세 + 배당소득세)
def calculate_liquidation_tax(income, acquisition_value):
    # 법인세 누진세율 적용
    corporate_tax = 0
    
    calculation_steps = []
    calculation_steps.append(f"청산소득금액: {format_original(income)}원 (잔여재산 - 자기자본 {format_original(acquisition_value)}원)")
    
    # 법인세 계산
    if income <= 200000000:  # 2억 이하
        corporate_tax = income * 0.1
        calculation_steps.append(f"법인세(2억 이하): {format_original(income)}원 × 10% = {format_original(corporate_tax)}원")
    elif income <= 20000000000:  # 2억 초과 200억 이하
        corporate_tax = 200000000 * 0.1 + (income - 200000000) * 0.2
        calculation_steps.append(f"법인세: 200,000,000원 × 10% + {format_original(income - 200000000)}원 × 20% = {format_original(corporate_tax)}원")
    elif income <= 300000000000:  # 200억 초과 3000억 이하
        corporate_tax = 200000000 * 0.1 + (20000000000 - 200000000) * 0.2 + (income - 20000000000) * 0.22
        calculation_steps.append(f"법인세: 200,000,000원 × 10% + 19,800,000,000원 × 20% + {format_original(income - 20000000000)}원 × 22% = {format_original(corporate_tax)}원")
    else:  # 3000억 초과
        corporate_tax = 200000000 * 0.1 + (20000000000 - 200000000) * 0.2 + (300000000000 - 20000000000) * 0.22 + (income - 300000000000) * 0.25
        calculation_steps.append(f"법인세: 복합세율 적용 = {format_original(corporate_tax)}원")
    
    # 배당소득세 계산
    after_tax = income - corporate_tax
    dividend_tax = after_tax * 0.154
    calculation_steps.append(f"배당소득세: (청산소득 - 법인세) × 15.4% = {format_original(after_tax)}원 × 15.4% = {format_original(dividend_tax)}원")
    
    total_tax = corporate_tax + dividend_tax
    calculation_steps.append(f"총 세금: 법인세 + 배당소득세 = {format_original(corporate_tax)}원 + {format_original(dividend_tax)}원 = {format_original(total_tax)}원")
    
    # 실효세율 계산
    effective_rate = (total_tax / income) * 100 if income > 0 else 0
    
    return corporate_tax, dividend_tax, total_tax, calculation_steps, effective_rate

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
    transfer_tax, transfer_steps, transfer_rate = calculate_transfer_tax(transfer_profit, acquisition_value)
    
    # 청산소득세 계산 (법인세 + 배당소득세)
    corporate_tax, dividend_tax, total_liquidation_tax, liquidation_steps, liquidation_rate = calculate_liquidation_tax(owned_value, acquisition_value)
    
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
        "transferSteps": transfer_steps,
        "liquidationSteps": liquidation_steps,
        "inheritanceRate": inheritance_rate,
        "transferRate": transfer_rate,
        "liquidationRate": liquidation_rate,
        "inheritanceDetails": inheritance_details
    }

if not st.session_state.get('evaluated', False):
    st.warning("먼저 '비상장주식 평가' 페이지에서 평가를 진행해주세요.")
    st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>비상장주식 평가</b> 메뉴를 클릭하여 평가를 먼저 진행하세요.</div>", unsafe_allow_html=True)
else:
    stock_value = st.session_state.stock_value
    company_name = st.session_state.company_name
    owned_shares = st.session_state.owned_shares
    share_price = st.session_state.share_price
    eval_date = st.session_state.get('eval_date', None)
    
    # 세금 계산
    current_tax_details = calculate_tax_details(stock_value, owned_shares, share_price)
    
    # 평가된 주식 가치 정보 표시
    with st.expander("평가된 주식 가치", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**회사명:** {company_name}")
            st.markdown(f"**주당 평가액:** {format_number(stock_value['finalValue'])}")
        with col2:
            st.markdown(f"**회사 총가치:** {format_number(stock_value['totalValue'])}")
            st.markdown(f"**대표이사 보유주식 가치:** {format_number(stock_value['ownedValue'])}")
        
        if eval_date:
            st.markdown(f"**평가 기준일:** {eval_date.strftime('%Y년 %m월 %d일')}")
    
    # 세금 계산 결과
    st.subheader("세금 계산 결과")
    
    # 3개의 세금 결과 카드로 표시
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>증여세</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-amount'>{format_number(current_tax_details['inheritanceTax'])}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-rate'>적용 세율: 누진세율 (10%~50%)</div>", unsafe_allow_html=True)
        st.markdown("<div class='tax-description'>주식을 타인에게 무상으로 증여할 경우 발생하는 세금입니다. 증여 받은 사람이 납부합니다.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>양도소득세</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-amount'>{format_number(current_tax_details['transferTax'])}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-rate'>적용 세율: 3억 이하 22%, 초과 27.5%</div>", unsafe_allow_html=True)
        st.markdown("<div class='tax-description'>주식을 매각하여 발생한 이익(양도차익)에 대해 부과되는 세금입니다. 기본공제 250만원이 적용됩니다.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>청산소득세</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-amount'>{format_number(current_tax_details['totalTax'])}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-rate'>법인세 + 배당소득세 15.4%</div>", unsafe_allow_html=True)
        st.markdown("<div class='tax-description'>법인 청산 시 발생하는 세금으로, 법인세와 잔여재산 분배에 따른 배당소득세로 구성됩니다.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 세금 비교 분석
    st.markdown("""
    <div class="tax-info-section">
        <h3>세금 비교 분석</h3>
        <p>위 세금 계산 결과를 바탕으로 자산 처분 방법에 따른 세금 부담을 비교할 수 있습니다.</p>
    """, unsafe_allow_html=True)
    
    # 세금 비교 테이블
    tax_data = [
        ["증여세", format_number(current_tax_details['inheritanceTax']), f"{current_tax_details['inheritanceRate']:.1f}%"],
        ["양도소득세", format_number(current_tax_details['transferTax']), f"{current_tax_details['transferRate']:.1f}%"],
        ["청산소득세", format_number(current_tax_details['totalTax']), f"{current_tax_details['liquidationRate']:.1f}%"]
    ]
    
    # 최적의 세금 옵션 찾기
    min_tax = min(current_tax_details['inheritanceTax'], current_tax_details['transferTax'], current_tax_details['totalTax'])
    best_option = ""
    if min_tax == current_tax_details['inheritanceTax']:
        best_option = "증여세"
    elif min_tax == current_tax_details['transferTax']:
        best_option = "양도소득세"
    else:
        best_option = "청산소득세"
    
    st.markdown(f"""
        <p>현재 기업가치 수준에서는 <b>{best_option}</b>가 세금 부담이 가장 적습니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 계산 방법 상세 설명
    st.markdown("<h3>계산 방법 상세 설명</h3>", unsafe_allow_html=True)
    
    # 증여세 계산 방법
    st.markdown("""
    <div class="tax-info-section">
        <h4>증여세 계산:</h4>
        <ul>
            <li>1억 이하: 10%</li>
            <li>1억~5억: 20%</li>
            <li>5억~10억: 30%</li>
            <li>10억~30억: 40%</li>
            <li>30억 초과: 50%</li>
        </ul>
    """, unsafe_allow_html=True)
    
    # 구간별 계산 예시 
    if len(current_tax_details["inheritanceDetails"]) > 0:
        calculation_text = ""
        for detail in current_tax_details["inheritanceDetails"]:
            calculation_text += f"({format_original(detail['amount'])}원 × {int(detail['rate']*100)}%) + "
        calculation_text = calculation_text[:-3]  # 마지막 "+ " 제거
        
        st.markdown(f"""
        <div class="calculation-example">
            예: {format_original(stock_value['ownedValue'])}원의 경우 = {calculation_text} = {format_original(current_tax_details['inheritanceTax'])}원
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 양도소득세 계산 방법
    st.markdown("""
    <div class="tax-info-section">
        <h4>양도소득세 계산:</h4>
        <ul>
            <li>양도차익 = 양도가액 - 취득가액</li>
            <li>과세표준 = 양도차익 - 기본공제 250만원</li>
            <li>3억 이하: 22%, 3억 초과: 27.5%의 세율 적용</li>
        </ul>
    """, unsafe_allow_html=True)
    
    # 양도소득세 계산 예시
    st.markdown(f"""
        <div class="calculation-example">
            양도차익: {format_original(stock_value['ownedValue'])} - {format_original(current_tax_details['acquisitionValue'])} = {format_original(current_tax_details['transferProfit'])}원<br>
            과세표준: {format_original(current_tax_details['transferProfit'])} - 2,500,000 = {format_original(current_tax_details['transferProfit'] - 2500000)}원<br>
            {"세액: " + format_original(current_tax_details['transferProfit'] - 2500000) + " × 22% = " + format_original(current_tax_details['transferTax']) + "원" if current_tax_details['transferProfit'] - 2500000 <= 300000000 else 
            "3억원 이하: 300,000,000 × 22% = " + format_original(300000000 * 0.22) + "원<br>" + 
            "3억원 초과: " + format_original(current_tax_details['transferProfit'] - 2500000 - 300000000) + " × 27.5% = " + format_original((current_tax_details['transferProfit'] - 2500000 - 300000000) * 0.275) + "원<br>" +
            "합계: " + format_original(current_tax_details['transferTax']) + "원"}
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 청산소득세 계산 방법
    st.markdown("""
    <div class="tax-info-section">
        <h4>청산소득세 계산:</h4>
        <ul>
            <li>법인세: 2억 이하 10%, 2억~200억 20%, 200억~3,000억 22%, 3,000억 초과 25%</li>
            <li>배당소득세: (잔여재산 - 법인세) × 15.4%</li>
            <li>총 세금: 법인세 + 배당소득세</li>
        </ul>
    """, unsafe_allow_html=True)
    
    # 청산소득세 계산 예시
    st.markdown(f"""
        <div class="calculation-example">
            법인세: {"2억 이하 " + format_original(stock_value['ownedValue']) + " × 10% = " + format_original(current_tax_details['corporateTax']) + "원" if stock_value['ownedValue'] <= 200000000 else
            "2억원 × 10% + (" + format_original(stock_value['ownedValue'] - 200000000) + " × 20%) = " + format_original(current_tax_details['corporateTax']) + "원" if stock_value['ownedValue'] <= 20000000000 else
            "복합세율 적용 = " + format_original(current_tax_details['corporateTax']) + "원"}<br>
            배당소득세: ({format_original(stock_value['ownedValue'])} - {format_original(current_tax_details['corporateTax'])}) × 15.4% = {format_original(current_tax_details['liquidationTax'])}원<br>
            총 세금: {format_original(current_tax_details['corporateTax'])} + {format_original(current_tax_details['liquidationTax'])} = {format_original(current_tax_details['totalTax'])}원
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 세금 최적화 참고사항
    st.markdown("""
    <div class="summary-box">
        <h4>세금 최적화 참고사항</h4>
        <p>상황에 따라 가장 유리한 방법을 선택하는 것이 중요합니다. 다음 사항을 고려하세요:</p>
        <ul>
            <li>증여세는 높은 누진세율(최대 50%)이 적용되지만, 한 번에 세금 부담을 해결할 수 있습니다.</li>
            <li>양도소득세는 취득가액과 기본공제가 적용되어 실제 세금 부담이 낮아질 수 있습니다.</li>
            <li>청산소득세는 법인세와 배당소득세가 이중으로 과세되나, 법인 규모에 따라 유리할 수 있습니다.</li>
        </ul>
        <p>주의: 실제 세금 계획은 개인 상황, 자산 구성, 사업 목적 등을 고려해 세무 전문가와 상담해야 합니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 참고사항
    st.info("※ 실제 세금은 개인 상황, 보유기간, 대주주 여부 등에 따라 달라질 수 있습니다.")
    
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
