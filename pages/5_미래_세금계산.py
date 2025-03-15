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
    .tax-info-section {
        background-color: #f0f7fb;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
    }
    .sidebar-guide {
        background-color: #e8f4f8;
        padding: 10px 15px;
        border-radius: 5px;
        margin-top: 10px;
        font-size: 0.9em;
        border-left: 3px solid #4dabf7;
    }
    .info-box {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .expander-box {
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .expander-header {
        cursor: pointer;
        padding: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .result-section {
        background-color: #f0f7fb;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
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
    
    return tax

# 양도소득세 계산 함수
def calculate_transfer_tax(gain, acquisition_value):
    # 기본공제 250만원 적용
    taxable_gain = max(0, gain - 2500000)
    
    # 3억 이하: 22%, 3억 초과: 27.5%
    if taxable_gain <= 300000000:
        tax = taxable_gain * 0.22
    else:
        tax = 300000000 * 0.22 + (taxable_gain - 300000000) * 0.275
    
    return tax

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
    
    return total_tax

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
        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
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
    current_inheritance_tax = calculate_inheritance_tax(current_ownership_value)
    current_transfer_tax = calculate_transfer_tax(current_ownership_value - acquisition_value, acquisition_value)
    current_liquidation_tax = calculate_liquidation_tax(current_ownership_value, acquisition_value, is_family_corp)
    
    # 미래 세금 계산
    future_inheritance_tax = calculate_inheritance_tax(future_ownership_value)
    future_transfer_tax = calculate_transfer_tax(future_ownership_value - acquisition_value, acquisition_value)
    future_liquidation_tax = calculate_liquidation_tax(future_ownership_value, acquisition_value, is_family_corp)
    
    # 세금 계산 결과 내역
    st.markdown("<div class='result-section'>", unsafe_allow_html=True)
    st.markdown("<h3>세금 계산 결과 안내</h3>", unsafe_allow_html=True)
    st.markdown("<p>비상장주식의 미래 가치를 바탕으로 세 가지 경우에 대한 세금을 계산했습니다:</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='bullet-item'>증여세: 미래 시점에 주식을 증여하는 경우 적용되는 세금 (누진세율 적용)</div>", unsafe_allow_html=True)
    st.markdown("<div class='bullet-item'>양도소득세: 미래 시점에 주식을 매각할 때 발생하는 세금 (3억 기준 세율 구분)</div>", unsafe_allow_html=True)
    st.markdown("<div class='bullet-item'>청산소득세: 미래 시점에 법인을 청산할 때 지분 가치에 대한 세금 (법인세 + 배당소득세)</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 현재 vs 미래 세금 비교
    st.markdown("<h2>현재 vs 미래 세금 비교</h2>", unsafe_allow_html=True)
    
    # 비교 테이블
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("<div style='text-align: center;'><b>세금 유형</b></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div style='text-align: center;'><b>현재 (2025년)</b></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div style='text-align: center;'><b>미래</b></div>", unsafe_allow_html=True)
    
    # 증여세 행
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("증여세 (누진세율)")
    with col2:
        st.markdown(f"{simple_format(current_inheritance_tax)}원")
    with col3:
        st.markdown(f"<span class='blue-text'>{simple_format(future_inheritance_tax)}원</span>", unsafe_allow_html=True)
    
    # 양도소득세 행
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("양도소득세 (22%~27.5%)")
    with col2:
        st.markdown(f"{simple_format(current_transfer_tax)}원")
    with col3:
        st.markdown(f"<span class='blue-text'>{simple_format(future_transfer_tax)}원</span>", unsafe_allow_html=True)
    
    # 청산소득세 행
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("청산소득세 (법인세+배당세)")
    with col2:
        st.markdown(f"{simple_format(current_liquidation_tax)}원")
    with col3:
        st.markdown(f"<span class='blue-text'>{simple_format(future_liquidation_tax)}원</span>", unsafe_allow_html=True)
    
    # 적용 세율 정보
    st.markdown("<div class='tax-info-section'>", unsafe_allow_html=True)
    st.markdown("<h4>적용 세율 정보:</h4>", unsafe_allow_html=True)
    st.markdown("<div class='bullet-item'>증여세: 1억 이하 10%, 1억~5억 20%, 5억~10억 30%, 10억~30억 40%, 30억 초과 50% (누진세율)</div>", unsafe_allow_html=True)
    st.markdown("<div class='bullet-item'>양도소득세: 3억 이하 22%, 3억 초과 27.5% (기본공제 250만원 적용)</div>", unsafe_allow_html=True)
    
    if is_family_corp:
        st.markdown("<div class='bullet-item'>법인세: 가족법인 200억 이하 19%, 200억~3,000억 21%, 3,000억 초과 24% (배당소득세 15.4% 추가)</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='bullet-item'>법인세: 2억 이하 9%, 2억~200억 19%, 200억~3,000억 21%, 3,000억 초과 24% (배당소득세 15.4% 추가)</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
