import streamlit as st
import pandas as pd
import locale
import numpy as np
from datetime import datetime
import io
import base64

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
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 15px;
    }
    .tax-amount {
        font-size: 26px;
        font-weight: 600;
        margin: 10px 0;
    }
    .tax-rate {
        color: #28a745;
        font-weight: 500;
        margin-bottom: 10px;
    }
    .tax-description {
        color: #555;
        margin: 10px 0;
        font-size: 14px;
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
    /* 균형잡힌 테이블 스타일 */
    .balanced-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 15px;
    }
    .balanced-table th, .balanced-table td {
        padding: 12px;
        border: 1px solid #e0e0e0;
        text-align: left;
    }
    .balanced-table th {
        background-color: #f5f9ff;
        font-weight: 500;
        color: #333;
    }
    .balanced-table td.label {
        width: 25%;
        font-weight: 500;
    }
    .balanced-table td.value {
        width: 25%;
        text-align: right;
        color: #0066cc;
        font-weight: 500;
    }
    /* 세금 비교 테이블 스타일 */
    .tax-comparison {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    .tax-comparison h3 {
        text-align: center;
        margin-bottom: 20px;
        color: #2c3e50;
        font-weight: 600;
        font-size: 20px;
    }
    .tax-compare-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        font-size: 15px;
    }
    .tax-compare-table th {
        background-color: #f0f7fb;
        border: 1px solid #e0e0e0;
        padding: 12px;
        text-align: center;
        font-weight: 500;
        color: #333;
    }
    .tax-compare-table td {
        padding: 12px;
        border: 1px solid #e0e0e0;
        text-align: center;
        font-weight: normal;
    }
    .tax-compare-table td.tax-amount {
        text-align: right;
        font-weight: 500;
    }
    .tax-compare-table tr.highlight {
        background-color: #f0fff0;
    }
    .best-option-box {
        text-align: center;
        margin: 15px 0;
        padding: 12px;
        background-color: #f8f9fa;
        border-radius: 8px;
        border-left: 5px solid #28a745;
    }
    .best-option-text {
        font-size: 16px;
        margin: 0;
        font-weight: 500;
    }
    .download-section {
        background-color: #f0f7fb;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
    }
    .alert-warning {
        background-color: #fff3cd;
        color: #856404;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .alert-info {
        background-color: #d1ecf1;
        color: #0c5460;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# PDF 생성 함수
def generate_pdf(tax_details, company_name, owned_shares, share_price, eval_date, is_family_corp):
    try:
        # FPDF 라이브러리 자동 설치 시도
        try:
            from fpdf import FPDF
        except ImportError:
            try:
                import subprocess
                subprocess.check_call(['pip', 'install', 'fpdf'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                from fpdf import FPDF
            except:
                return None
        
        # PDF 객체 생성
        pdf = FPDF()
        pdf.add_page()
        
        # 기본 폰트 설정 (한글 지원 제한)
        pdf.set_font('Arial', 'B', 16)
        
        # 제목
        pdf.cell(190, 10, 'Tax Calculation Report', 0, 1, 'C')
        pdf.ln(5)
        
        # 회사 정보
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(190, 10, f'Company: {company_name}', 0, 1)
        pdf.cell(190, 10, f'Evaluation Date: {eval_date.strftime("%Y-%m-%d")}', 0, 1)
        pdf.ln(5)
        
        # 주식 정보
        pdf.set_font('Arial', '', 11)
        pdf.cell(190, 10, f'Owned Shares: {simple_format(owned_shares)} shares', 0, 1)
        pdf.cell(190, 10, f'Share Price: {simple_format(share_price)} KRW', 0, 1)
        pdf.ln(5)
        
        # 세금 정보
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(190, 10, 'Tax Calculation Results:', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        # 증여세
        pdf.cell(60, 10, 'Gift Tax:', 0, 0)
        pdf.cell(65, 10, f'{simple_format(tax_details["inheritanceTax"])} KRW', 0, 0)
        pdf.cell(65, 10, f'Effective Rate: {tax_details["inheritanceRate"]:.1f}%', 0, 1)
        
        # 양도소득세
        pdf.cell(60, 10, 'Capital Gains Tax (incl. Local Tax):', 0, 0)
        pdf.cell(65, 10, f'{simple_format(tax_details["transferTax"])} KRW', 0, 0)
        pdf.cell(65, 10, f'Effective Rate: {tax_details["transferRate"]:.1f}%', 0, 1)
        
        # 청산소득세
        pdf.cell(60, 10, 'Liquidation Tax:', 0, 0)
        pdf.cell(65, 10, f'{simple_format(tax_details["liquidationTax"])} KRW', 0, 0)
        pdf.cell(65, 10, f'Effective Rate: {tax_details["liquidationRate"]:.1f}%', 0, 1)
        
        # 최적 세금 옵션
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        
        # 최적의 세금 옵션 찾기
        min_tax = min(tax_details['inheritanceTax'], tax_details['transferTax'], tax_details['liquidationTax'])
        
        if min_tax == tax_details['inheritanceTax']:
            best_option = "Gift Tax"
        elif min_tax == tax_details['transferTax']:
            best_option = "Capital Gains Tax"
        else:
            best_option = "Liquidation Tax"
            
        pdf.cell(190, 10, f'Best Tax Option: {best_option}', 0, 1)
        
        # 생성일
        pdf.ln(10)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(190, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d")}', 0, 1)
        
        # PDF를 바이트로 변환
        try:
            return pdf.output(dest='S').encode('latin-1')
        except Exception as e:
            return None
    except Exception as e:
        return None

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

# 양도소득세 계산 함수 - 오류 수정
def calculate_transfer_tax(gain, acquisition_value):
    # 양도차익 계산 - 수정된 부분
    transfer_profit = gain - acquisition_value
    
    # 기본공제 250만원 적용
    taxable_gain = max(0, transfer_profit - 2500000)
    
    calculation_steps = []
    # 양도차익 계산 단계 - 수정된 부분
    calculation_steps.append({"description": "양도차익 계산", "detail": f"양도가액({simple_format(gain)}원) - 취득가액({simple_format(acquisition_value)}원) = {simple_format(transfer_profit)}원"})
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
    effective_rate = (tax / transfer_profit) * 100 if transfer_profit > 0 else 0
    
    return tax, calculation_steps, effective_rate, transfer_profit

# 청산소득세 계산 함수 - 이미지에 맞게 수정
def calculate_liquidation_tax(total_value, acquisition_value, is_family_corp=False):
    # 청산소득금액 계산 - 자기자본(취득가액) 차감
    income = total_value - acquisition_value
    
    calculation_steps = []
    calculation_steps.append({"description": "청산소득금액", "detail": f"보유주식가치({simple_format(total_value)}원) - 자기자본({simple_format(acquisition_value)}원) = {simple_format(income)}원"})
    
    # 법인세 계산 - 일반 법인인 경우 (가족법인 아닌 경우)
    if not is_family_corp:
        if income <= 200000000:  # 2억원 이하
            corporate_tax = income * 0.09
            calculation_steps.append({"description": "법인세(2억 이하)", "detail": f"{simple_format(income)}원 × 9% = {simple_format(corporate_tax)}원"})
        else:  # 2억원 초과
            # 2억원까지는 9%, 나머지는 19% 적용
            corporate_tax = 200000000 * 0.09 + (income - 200000000) * 0.19
            calculation_steps.append({"description": "법인세", "detail": f"2억원 × 9% + {simple_format(income - 200000000)}원 × 19% = {simple_format(corporate_tax)}원"})
    else:  # 가족법인인 경우
        # 가족법인 법인세율 (19%~24% 구간별 적용)
        if income <= 20000000000:  # 200억 이하
            corporate_tax = income * 0.19
            calculation_steps.append({"description": "법인세(가족법인, 200억 이하)", "detail": f"{simple_format(income)}원 × 19% = {simple_format(corporate_tax)}원"})
        elif income <= 300000000000:  # 200억 초과 3000억 이하
            corporate_tax = 20000000000 * 0.19 + (income - 20000000000) * 0.21
            calculation_steps.append({"description": "법인세(가족법인)", "detail": f"200억원 × 19% + {simple_format(income - 20000000000)}원 × 21% = {simple_format(corporate_tax)}원"})
        else:  # 3000억 초과
            corporate_tax = 20000000000 * 0.19 + (300000000000 - 20000000000) * 0.21 + (income - 300000000000) * 0.24
            calculation_steps.append({"description": "법인세(가족법인)", "detail": f"200억원 × 19% + 2,800억원 × 21% + {simple_format(income - 300000000000)}원 × 24% = {simple_format(corporate_tax)}원"})
    
    # 배당소득세 계산
    after_tax = income - corporate_tax
    dividend_tax = after_tax * 0.154
    calculation_steps.append({"description": "배당소득세", "detail": f"({simple_format(income)}원 - {simple_format(corporate_tax)}원) × 15.4% = {simple_format(dividend_tax)}원"})
    
    total_tax = corporate_tax + dividend_tax
    calculation_steps.append({"description": "총 세금", "detail": f"{simple_format(corporate_tax)}원 + {simple_format(dividend_tax)}원 = {simple_format(total_tax)}원"})
    
    # 실효세율 계산
    effective_rate = (total_tax / income) * 100 if income > 0 else 0
    
    return corporate_tax, dividend_tax, total_tax, calculation_steps, effective_rate, income

# 세금 계산 함수 (수정)
def calculate_tax_details(value, owned_shares, share_price, is_family_corp=False):
    if not value:
        return None
    
    owned_value = value["ownedValue"]
    
    # 상속증여세
    inheritance_tax, inheritance_steps, inheritance_rate = calculate_inheritance_tax(owned_value)
    
    # 양도소득세 - 함수 수정됨
    acquisition_value = owned_shares * share_price
    transfer_tax, transfer_steps, transfer_rate, transfer_profit = calculate_transfer_tax(owned_value, acquisition_value)
    
    # 청산소득세 - 수정된 함수 사용
    corporate_tax, dividend_tax, total_liquidation_tax, liquidation_steps, liquidation_rate, liquidation_income = calculate_liquidation_tax(owned_value, acquisition_value, is_family_corp)
    
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
        "transferProfit": transfer_profit,
        "liquidationIncome": liquidation_income,
        "corporateTax": corporate_tax,
        "dividendTax": dividend_tax
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
    
    # 평가된 주식 가치 정보 표시 (균형있는 테이블 형식)
    st.markdown("<h3>평가된 주식 가치</h3>", unsafe_allow_html=True)
    
    # 균형있는 테이블 스타일로 업데이트
    st.markdown(f"""
    <table class="balanced-table">
        <tr>
            <th>회사명:</th>
            <td class="value">{company_name}</td>
            <th>회사 총가치:</th>
            <td class="value">{simple_format(stock_value['totalValue'])}원</td>
        </tr>
        <tr>
            <th>주당 평가액:</th>
            <td class="value">{simple_format(stock_value['finalValue'])}원</td>
            <th>대표이사 보유주식 가치:</th>
            <td class="value">{simple_format(stock_value['ownedValue'])}원</td>
        </tr>
        <tr>
            <th>평가 기준일:</th>
            <td class="value">{eval_date.strftime('%Y년 %m월 %d일')}</td>
            <th>적용 평가방식:</th>
            <td class="value">{stock_value['methodText']}</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)
    
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
    
    # 양도소득세 카드 - "지방소득세 포함" 추가
    with col2:
        st.markdown("<div class='tax-card'>", unsafe_allow_html=True)
        st.markdown("<div class='tax-title'>양도소득세(지방소득세 포함)</div>", unsafe_allow_html=True)
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
        
        st.markdown(f"<p><b>총 양도소득세(지방소득세 포함): {simple_format(tax_details['transferTax'])}원</b> (실효세율: {tax_details['transferRate']:.1f}%)</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 청산소득세 계산 세부내역 (수정됨)
    with st.expander("청산소득세 계산 세부내역"):
        st.markdown("<div class='calculation-box'>", unsafe_allow_html=True)
        
        for step in tax_details['liquidationSteps']:
            st.markdown(f"<div class='calculation-step'>{step['description']}: {step['detail']}</div>", unsafe_allow_html=True)
        
        st.markdown(f"<p><b>총 청산소득세: {simple_format(tax_details['liquidationTax'])}원</b> (실효세율: {tax_details['liquidationRate']:.1f}%)</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 세금 비교 분석 (균형있게 조정)
    st.markdown("<div class='tax-comparison'>", unsafe_allow_html=True)
    st.markdown("<h3>세금 비교 분석</h3>", unsafe_allow_html=True)
    
    # 최적의 세금 옵션 찾기
    min_tax = min(tax_details['inheritanceTax'], tax_details['transferTax'], tax_details['liquidationTax'])
    
    if min_tax == tax_details['inheritanceTax']:
        best_option = "증여세"
        best_color = "#4CAF50"
        inherit_class = "highlight"
        transfer_class = ""
        liquid_class = ""
    elif min_tax == tax_details['transferTax']:
        best_option = "양도소득세"
        best_color = "#2196F3"
        inherit_class = ""
        transfer_class = "highlight"
        liquid_class = ""
    else:
        best_option = "청산소득세"
        best_color = "#9C27B0"
        inherit_class = ""
        transfer_class = ""
        liquid_class = "highlight"
    
    # 최적 옵션 표시 (적절한 사이즈로)
    st.markdown(f"""
    <div class="best-option-box" style="border-left: 5px solid {best_color};">
        <p class="best-option-text">현재 기업가치 수준에서는 <span style="font-weight: bold; color: {best_color};">{best_option}</span>가 세금 부담이 가장 적습니다.</p>
    </div>
    """, unsafe_allow
