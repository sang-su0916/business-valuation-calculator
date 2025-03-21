import streamlit as st
import pandas as pd
import locale
import numpy as np
from datetime import datetime, timedelta
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
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .tax-title {
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 15px;
        text-align: center;
    }
    .tax-amount {
        font-size: 24px;
        font-weight: 500;
        margin: 10px 0;
        text-align: center;
    }
    .tax-rate {
        color: #28a745;
        font-weight: 500;
        margin-bottom: 10px;
        text-align: center;
    }
    .tax-description {
        color: #555;
        font-size: 0.95em;
        margin: 10px 0;
        text-align: left;
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
        font-weight: 500;
    }
    /* 수정된 세금 비교 테이블 스타일 */
    .tax-compare-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 15px;
        table-layout: fixed;
    }
    .tax-compare-table th {
        background-color: #f1f8ff;
        padding: 12px;
        text-align: center;
        border: 1px solid #dee2e6;
        font-weight: 600;
    }
    .tax-compare-table td {
        padding: 12px;
        border: 1px solid #dee2e6;
        text-align: center;
    }
    .tax-type {
        width: 34%;
        text-align: center;
        font-weight: 500;
    }
    .tax-amount {
        width: 33%;
        text-align: center;
        font-family: 'Courier New', monospace;
        font-weight: 500;
    }
    .analysis-section {
        background-color: #e9f7ef;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    .download-section {
        background-color: #f0f7fb;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
    }
    /* 상단 세금 금액 중앙 정렬 스타일 */
    .center-tax-display {
        text-align: center;
        font-size: 24px;
        font-weight: 500;
        margin: 10px 0;
        font-family: 'Courier New', monospace;
    }
    .center-tax-label {
        text-align: center;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .center-tax-detail {
        text-align: center;
        color: #28a745;
        font-size: 14px;
        margin-bottom: 10px;
    }
    .error-message {
        color: #dc3545;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .notice-box {
        background-color: #e8f7e8;
        border-left: 4px solid #28a745;
        padding: 15px;
        margin: 15px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# HTML 다운로드용 내용 생성
def create_html_content(current_tax, future_tax, company_name, growth_rate, future_years):
    target_year = datetime.now().year + future_years
    
    # 세금 증가율 계산
    inheritance_increase = (future_tax["inheritance"] / current_tax["inheritance"] - 1) * 100
    transfer_increase = (future_tax["transfer"] / current_tax["transfer"] - 1) * 100
    liquidation_increase = (future_tax["liquidation"] / current_tax["liquidation"] - 1) * 100
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>미래 세금 계산 보고서 - {company_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            h2 {{ color: #3498db; margin-top: 20px; }}
            .info {{ margin-bottom: 5px; }}
            .tax-box {{ background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; }}
            .current {{ border-left: 4px solid #3498db; }}
            .future {{ border-left: 4px solid #e67e22; }}
            .increase {{ color: #27ae60; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            table, th, td {{ border: 1px solid #ddd; }}
            th, td {{ padding: 12px; text-align: center; }}
            th {{ background-color: #f2f2f2; }}
            td.number {{ text-align: right; }}
            .best-option {{ background-color: #e6f7e6; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <h1>미래 세금 계산 보고서</h1>
        
        <h2>회사 정보</h2>
        <div class="info">회사명: {company_name}</div>
        
        <h2>예측 정보</h2>
        <div class="info">적용 성장률: 연 {growth_rate}% (복리)</div>
        <div class="info">예측 기간: {future_years}년 (기준: {datetime.now().year}년 → 예측: {target_year}년)</div>
        
        <h2>현재 vs 미래 세금 비교</h2>
        <table>
            <tr>
                <th>세금 유형</th>
                <th>현재 (2025년)</th>
                <th>미래 ({target_year}년)</th>
                <th>증가율</th>
            </tr>
            <tr>
                <td>상속증여세 (누진세율)</td>
                <td class="number">{simple_format(current_tax["inheritance"])}원</td>
                <td class="number">{simple_format(future_tax["inheritance"])}원</td>
                <td class="number">{inheritance_increase:.1f}%</td>
            </tr>
            <tr>
                <td>양도소득세(지방소득세 포함) (20%~25%)</td>
                <td class="number">{simple_format(current_tax["transfer"])}원</td>
                <td class="number">{simple_format(future_tax["transfer"])}원</td>
                <td class="number">{transfer_increase:.1f}%</td>
            </tr>
            <tr>
                <td>청산소득세 (법인세+종합소득세)</td>
                <td class="number">{simple_format(current_tax["liquidation"])}원</td>
                <td class="number">{simple_format(future_tax["liquidation"])}원</td>
                <td class="number">{liquidation_increase:.1f}%</td>
            </tr>
        </table>
        
        <div class="best-option">
            <h3>최적 세금 옵션</h3>
            <p>현재 기준 최적 세금 옵션: <strong>{current_tax["best_option"]}</strong></p>
            <p>미래 기준 최적 세금 옵션: <strong>{future_tax["best_option"]}</strong></p>
        </div>
        
        <div style="margin-top: 30px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
            <p><b>참고:</b> 이 보고서의 세금 계산은 참고용으로만 사용하시기 바랍니다. 실제 세금은 개인 상황, 보유기간, 대주주 여부, 사업 형태 등에 따라 달라질 수 있습니다.</p>
            <p>미래 가치 예측은 단순 성장률 적용으로 실제 기업 가치 변동과는 차이가 있을 수 있습니다.</p>
        </div>
        
        <div style="margin-top: 30px; text-align: center; color: #777; font-size: 0.9em;">
            <p>생성일: {datetime.now().strftime('%Y년 %m월 %d일')}</p>
        </div>
    </body>
    </html>
    """
    return html_content

# CSV 다운로드용 내용 생성
def create_csv_content(current_tax, future_tax, company_name, growth_rate, future_years):
    # 현재 년도 계산
    current_year = datetime.now().year
    target_year = current_year + future_years
    
    # 세금 증가율 계산
    inheritance_increase = (future_tax["inheritance"] / current_tax["inheritance"] - 1) * 100
    transfer_increase = (future_tax["transfer"] / current_tax["transfer"] - 1) * 100
    liquidation_increase = (future_tax["liquidation"] / current_tax["liquidation"] - 1) * 100
    
    # CSV 데이터 생성
    data = {
        '항목': [
            '회사명', '성장률', '예측기간', 
            '예측 시작 연도', '예측 종료 연도',
            '현재 상속증여세', '미래 상속증여세', '상속증여세 증가율',
            '현재 양도소득세(지방소득세 포함)', '미래 양도소득세(지방소득세 포함)', '양도소득세 증가율',
            '현재 청산소득세(종합소득세 포함)', '미래 청산소득세(종합소득세 포함)', '청산소득세 증가율',
            '현재 최적 세금 옵션', '미래 최적 세금 옵션'
        ],
        '값': [
            company_name, f"{growth_rate}%", f"{future_years}년",
            str(current_year), str(target_year),
            current_tax["inheritance"], future_tax["inheritance"], f"{inheritance_increase:.1f}%",
            current_tax["transfer"], future_tax["transfer"], f"{transfer_increase:.1f}%",
            current_tax["liquidation"], future_tax["liquidation"], f"{liquidation_increase:.1f}%",
            current_tax["best_option"], future_tax["best_option"]
        ]
    }
    
    # DataFrame 생성 후 CSV로 변환
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False).encode('utf-8')
    return csv

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

# 양도소득세 계산 함수 - 수정됨
def calculate_transfer_tax(transfer_value, acquisition_value):
    # 양도차익 계산 (수정됨)
    transfer_profit = transfer_value - acquisition_value
    
    # 기본공제 250만원 적용
    taxable_gain = max(0, transfer_profit - 2500000)
    
    calculation_steps = []
    # 양도차익 계산 표시 수정
    calculation_steps.append({"description": "양도차익 계산", "detail": f"양도가액({simple_format(transfer_value)}원) - 취득가액({simple_format(acquisition_value)}원) = {simple_format(transfer_profit)}원"})
    calculation_steps.append({"description": "기본공제", "detail": f"2,500,000원"})
    calculation_steps.append({"description": "과세표준", "detail": f"{simple_format(taxable_gain)}원"})
    
    # 3억 이하: 20%, 3억 초과: 25% (지방소득세 포함 22%, 27.5%)
    base_tax_rate = 0.20  # 기본세율 20%
    higher_tax_rate = 0.25  # 3억 초과분 세율 25%
    
    if taxable_gain <= 300000000:
        tax = taxable_gain * base_tax_rate
        calculation_steps.append({"description": "세액 계산", "detail": f"{simple_format(taxable_gain)}원 × 20% = {simple_format(tax)}원"})
    else:
        tax_below_300m = 300000000 * base_tax_rate
        tax_above_300m = (taxable_gain - 300000000) * higher_tax_rate
        tax = tax_below_300m + tax_above_300m
        
        calculation_steps.append({"description": "3억원 이하", "detail": f"300,000,000원 × 20% = {simple_format(tax_below_300m)}원"})
        calculation_steps.append({"description": "3억원 초과", "detail": f"{simple_format(taxable_gain - 300000000)}원 × 25% = {simple_format(tax_above_300m)}원"})
        calculation_steps.append({"description": "소득세 합계", "detail": f"{simple_format(tax)}원"})
    
    # 지방소득세 계산 (소득세의 10%)
    local_tax = tax * 0.1
    calculation_steps.append({"description": "지방소득세", "detail": f"{simple_format(tax)}원 × 10% = {simple_format(local_tax)}원"})
    
    # 총 세액 (소득세 + 지방소득세)
    total_tax = tax + local_tax
    calculation_steps.append({"description": "총 세액", "detail": f"{simple_format(tax)}원 + {simple_format(local_tax)}원 = {simple_format(total_tax)}원"})
    
    # 실효세율 계산
    effective_rate = (total_tax / transfer_profit) * 100 if transfer_profit > 0 else 0
    
    return total_tax, calculation_steps, effective_rate, transfer_profit

# 청산소득세 계산 함수 - 첨부 자료 기준으로 수정
def calculate_liquidation_tax(owned_value, acquisition_value, total_value, total_shares, owned_shares, is_family_corp=False):
    calculation_steps = []
    
    # 1단계: 법인 단계 - 청산소득에 대한 법인세 계산
    # 회사의 자기자본총액 계산 (액면가 × 총 주식수)
    capital = 5000 * total_shares  # 액면가 5,000원으로 가정
    
    # 잔여재산가액 (회사 총가치)
    company_value = total_value
    
    # 청산소득금액 계산
    corporate_income = company_value - capital
    calculation_steps.append({"description": "청산소득금액", "detail": f"잔여재산가액({simple_format(company_value)}원) - 자기자본총액({simple_format(capital)}원) = {simple_format(corporate_income)}원"})
    
    # 법인세 계산 - 새로운 세율 적용
    if not is_family_corp:
        # 일반법인 세율 적용
        if corporate_income <= 200000000:  # 2억원 이하
            corporate_tax = corporate_income * 0.09
            calculation_steps.append({"description": "법인세(2억 이하)", "detail": f"{simple_format(corporate_income)}원 × 9% = {simple_format(corporate_tax)}원"})
        else:  # 2억원 초과
            # 2억원까지는 9%, 나머지는 19% 적용
            corporate_tax = 200000000 * 0.09 + (corporate_income - 200000000) * 0.19
            calculation_steps.append({"description": "법인세", "detail": f"2억원 × 9% + {simple_format(corporate_income - 200000000)}원 × 19% = {simple_format(corporate_tax)}원"})
    else:
        # 가족법인 세율 적용
        corporate_tax = corporate_income * 0.19  # 가족법인은 19% 고정 세율 적용
        calculation_steps.append({"description": "법인세(가족법인)", "detail": f"{simple_format(corporate_income)}원 × 19% = {simple_format(corporate_tax)}원"})
    
    # 2단계: 주주 단계 - 잔여재산 분배에 대한 종합소득세
    # 법인세 납부 후 잔여재산
    after_tax_corporate = corporate_income - corporate_tax
    calculation_steps.append({"description": "법인세 납부 후 잔여재산", "detail": f"{simple_format(corporate_income)}원 - {simple_format(corporate_tax)}원 = {simple_format(after_tax_corporate)}원"})
    
    # 대표자 몫(지분율 적용)
    ownership_ratio = owned_shares / total_shares
    individual_distribution = after_tax_corporate * ownership_ratio
    calculation_steps.append({"description": "대표자 몫(80%)", "detail": f"{simple_format(after_tax_corporate)}원 × {ownership_ratio:.1%} = {simple_format(individual_distribution)}원"})
    
    # 종합소득세 계산(최고세율 45% 적용, 누진공제 6,540만원)
    individual_tax = individual_distribution * 0.45 - 65400000
    if individual_tax < 0:
        individual_tax = 0
    calculation_steps.append({"description": "종합소득세", "detail": f"{simple_format(individual_distribution)}원 × 45% - 65,400,000원(누진공제) = {simple_format(individual_tax)}원"})
    
    # 총 세액 (법인세 + 종합소득세)
    total_tax = corporate_tax + individual_tax
    calculation_steps.append({"description": "총 세액(법인세 + 종합소득세)", "detail": f"{simple_format(corporate_tax)}원 + {simple_format(individual_tax)}원 = {simple_format(total_tax)}원"})
    
    # 실효세율 계산
    effective_rate = (total_tax / owned_value) * 100 if owned_value > 0 else 0
    
    return corporate_tax, individual_tax, total_tax, calculation_steps, effective_rate, corporate_income, individual_distribution

# 미래 가치 계산 함수 - 오류 수정
def calculate_future_value(current_value, growth_rate, years):
    """
    현재 가치에서 성장률을 적용하여 미래 가치를 계산합니다.
    
    Parameters:
    current_value (dict): 현재 주식 가치 정보가 담긴 딕셔너리
    growth_rate (float): 연간 성장률 (%)
    years (int): 예측 기간 (년)
    
    Returns:
    dict: 미래 주식 가치 정보가 담긴 딕셔너리
    """
    try:
        future_value = {}
        
        # 안전하게 딕셔너리 키 존재 여부 확인 후 계산
        for key, value in current_value.items():
            if isinstance(value, (int, float)):
                # 숫자 값에만 성장률 적용
                future_value[key] = value * ((1 + growth_rate/100) ** years)
            else:
                # 문자열 등 다른 값은 그대로 복사
                future_value[key] = value
        
        return future_value
    except Exception as e:
        # 오류 발생 시 현재 값 그대로 반환
        st.error(f"미래 가치 계산 중 오류가 발생했습니다: {str(e)}")
        return {k: v for k, v in current_value.items()}

# 페이지 헤더
st.title("미래 세금 계산")

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
    
    # 총 주식수는 session_state에서 가져오거나 기본값 설정
    total_shares = st.session_state.get('total_shares', 10000)
    
    # 2025년 세법 변경 공지
    st.markdown("<div class='notice-box'>🍀 2025년부터 법인세율에 일부 변화가 적용됩니다.</div>", unsafe_allow_html=True)
    
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
    
    # 미래 회사 가치 계산 - 오류 처리 추가
    try:
        future_value = calculate_future_value(stock_value, growth_rate, years)
        
        # 안전하게 future_value 확인
        if not isinstance(future_value, dict):
            st.error("미래 가치 계산 중 오류가 발생했습니다.")
            future_value = {k: v for k, v in stock_value.items()}  # 기본값으로 현재 가치 사용
    except Exception as e:
        st.error(f"미래 가치 계산 중 오류가 발생했습니다: {str(e)}")
        future_value = {k: v for k, v in stock_value.items()}  # 기본값으로 현재 가치 사용
    
    # 미래 주식가치 정보
    with st.expander("미래 주식 가치", expanded=True):
        st.markdown("<div class='tax-info-section'>", unsafe_allow_html=True)
        st.markdown(f"<div>회사명: <b>{company_name}</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div>예측 기간: <b>{years}년</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div>적용 성장률: <b>연 {growth_rate}%</b></div>", unsafe_allow_html=True)
        
        # 안전하게 키 존재 확인
        if 'finalValue' in future_value:
            st.markdown(f"<div>미래 주당 평가액: <b>{simple_format(future_value['finalValue'])}원</b></div>", unsafe_allow_html=True)
        if 'totalValue' in future_value:
            st.markdown(f"<div>미래 회사 총가치: <b>{simple_format(future_value['totalValue'])}원</b></div>", unsafe_allow_html=True)
        if 'ownedValue' in future_value:
            st.markdown(f"<div>미래 대표이사 보유주식 가치: <b>{simple_format(future_value['ownedValue'])}원</b></div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 현재와 미래 세금 계산 - 안전하게 처리
    try:
        current_ownership_value = stock_value.get("ownedValue", 0)
        future_ownership_value = future_value.get("ownedValue", 0)
        current_total_value = stock_value.get("totalValue", 0)
        future_total_value = future_value.get("totalValue", 0)
        acquisition_value = owned_shares * share_price
        
        # 현재 세금 계산 - 수정된 함수 호출
        current_inheritance_tax, current_inheritance_steps, current_inheritance_rate = calculate_inheritance_tax(current_ownership_value)
        current_transfer_tax, current_transfer_steps, current_transfer_rate, current_transfer_profit = calculate_transfer_tax(current_ownership_value, acquisition_value)
        current_corporate_tax, current_individual_tax, current_liquidation_tax, current_liquidation_steps, current_liquidation_rate, current_corporate_income, current_individual_distribution = calculate_liquidation_tax(
            current_ownership_value, acquisition_value, current_total_value, total_shares, owned_shares, is_family_corp
        )
        
        # 미래 세금 계산 - 수정된 함수 호출
        future_inheritance_tax, future_inheritance_steps, future_inheritance_rate = calculate_inheritance_tax(future_ownership_value)
        future_transfer_tax, future_transfer_steps, future_transfer_rate, future_transfer_profit = calculate_transfer_tax(future_ownership_value, acquisition_value)
        future_corporate_tax, future_individual_tax, future_liquidation_tax, future_liquidation_steps, future_liquidation_rate, future_corporate_income, future_individual_distribution = calculate_liquidation_tax(
            future_ownership_value, acquisition_value, future_total_value, total_shares, owned_shares, is_family_corp
        )
    except Exception as e:
        st.error(f"세금 계산 중 오류가 발생했습니다: {str(e)}")
        # 기본값 설정
        current_inheritance_tax, current_inheritance_steps, current_inheritance_rate = 0, [], 0
        current_transfer_tax, current_transfer_steps, current_transfer_rate, current_transfer_profit = 0, [], 0, 0
        current_corporate_tax, current_individual_tax, current_liquidation_tax, current_liquidation_steps, current_liquidation_rate, current_corporate_income, current_individual_distribution = 0, 0, 0, [], 0, 0, 0
        future_inheritance_tax, future_inheritance_steps, future_inheritance_rate = 0, [], 0
        future_transfer_tax, future_transfer_steps, future_transfer_rate, future_transfer_profit = 0, [], 0, 0
        future_corporate_tax, future_individual_tax, future_liquidation_tax, future_liquidation_steps, future_liquidation_rate, future_corporate_income, future_individual_distribution = 0, 0, 0, [], 0, 0, 0
    
    # 세금 계산 결과
    st.header("미래 세금 계산 결과")
    
    # 상단 세금 정보를 3개 컬럼으로 나누어 표시
    col1, col2, col3 = st.columns(3)
    
    # 상속증여세 표시 (중앙 정렬)
    with col1:
        st.markdown("<div class='center-tax-label'>상속증여세</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='center-tax-display'>{simple_format(future_inheritance_tax)}원</div>", unsafe_allow_html=True)
        st.markdown("<div class='center-tax-detail'>적용 세율: 누진세율 (10%~50%)</div>", unsafe_allow_html=True)
        st.markdown("<div>주식을 타인에게 무상으로 증여할 경우 발생하는 세금입니다. 증여 받은 사람이 납부합니다.</div>", unsafe_allow_html=True)
    
    # 양도소득세 표시 (중앙 정렬) - 수정
    with col2:
        st.markdown("<div class='center-tax-label'>양도소득세(지방소득세 포함)</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='center-tax-display'>{simple_format(future_transfer_tax)}원</div>", unsafe_allow_html=True)
        st.markdown("<div class='center-tax-detail'>적용 세율: 3억 이하 20%, 초과 25%</div>", unsafe_allow_html=True)
        st.markdown("<div>주식을 매각하여 발생한 이익(양도차익)에 대해 부과되는 세금입니다. 기본공제 250만원이 적용됩니다.</div>", unsafe_allow_html=True)
    
    # 청산소득세 표시 (중앙 정렬) - 수정
    with col3:
        st.markdown("<div class='center-tax-label'>청산소득세(종합소득세 포함)</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='center-tax-display'>{simple_format(future_liquidation_tax)}원</div>", unsafe_allow_html=True)
        if is_family_corp:
            st.markdown("<div class='center-tax-detail'>법인: 19% + 개인: 45%</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='center-tax-detail'>법인: 9~19% + 개인: 45%</div>", unsafe_allow_html=True)
        st.markdown("<div>법인 청산 시 발생하는 세금으로, 법인세와 잔여재산 분배에 따른 종합소득세로 구성됩니다.</div>", unsafe_allow_html=True)
    
    # 미래 상속증여세 계산 세부내역
    with st.expander("상속증여세 계산 세부내역"):
        st.markdown("<div class='calculation-box'>", unsafe_allow_html=True)
        st.markdown(f"<p>과세표준: {simple_format(future_ownership_value)}원</p>", unsafe_allow_html=True)
        
        for step in future_inheritance_steps:
            st.markdown(f"<div class='calculation-step'>{step['bracket']}: {simple_format(step['amount'])}원 × {int(step['rate']*100)}% = {simple_format(step['tax'])}원</div>", unsafe_allow_html=True)
        
        st.markdown(f"<p><b>총 상속증여세: {simple_format(future_inheritance_tax)}원</b> (실효세율: {future_inheritance_rate:.1f}%)</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 미래 양도소득세 계산 세부내역 - 이름 수정
    with st.expander("양도소득세(지방소득세 포함) 계산 세부내역"):
        st.markdown("<div class='calculation-box'>", unsafe_allow_html=True)
        
        for step in future_transfer_steps:
            st.markdown(f"<div class='calculation-step'>{step['description']}: {step['detail']}</div>", unsafe_allow_html=True)
        
        st.markdown(f"<p><b>총 양도소득세(지방소득세 포함): {simple_format(future_transfer_tax)}원</b> (실효세율: {future_transfer_rate:.1f}%)</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 미래 청산소득세 계산 세부내역 - 수정
    with st.expander("청산소득세(종합소득세 포함) 계산 세부내역"):
        st.markdown("<div class='calculation-box'>", unsafe_allow_html=True)
        
        # 청산소득세 계산 과정에 법인과 개인 단계 표시
        st.markdown("<p><b>청산소득세 (법인세+종합소득세)</b></p>", unsafe_allow_html=True)
        st.markdown(f"<p>법인: {simple_format(future_corporate_income)}원</p>", unsafe_allow_html=True)
        st.markdown(f"<p>개인: {simple_format(future_individual_distribution)}원</p>", unsafe_allow_html=True)
        
        for step in future_liquidation_steps:
            st.markdown(f"<div class='calculation-step'>{step['description']}: {step['detail']}</div>", unsafe_allow_html=True)
        
        st.markdown(f"<p><b>총 청산소득세: {simple_format(future_liquidation_tax)}원</b> (실효세율: {future_liquidation_rate:.1f}%)</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 현재 vs 미래 세금 비교
    st.markdown("<h2 style='margin-top:30px; text-align:center;'>현재 vs 미래 세금 비교</h2>", unsafe_allow_html=True)
    
    # 세금 증가율 계산 - 0으로 나누기 오류 방지
    try:
        inheritance_increase = (future_inheritance_tax / current_inheritance_tax - 1) * 100 if current_inheritance_tax > 0 else 0
        transfer_increase = (future_transfer_tax / current_transfer_tax - 1) * 100 if current_transfer_tax > 0 else 0
        liquidation_increase = (future_liquidation_tax / current_liquidation_tax - 1) * 100 if current_liquidation_tax > 0 else 0
    except Exception as e:
        inheritance_increase = transfer_increase = liquidation_increase = 0
    
    # 중앙 정렬된 테이블 - 양도소득세 이름 수정
    st.markdown("""
    <table class="tax-compare-table">
        <thead>
            <tr>
                <th style="width:34%;">세금 유형</th>
                <th style="width:33%;">현재 (2025년)</th>
                <th style="width:33%;">미래</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="tax-type">상속증여세 (누진세율)</td>
                <td class="tax-amount">{0}원</td>
                <td class="tax-amount blue-text">{1}원</td>
            </tr>
            <tr>
                <td class="tax-type">양도소득세(지방소득세 포함) (20%~25%)</td>
                <td class="tax-amount">{2}원</td>
                <td class="tax-amount blue-text">{3}원</td>
            </tr>
            <tr>
                <td class="tax-type">청산소득세(종합소득세 포함)</td>
                <td class="tax-amount">{4}원</td>
                <td class="tax-amount blue-text">{5}원</td>
            </tr>
        </tbody>
    </table>
    """.format(
        simple_format(current_inheritance_tax),
        simple_format(future_inheritance_tax),
        simple_format(current_transfer_tax),
        simple_format(future_transfer_tax),
        simple_format(current_liquidation_tax),
        simple_format(future_liquidation_tax)
    ), unsafe_allow_html=True)
    
    # 세금 비교 분석
    st.markdown("<div class='analysis-section'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>세금 비교 분석</h3>", unsafe_allow_html=True)
    
    # 최적의 세금 옵션 찾기 (현재)
    current_min_tax = min(current_inheritance_tax, current_transfer_tax, current_liquidation_tax)
    
    if current_min_tax == current_inheritance_tax:
        current_best = "상속증여세"
    elif current_min_tax == current_transfer_tax:
        current_best = "양도소득세(지방소득세 포함)"  # 이름 수정
    else:
        current_best = "청산소득세(종합소득세 포함)"  # 이름 수정
    
    # 최적의 세금 옵션 찾기 (미래)
    future_min_tax = min(future_inheritance_tax, future_transfer_tax, future_liquidation_tax)
    
    if future_min_tax == future_inheritance_tax:
        future_best = "상속증여세"
    elif future_min_tax == future_transfer_tax:
        future_best = "양도소득세(지방소득세 포함)"  # 이름 수정
    else:
        future_best = "청산소득세(종합소득세 포함)"  # 이름 수정
    
    # 세금 최소값 데이터
    current_tax = {
        "inheritance": current_inheritance_tax,
        "transfer": current_transfer_tax,
        "liquidation": current_liquidation_tax,
        "best_option": current_best
    }
    
    future_tax = {
        "inheritance": future_inheritance_tax,
        "transfer": future_transfer_tax,
        "liquidation": future_liquidation_tax,
        "best_option": future_best
    }
    
    st.markdown(f"<div style='text-align:center;'>현재 기준으로는 <b>{current_best}</b>가 세금 부담이 가장 적습니다.</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center;'>미래 기준으로는 <b>{future_best}</b>가 세금 부담이 가장 적을 것으로 예상됩니다.</div>", unsafe_allow_html=True)
    
    # 세금 증가율 표시
    st.markdown("<h4 style='text-align:center; margin-top:20px;'>세금 증가 예상</h4>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center;'>상속증여세: <b>+{inheritance_increase:.1f}%</b> 증가</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center;'>양도소득세(지방소득세 포함): <b>+{transfer_increase:.1f}%</b> 증가</div>", unsafe_allow_html=True)  # 이름 수정
    st.markdown(f"<div style='text-align:center;'>청산소득세(종합소득세 포함): <b>+{liquidation_increase:.1f}%</b> 증가</div>", unsafe_allow_html=True)  # 이름 수정
    
    st.markdown("<p style='margin-top:15px;'>기업 가치의 성장에 따라 세금 부담도 증가합니다. 누진세율이 적용되는 상속증여세의 경우 가치 증가 비율보다 세금 증가 비율이 더 높을 수 있습니다.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 적용 세율 정보
    with st.expander("적용 세율 정보"):
        st.markdown("<div class='tax-info-section'>", unsafe_allow_html=True)
        st.markdown("<h4>상속증여세율</h4>", unsafe_allow_html=True)
        st.markdown("<ul>", unsafe_allow_html=True)
        st.markdown("<li>1억 이하: 10%</li>", unsafe_allow_html=True)
        st.markdown("<li>1억~5억: 20%</li>", unsafe_allow_html=True)
        st.markdown("<li>5억~10억: 30%</li>", unsafe_allow_html=True)
        st.markdown("<li>10억~30억: 40%</li>", unsafe_allow_html=True)
        st.markdown("<li>30억 초과: 50%</li>", unsafe_allow_html=True)
        st.markdown("</ul>", unsafe_allow_html=True)
        
        # 양도소득세율 수정
        st.markdown("<h4>양도소득세율(지방소득세 포함)</h4>", unsafe_allow_html=True)
        st.markdown("<ul>", unsafe_allow_html=True)
        st.markdown("<li>3억 이하: 20% (지방세 포함 22%)</li>", unsafe_allow_html=True)
        st.markdown("<li>3억 초과: 25% (지방세 포함 27.5%)</li>", unsafe_allow_html=True)
        st.markdown("<li>기본공제: 250만원</li>", unsafe_allow_html=True)
        st.markdown("</ul>", unsafe_allow_html=True)
        
        # 법인세율 테이블 - 2025년 세법 변경 반영
        st.markdown("<h4>일반법인 세율 (2025년 기준)</h4>", unsafe_allow_html=True)
        st.markdown("""
        <table class="balanced-table">
            <tr>
                <th>과세표준 구간 (원)</th>
                <th>2024년 세율</th>
                <th>2025년 세율</th>
            </tr>
            <tr>
                <td>0 ~ 2억</td>
                <td>9%</td>
                <td>9% (유지)</td>
            </tr>
            <tr>
                <td>2억 ~ 200억</td>
                <td>19%</td>
                <td>19% (유지)</td>
            </tr>
            <tr>
                <td>200억 초과</td>
                <td>22%</td>
                <td>22% (유지)</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        
        st.markdown("<h4>성실신고 법인 세율 (2025년 기준)</h4>", unsafe_allow_html=True)
        st.markdown("""
        <table class="balanced-table">
            <tr>
                <th>과세표준 구간 (원)</th>
                <th>2024년 세율</th>
                <th>2025년 세율</th>
            </tr>
            <tr>
                <td>2억원 이하</td>
                <td>9%</td>
                <td>19%</td>
            </tr>
            <tr>
                <td>200억원 이하</td>
                <td>19%</td>
                <td>19% (유지)</td>
            </tr>
            <tr>
                <td>200억원 초과</td>
                <td>24%</td>
                <td>24% (유지)</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        
        st.markdown("<h4>종합소득세율</h4>", unsafe_allow_html=True)
        st.markdown("<ul>", unsafe_allow_html=True)
        st.markdown("<li>최고세율: 45% (누진공제 6,540만원 적용)</li>", unsafe_allow_html=True)
        st.markdown("</ul>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 결과 다운로드 섹션 추가
    st.markdown("---")
    with st.expander("📥 세금 계산 결과 다운로드", expanded=False):
        st.markdown("<div class='download-section'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["HTML", "CSV"])
        
        # HTML 다운로드 탭
        with tab1:
            if st.button("HTML 보고서 생성하기", key="generate_html"):
                html_content = create_html_content(current_tax, future_tax, company_name, growth_rate, years)
                
                st.download_button(
                    label="📄 HTML 파일 다운로드",
                    data=html_content,
                    file_name=f"미래세금_{company_name}_{future_date.year}.html",
                    mime="text/html"
                )
                
                st.info("HTML 파일을 다운로드 후 브라우저에서 열어 인쇄하면 PDF로 저장할 수 있습니다.")
        
        # CSV 다운로드 탭
        with tab2:
            if st.button("CSV 데이터 생성하기", key="generate_csv"):
                csv_content = create_csv_content(current_tax, future_tax, company_name, growth_rate, years)
                
                st.download_button(
                    label="📄 CSV 파일 다운로드",
                    data=csv_content,
                    file_name=f"미래세금_{company_name}_{future_date.year}.csv",
                    mime="text/csv"
                )
        
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
