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
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
    .tax-info-section {
        background-color: #f0f7fb;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        border-left: 4px solid #ffc107;
        padding: 15px;
        margin: 15px 0;
        border-radius: 5px;
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
    .tax-comparison {
        background-color: #e9f7ef;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# 페이지 헤더
st.title("현시점 세금 계산")

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

# 세금 계산 함수
def calculate_tax_details(value, owned_shares, share_price, is_family_corp=False):
    if not value:
        return None
    
    owned_value = value["ownedValue"]
    
    # 상속증여세
    inheritance_tax, inheritance_steps, inheritance_rate = calculate_inheritance_tax(owned_value)
    
    # 양도소득세
    acquisition_value = owned_shares * share_price
    transfer_profit = owned_value - acquisition_value
    transfer_tax, transfer_steps, transfer_rate = calculate_transfer_tax(transfer_profit, acquisition_value)
    
    # 청산소득세
    corporate_tax, dividend_tax, total_liquidation_tax, liquidation_steps, liquidation_rate = calculate_liquidation_tax(owned_value, acquisition_value, is_family_corp)
    
    return {
        "inheritanceTax": inheritance_tax,
        "transferTax": transfer_tax,
        "liquidationTax": total_liquidation_tax,
        "inheritanceSteps": inheritance_steps,
        "transferSteps": transfer_steps,
        "liquidationSteps": liquidation_steps,
        "inheritanceRate": inheritance_rate,
        "transferRate": transfer_rate,
        "liquidationRate": liquidation_rate,
        "acquisitionValue": acquisition_value,
        "transferProfit": transfer_profit
    }

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
    
    # 기업 유형 선택
    is_family_corp = st.checkbox("가족법인 여부 (부동산임대업 주업, 지배주주 50% 초과, 상시근로자 5명 미만)", 
                              help="2025년부터 가족법인(부동산임대업 등 주업)에 대해서는 법인세 최저세율이 19%로 적용됩니다")
    
    # 평가된 주식 가치 정보 표시
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
    
    # 세금 계산
    tax_details = calculate_tax_details(stock_value, owned_shares, share_price, is_family_corp)
    
    # 세금 결과 카드 표시
    col1, col2, col3 = st.columns(3)
    
    # 증여세 카드
    with col1:
        st.markdown("<div class='tax-card'>", unsafe_allow_html=True)
        st.markdown("<div class='tax-title'>증여세</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-amount'>{simple_format(tax_details['inheritanceTax'])}원</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-rate'>적용 세율: 누진세율 (10%~50%)</div>", unsafe_allow_html=True)
        st.markdown("<div class='tax-description'>주식을 타인에게 무상으로 증여할 경우 발생하는 세금입니다. 증여 받은 사람이 납부합니다.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 양도소득세 카드
    with col2:
        st.markdown("<div class='tax-card'>", unsafe_allow_html=True)
        st.markdown("<div class='tax-title'>양도소득세</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-amount'>{simple_format(tax_details['transferTax'])}원</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-rate'>적용 세율: 3억 이하 22%, 초과 27.5%</div>", unsafe_allow_html=True)
        st.markdown("<div class='tax-description'>주식을 매각하여 발생한 이익(양도차익)에 대해 부과되는 세금입니다. 기본공제 250만원이 적용됩니다.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 청산소득세 카드
    with col3:
        st.markdown("<div class='tax-card'>", unsafe_allow_html=True)
        st.markdown("<div class='tax-title'>청산소득세</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-amount'>{simple_format(tax_details['liquidationTax'])}원</div>", unsafe_allow_html=True)
        if is_family_corp:
            st.markdown(f"<div class='tax-rate'>법인세(19~24%) + 배당세 15.4%</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='tax-rate'>법인세(9~24%) + 배당세 15.4%</div>", unsafe_allow_html=True)
        st.markdown("<div class='tax-description'>법인 청산 시 발생하는 세금으로, 법인세와 잔여재산 분배에 따른 배당소득세로 구성됩니다.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 증여세 계산 세부내역
    with st.expander("증여세 계산 세부내역"):
        st.markdown("<div class='calculation-box'>", unsafe_allow_html=True)
        st.markdown(f"<p>과세표준: {simple_format(stock_value['ownedValue'])}원</p>", unsafe_allow_html=True)
        
        for step in tax_details['inheritanceSteps']:
            st.markdown(f"<div class='calculation-step'>{step['bracket']}: {simple_format(step['amount'])}원 × {int(step['rate']*100)}% = {simple_format(step['tax'])}원</div>", unsafe_allow_html=True)
        
        st.markdown(f"<p><b>총 증여세: {simple_format(tax_details['inheritanceTax'])}원</b> (실효세율: {tax_details['inheritanceRate']:.1f}%)</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 양도소득세 계산 세부내역
    with st.expander("양도소득세 계산 세부내역"):
        st.markdown("<div class='calculation-box'>", unsafe_allow_html=True)
        
        for step in tax_details['transferSteps']:
            st.markdown(f"<div class='calculation-step'>{step['description']}: {step['detail']}</div>", unsafe_allow_html=True)
        
        st.markdown(f"<p><b>총 양도소득세: {simple_format(tax_details['transferTax'])}원</b> (실효세율: {tax_details['transferRate']:.1f}%)</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 청산소득세 계산 세부내역
    with st.expander("청산소득세 계산 세부내역"):
        st.markdown("<div class='calculation-box'>", unsafe_allow_html=True)
        
        for step in tax_details['liquidationSteps']:
            st.markdown(f"<div class='calculation-step'>{step['description']}: {step['detail']}</div>", unsafe_allow_html=True)
        
        st.markdown(f"<p><b>총 청산소득세: {simple_format(tax_details['liquidationTax'])}원</b> (실효세율: {tax_details['liquidationRate']:.1f}%)</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 세금 비교 분석
    st.markdown("<div class='tax-comparison'>", unsafe_allow_html=True)
    st.markdown("<h3>세금 비교 분석</h3>", unsafe_allow_html=True)
    
    # 최적의 세금 옵션 찾기
    min_tax = min(tax_details['inheritanceTax'], tax_details['transferTax'], tax_details['liquidationTax'])
    
    if min_tax == tax_details['inheritanceTax']:
        best_option = "증여세"
    elif min_tax == tax_details['transferTax']:
        best_option = "양도소득세"
    else:
        best_option = "청산소득세"
    
    st.markdown(f"<p>현재 기업가치 수준에서는 <b>{best_option}</b>가 세금 부담이 가장 적습니다.</p>", unsafe_allow_html=True)
    
    # 세금 비교 테이블
    st.markdown("""
    <table class="tax-compare-table">
        <tr>
            <th>세금 유형</th>
            <th>세액</th>
            <th>실효세율</th>
        </tr>
        <tr>
            <td>증여세</td>
            <td>{:,}원</td>
            <td>{:.1f}%</td>
        </tr>
        <tr>
            <td>양도소득세</td>
            <td>{:,}원</td>
            <td>{:.1f}%</td>
        </tr>
        <tr>
            <td>청산소득세</td>
            <td>{:,}원</td>
            <td>{:.1f}%</td>
        </tr>
    </table>
    """.format(
        tax_details['inheritanceTax'],
        tax_details['inheritanceRate'],
        tax_details['transferTax'],
        tax_details['transferRate'],
        tax_details['liquidationTax'],
        tax_details['liquidationRate']
    ), unsafe_allow_html=True)
    
    st.markdown("<p>주의: 이는 단순 세금 비교이며, 실제 의사결정은 개인 상황, 자산 구성, 사업 목표 등을 고려해야 합니다.</p>", unsafe_allow_html=True)
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
    st.markdown("<div class='warning-box'>", unsafe_allow_html=True)
    st.markdown("※ 이 계산기의 세금 계산은 참고용으로만 사용하시기 바랍니다. 실제 세금은 개인 상황, 보유기간, 대주주 여부, 사업 형태 등에 따라 달라질 수 있습니다.", unsafe_allow_html=True)
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

    # 다운로드 섹션 추가
    st.markdown("---")
    st.subheader("📥 세금 계산 결과 다운로드")

    col1, col2 = st.columns(2)

    # HTML 보고서 다운로드
    with col1:
        if st.button("HTML 보고서 다운로드", use_container_width=True):
            # HTML 내용 생성
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>비상장주식 세금 분석 - {company_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                    h1 {{ color: #2c3e50; text-align: center; }}
                    h2 {{ color: #3498db; margin-top: 20px; }}
                    .info {{ margin-bottom: 5px; }}
                    .tax-box {{ background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #3498db; }}
                    .result {{ margin-top: 10px; font-weight: bold; }}
                    .results-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    .results-table th, .results-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    .results-table th {{ background-color: #f2f2f2; }}
                    .best-option {{ background-color: #e6f7e6; padding: 10px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #28a745; }}
                </style>
            </head>
            <body>
                <h1>비상장주식 세금 분석 보고서</h1>
                
                <h2>기본 정보</h2>
                <div class="info">회사명: {company_name}</div>
                <div class="info">평가 기준일: {eval_date.strftime('%Y년 %m월 %d일')}</div>
                <div class="info">주당 평가액: {simple_format(stock_value["finalValue"])}원</div>
                <div class="info">회사 총 가치: {simple_format(stock_value["totalValue"])}원</div>
                <div class="info">대표이사 보유주식 가치: {simple_format(stock_value["ownedValue"])}원</div>
                
                <h2>세금 분석 결과</h2>
                <table class="results-table">
                    <tr>
                        <th>세금 유형</th>
                        <th>세액</th>
                        <th>실효세율</th>
                    </tr>
                    <tr>
                        <td>증여세</td>
                        <td>{simple_format(tax_details['inheritanceTax'])}원</td>
                        <td>{tax_details['inheritanceRate']:.1f}%</td>
                    </tr>
                    <tr>
                        <td>양도소득세</td>
                        <td>{simple_format(tax_details['transferTax'])}원</td>
                        <td>{tax_details['transferRate']:.1f}%</td>
                    </tr>
                    <tr>
                        <td>청산소득세</td>
                        <td>{simple_format(tax_details['liquidationTax'])}원</td>
                        <td>{tax_details['liquidationRate']:.1f}%</td>
                    </tr>
                </table>
                
                <div class="best-option">
                    <h3>최적의 세금 옵션: {best_option}</h3>
                    <p>현재 기업가치 수준에서는 {best_option}가 세금 부담이 가장 적습니다.</p>
                </div>
                
                <h2>세금 계산 세부내역</h2>
                
                <div class="tax-box">
                    <h3>증여세 계산</h3>
                    <p>과세표준: {simple_format(stock_value['ownedValue'])}원</p>
                    <ul>
                        {''.join([f"<li>{step['bracket']}: {simple_format(step['amount'])}원 × {int(step['rate']*100)}% = {simple_format(step['tax'])}원</li>" for step in tax_details['inheritanceSteps']])}
                    </ul>
                    <p><b>총 증여세: {simple_format(tax_details['inheritanceTax'])}원</b> (실효세율: {tax_details['inheritanceRate']:.1f}%)</p>
                </div>
                
                <div class="tax-box">
                    <h3>양도소득세 계산</h3>
                    <ul>
                        {''.join([f"<li>{step['description']}: {step['detail']}</li>" for step in tax_details['transferSteps']])}
                    </ul>
                    <p><b>총 양도소득세: {simple_format(tax_details['transferTax'])}원</b> (실효세율: {tax_details['transferRate']:.1f}%)</p>
                </div>
                
                <div class="tax-box">
                    <h3>청산소득세 계산</h3>
                    <ul>
                        {''.join([f"<li>{step['description']}: {step['detail']}</li>" for step in tax_details['liquidationSteps']])}
                    </ul>
                    <p><b>총 청산소득세: {simple_format(tax_details['liquidationTax'])}원</b> (실효세율: {tax_details['liquidationRate']:.1f}%)</p>
                </div>
                
                <div style="margin-top: 30px; padding: 10px; background-color: #fff3cd; border-radius: 5px;">
                    <p><b>참고:</b> 이 보고서의 세금 계산은 참고용으로만 사용하시기 바랍니다. 실제 세금은 개인 상황, 보유기간, 대주주 여부, 사업 형태 등에 따라 달라질 수 있습니다.</p>
                </div>
                
                <div style="margin-top: 30px; text-align: center; color: #777; font-size: 0.9em;">
                    <p>생성일: {datetime.now().strftime('%Y년 %m월 %d일')}</p>
                </div>
            </body>
            </html>
            """
            
            st.download_button(
                label="📄 HTML 파일 저장하기",
                data=html_content,
                file_name=f"세금분석_{company_name}_{eval_date.strftime('%Y%m%d')}.html",
                mime="text/html"
            )

    # CSV 다운로드
    with col2:
        if st.button("CSV 데이터 다운로드", use_container_width=True):
            # CSV 데이터 생성
            data = {
                '항목': [
                    '회사명', '평가 기준일', '주당 평가액', '회사 총가치', '대표이사 보유주식 가치',
                    '증여세', '증여세 실효세율', 
                    '양도소득세', '양도소득세 실효세율', 
                    '청산소득세', '청산소득세 실효세율',
                    '최적 세금 옵션'
                ],
                '값': [
                    company_name, str(eval_date), stock_value['finalValue'], stock_value['totalValue'], stock_value['ownedValue'],
                    tax_details['inheritanceTax'], f"{tax_details['inheritanceRate']:.1f}%",
                    tax_details['transferTax'], f"{tax_details['transferRate']:.1f}%",
                    tax_details['liquidationTax'], f"{tax_details['liquidationRate']:.1f}%",
                    best_option
                ]
            }
            
            # DataFrame 생성 후 CSV로 변환
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📄 CSV 파일 저장하기",
                data=csv,
                file_name=f"세금분석_{company_name}_{eval_date.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
