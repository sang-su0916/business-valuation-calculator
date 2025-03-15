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
   .tax-compare {
       background-color: #f8f9fa;
       border-radius: 5px;
       padding: 15px;
       margin: 15px 0;
   }
   .tax-compare-header {
       font-size: 1.5rem;
       font-weight: bold;
       margin-bottom: 15px;
   }
   .tax-increase {
       color: #e74c3c;
       font-weight: bold;
   }
   .tax-optimize {
       background-color: #e9fcef;
       border-radius: 5px;
       padding: 15px;
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
   .table-container {
       overflow-x: auto;
   }
   .blue-text {
       color: #0066cc;
       font-weight: bold;
   }
</style>
""", unsafe_allow_html=True)

# 페이지 헤더
st.title("미래 세금 계산")

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
   
   tax_formula.append(f"양도차익: {simple_format(gain)}원 (양도가액 - 취득가액 {simple_format(acquisition_value)}원)")
   tax_formula.append(f"기본공제: 2,500,000원")
   tax_formula.append(f"과세표준: {simple_format(taxable_gain)}원")
   
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
def calculate_liquidation_tax(income, acquisition_value, is_family_corp=False):
   # 법인세 누진세율 적용 (2025년 기준)
   corporate_tax = 0
   
   tax_formula = []
   tax_formula.append(f"청산소득금액: {simple_format(income)}원 (잔여재산 - 자기자본 {simple_format(acquisition_value)}원)")
   
   # 법인세 계산 (2025년 세율 적용)
   if is_family_corp:
       # 가족법인(부동산임대업 주업)의 경우 2025년부터 최저세율 19% 적용
       if income <= 20000000000:  # 200억 이하
           corporate_tax = income * 0.19
           tax_formula.append(f"법인세(가족법인, 200억 이하): {simple_format(income)} × 19% = {simple_format(corporate_tax)}원")
       elif income <= 300000000000:  # 200억 초과 3000억 이하
           corporate_tax = 20000000000 * 0.19 + (income - 20000000000) * 0.21
           tax_formula.append(f"법인세(가족법인): 200억원 × 19% + {simple_format(income - 20000000000)} × 21% = {simple_format(corporate_tax)}원")
       else:  # 3000억 초과
           corporate_tax = 20000000000 * 0.19 + (300000000000 - 20000000000) * 0.21 + (income - 300000000000) * 0.24
           tax_formula.append(f"법인세(가족법인): 200억원 × 19% + 2,800억원 × 21% + {simple_format(income - 300000000000)} × 24% = {simple_format(corporate_tax)}원")
   else:
       # 일반법인 세율 적용
       if income <= 200000000:  # 2억 이하
           corporate_tax = income * 0.09
           tax_formula.append(f"법인세(2억 이하): {simple_format(income)} × 9% = {simple_format(corporate_tax)}원")
       elif income <= 20000000000:  # 2억 초과 200억 이하
           corporate_tax = 200000000 * 0.09 + (income - 200000000) * 0.19
           tax_formula.append(f"법인세: 2억원 × 9% + {simple_format(income - 200000000)} × 19% = {simple_format(corporate_tax)}원")
       elif income <= 300000000000:  # 200억 초과 3000억 이하
           corporate_tax = 200000000 * 0.09 + (20000000000 - 200000000) * 0.19 + (income - 20000000000) * 0.21
           tax_formula.append(f"법인세: 2억원 × 9% + 198억원 × 19% + {simple_format(income - 20000000000)} × 21% = {simple_format(corporate_tax)}원")
       else:  # 3000억 초과
           corporate_tax = 200000000 * 0.09 + (20000000000 - 200000000) * 0.19 + (300000000000 - 20000000000) * 0.21 + (income - 300000000000) * 0.24
           tax_formula.append(f"법인세: 2억원 × 9% + 198억원 × 19% + 2,800억원 × 21% + {simple_format(income - 300000000000)} × 24% = {simple_format(corporate_tax)}원")
   
   # 배당소득세 계산
   after_tax = income - corporate_tax
   dividend_tax = after_tax * 0.154  # 15.4%
   tax_formula.append(f"배당소득세: ({simple_format(income)} - {simple_format(corporate_tax)}) × 15.4% = {simple_format(dividend_tax)}원")
   
   total_tax = corporate_tax + dividend_tax
   tax_formula.append(f"총 세금: {simple_format(corporate_tax)} + {simple_format(dividend_tax)} = {simple_format(total_tax)}원")
   
   # 실효세율 계산
   effective_rate = (total_tax / income) * 100 if income > 0 else 0
   
   return corporate_tax, dividend_tax, total_tax, tax_formula, effective_rate

# 미래 세금 계산 함수 (연간 성장률 적용)
def calculate_future_tax(current_tax, growth_rate, years):
   return current_tax * (1 + growth_rate/100) ** years

# 세금 계산 함수
def calculate_tax_details(value, owned_shares, share_price, is_family_corp=False):
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
   corporate_tax, dividend_tax, total_liquidation_tax, liquidation_formula, liquidation_rate = calculate_liquidation_tax(owned_value, acquisition_value, is_family_corp)
   
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
       "ownedValue": owned_value,
       "isFamilyCorp": is_family_corp
   }

# 미래 세금 계산
def calculate_future_taxes(current_tax_details, future_value, growth_rate, years, is_family_corp=False):
   # 미래 회사 가치 계산
   future_owned_value = future_value["ownedValue"]
   
   # 미래 양도차익 계산 (취득가액은 현재와 동일하게 유지)
   future_transfer_profit = future_owned_value - current_tax_details["acquisitionValue"]
   
   # 미래 세금 계산
   future_inheritance_tax, _, future_inheritance_rate, _ = calculate_inheritance_tax(future_owned_value)
   future_transfer_tax, _, future_transfer_rate = calculate_transfer_tax(future_transfer_profit, current_tax_details["acquisitionValue"])
   _, _, future_liquidation_tax, _, future_liquidation_rate = calculate_liquidation_tax(future_owned_value, current_tax_details["acquisitionValue"], is_family_corp)
   
   # 세금 증가율 계산
   inheritance_increase = (future_inheritance_tax / current_tax_details["inheritanceTax"] - 1) * 100
   transfer_increase = (future_transfer_tax / current_tax_details["transferTax"] - 1) * 100
   liquidation_increase = (future_liquidation_tax / current_tax_details["totalTax"] - 1) * 100
   
   return {
       "inheritanceTax": future_inheritance_tax,
       "transferTax": future_transfer_tax,
       "liquidationTax": future_liquidation_tax,
       "inheritanceIncrease": inheritance_increase,
       "transferIncrease": transfer_increase,
       "liquidationIncrease": liquidation_increase,
       "inheritanceRate": future_inheritance_rate,
       "transferRate": future_transfer_rate,
       "liquidationRate": future_liquidation_rate
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
       # 기준 시점
       st.markdown(f"<div class='value-display'><span class='value-label'>기준 시점:</span> <span class='value-amount'>2025년</span></div>", unsafe_allow_html=True)
       # 기업 유형 선택 (일반 법인 또는 가족 법인)
       is_family_corp = st.checkbox("가족법인 여부 (부동산임대업 주업, 지배주주 50% 초과, 상시근로자 5명 미만)", 
                               help="2025년부터 가족법인(부동산임대업 등 주업)에 대해서는 법인세 최저세율이 19%로 적용됩니다")
   
   with col2:
       # 예측 기간
       years = st.number_input("예측 기간(년)", min_value=1, max_value=30, value=10)
       # 연간 성장률
       growth_rate = st.slider("적용 성장률 (%)", min_value=1, max_value=50, value=30, step=1)
   
   st.markdown("</div>", unsafe_allow_html=True)
   
   # 현재 세금 계산
   current_tax_details = calculate_tax_details(stock_value, owned_shares, share_price, is_family_corp)
   
   # 미래 회사 가치 계산
   future_date = eval_date + timedelta(days=365 * years)
   future_value = calculate_future_value(stock_value, growth_rate, years)
   
   # 미래 세금 계산
   future_taxes = calculate_future_taxes(current_tax_details, future_value, growth_rate, years, is_family_corp)
   
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
   st.markdown(f"""
   <tr>
       <td>증여세 (누진세율)</td>
       <td>{simple_format(current_tax_details['inheritanceTax'])}원</td>
       <td class="blue-text">{simple_format(future_taxes['inheritanceTax'])}원</td>
   </tr>
   """, unsafe_allow_html=True)
   
   # 양도소득세 비교 행
   st.markdown(f"""
   <tr>
       <td>양도소득세 (22%~27.5%)</td>
       <td>{simple_format(current_tax_details['transferTax'])}원</td>
       <td class="blue-text">{simple_format(future_taxes['transferTax'])}원</td>
   </tr>
   """, unsafe_allow_html=True)
   
   # 청산소득세 비교 행
   if is_family_corp:
       st.markdown(f"""
       <tr>
           <td>청산소득세 (법인세+배당세)</td>
           <td>{simple_format(current_tax_details['totalTax'])}원</td>
           <td class="blue-text">{simple_format(future_taxes['liquidationTax'])}원</td>
       </tr>
       """, unsafe_allow_html=True)
   else:
       st.markdown(f"""
       <tr>
           <td>청산소득세 (법인세+배당세)</td>
           <td>{simple_format(current_tax_details['totalTax'])}원</td>
           <td class="blue-text">{simple_format(future_taxes['liquidationTax'])}원</td>
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
   
    # 세금 증가 예상
    st.markdown("<div class='tax-info-section'>", unsafe_allow_html=True)
    st.markdown("<h3>세금 증가 예상</h3>", unsafe_allow_html=True)
    
    st.markdown("<ul>", unsafe_allow_html=True)
    st.markdown(f"<li>증여세: <span class='tax-increase'>+{future_taxes['inheritanceIncrease']:.1f}%</span> 증가</li>", unsafe_allow_html=True)
    st.markdown(f"<li>양도소득세: <span class='tax-increase'>+{future_taxes['transferIncrease']:.1f}%</span> 증가</li>", unsafe_allow_html=True)
    st.markdown(f"<li>청산소득세: <span class='tax-increase'>+{future_taxes['liquidationIncrease']:.1f}%</span> 증가</li>", unsafe_allow_html=True)
    st.markdown("</ul>", unsafe_allow_html=True)
    
    st.markdown("<p>기업 가치의 성장에 따라 세금 부담도 증가합니다. 누진세율이 적용되는 증여세의 경우 가치 증가 비율보다 세금 증가 비율이 더 높을 수 있습니다.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 세금 최적화 참고사항
    st.markdown("<div class='tax-optimize'>", unsafe_allow_html=True)
    st.markdown("<h3>세금 최적화 참고사항</h3>", unsafe_allow_html=True)
    
    # 현재와 미래 기준으로 세금 부담이 가장 낮은 방법 찾기
    current_min_tax = min(current_tax_details['inheritanceTax'], current_tax_details['transferTax'], current_tax_details['totalTax'])
    future_min_tax = min(future_taxes['inheritanceTax'], future_taxes['transferTax'], future_taxes['liquidationTax'])
    
    if current_min_tax == current_tax_details['inheritanceTax']:
        current_best = "증여세"
    elif current_min_tax == current_tax_details['transferTax']:
        current_best = "양도소득세"
    else:
        current_best = "청산소득세"
        
    if future_min_tax == future_taxes['inheritanceTax']:
        future_best = "증여세"
    elif future_min_tax == future_taxes['transferTax']:
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
    st.markdown("※ 이 계산기의 세금 계산은 참고용으로만 사용하시기 바랍니다.", unsafe_allow_html=True)
    st.markdown("※ 실제 세금은 개인 상황, 보유기간, 대주주 여부, 사업 형태 등에 따라 달라질 수 있습니다.", unsafe_allow_html=True)
    st.markdown("※ 정확한 세금 계산과 절세 전략은 세무사와 상담하시기 바랍니다.", unsafe_allow_html=True)
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
