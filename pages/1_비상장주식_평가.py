import streamlit as st

# 페이지 설정 - 반드시 첫 번째 Streamlit 명령어로 위치해야 함
st.set_page_config(
    page_title="비상장주식 평가",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import numpy as np
import locale
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

# 페이지 스타일링
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1000px;
    }
    .stNumberInput input {
        font-weight: bold;
    }
    .stExpander {
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .amount-display {
        color: #0066cc;
        font-weight: bold;
        padding: 5px 0;
    }
    .field-description {
        color: #666;
        font-style: italic;
        font-size: 0.85rem;
        margin-top: 0.2rem;
        margin-bottom: 0.5rem;
    }
    .section-header {
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        color: #333;
    }
    .download-section {
        background-color: #f0f7fb;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
    }
    .number-input-container {
        display: flex;
        align-items: center;
        margin-bottom: 5px;
    }
    .number-input-container .stNumberInput {
        flex-grow: 1;
        margin-right: 10px;
    }
    .unit-selector {
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 앱이 처음 실행될 때만 초기화하는 플래그
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

# 세션 상태 초기화
if not st.session_state.initialized:
    st.session_state.eval_date = datetime.now().date()
    st.session_state.company_name = "엘비즈"
    st.session_state.total_equity = 1000000000
    st.session_state.net_income1 = 400000000
    st.session_state.net_income2 = 300000000
    st.session_state.net_income3 = 250000000
    st.session_state.shares = 10000
    st.session_state.owned_shares = 8000
    st.session_state.share_price = 5000
    st.session_state.interest_rate = 10  # 환원율 10%로 고정
    st.session_state.evaluation_method = "일반법인"
    st.session_state.stock_value = None
    st.session_state.evaluated = False
    st.session_state.shareholders = [
        {"name": "대표이사", "shares": 8000},
        {"name": "", "shares": 0},
        {"name": "", "shares": 0},
        {"name": "", "shares": 0},
        {"name": "", "shares": 0}
    ]
    st.session_state.shareholder_count = 1
    
    # 단위 옵션 세션 상태 초기화
    st.session_state.total_equity_unit = "원"
    st.session_state.net_income1_unit = "원"
    st.session_state.net_income2_unit = "원"
    st.session_state.net_income3_unit = "원"
    
    # 초기화 완료
    st.session_state.initialized = True

# 사용자가 입력한 숫자에서 콤마 제거하는 함수
def remove_commas(text):
    if isinstance(text, str):
        return text.replace(',', '')
    return text

# 단위에 맞게 표시 형식 변환
def format_by_unit(value, unit):
    if unit == "천원":
        return format_number(value // 1000)
    return format_number(value)

# 숫자 형식화 함수
def format_number(num, in_thousands=False):
    try:
        if in_thousands:
            # 천원 단위로 변환 (1,000,000,000원 -> 1,000,000천원)
            return "{:,}".format(int(num) // 1000) + "천"
        else:
            return "{:,}".format(int(num))
    except:
        return str(num)

# CSV 다운로드용 내용 생성
def create_csv_content():
    if not st.session_state.stock_value:
        return None
    
    # CSV 데이터 생성
    data = {
        '항목': ['평가 기준일', '회사명', '자본총계', '1년 전 당기순이익', '2년 전 당기순이익', '3년 전 당기순이익',
                '총 발행주식수', '액면금액', '환원율', '순자산가치', '수익가치', 
                '평가 방법', '주당 평가액', '기업 총 가치'],
        '값': [str(st.session_state.eval_date), st.session_state.company_name,
              st.session_state.total_equity, st.session_state.net_income1,
              st.session_state.net_income2, st.session_state.net_income3,
              st.session_state.shares, st.session_state.share_price,
              st.session_state.interest_rate, 
              st.session_state.stock_value["netAssetPerShare"],
              st.session_state.stock_value["incomeValue"],
              st.session_state.stock_value["methodText"],
              st.session_state.stock_value["finalValue"],
              st.session_state.stock_value["totalValue"]]
    }
    
    # DataFrame 생성 후 CSV로 변환
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False).encode('utf-8')
    return csv

# HTML 다운로드용 내용 생성
def create_html_content():
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>비상장주식 가치평가 보고서</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            h2 {{ color: #3498db; margin-top: 20px; }}
            .info {{ margin-bottom: 5px; }}
            .result {{ margin-top: 10px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>비상장주식 가치평가 보고서</h1>
        
        <h2>평가 정보</h2>
        <div class="info">평가 기준일: {st.session_state.eval_date}</div>
        <div class="info">회사명: {st.session_state.company_name}</div>
        
        <h2>재무 정보</h2>
        <div class="info">자본총계: {format_number(st.session_state.total_equity)}원</div>
        <div class="info">1년 전 당기순이익: {format_number(st.session_state.net_income1)}원 (가중치 3배)</div>
        <div class="info">2년 전 당기순이익: {format_number(st.session_state.net_income2)}원 (가중치 2배)</div>
        <div class="info">3년 전 당기순이익: {format_number(st.session_state.net_income3)}원 (가중치 1배)</div>
        
        <h2>주식 정보</h2>
        <div class="info">총 발행주식수: {format_number(st.session_state.shares)}주</div>
        <div class="info">액면금액: {format_number(st.session_state.share_price)}원</div>
        <div class="info">환원율: {st.session_state.interest_rate}%</div>
    """
    
    if st.session_state.stock_value:
        html_content += f"""
        <h2>평가 결과</h2>
        <div class="info">순자산가치: {format_number(st.session_state.stock_value["netAssetPerShare"])}원</div>
        <div class="info">수익가치: {format_number(st.session_state.stock_value["incomeValue"])}원</div>
        
        <div class="result">평가방법: {st.session_state.stock_value["methodText"]}</div>
        <div class="result">주당 평가액: {format_number(st.session_state.stock_value["finalValue"])}원</div>
        <div class="result">기업 총 가치: {format_number(st.session_state.stock_value["totalValue"])}원</div>
        """
    
    html_content += """
    </body>
    </html>
    """
    return html_content

# 비상장주식 가치 계산 함수
def calculate_stock_value():
    # 입력값 가져오기
    total_equity = st.session_state.total_equity
    net_income1 = st.session_state.net_income1
    net_income2 = st.session_state.net_income2
    net_income3 = st.session_state.net_income3
    shares = st.session_state.shares
    owned_shares = st.session_state.owned_shares
    interest_rate = st.session_state.interest_rate
    evaluation_method = st.session_state.evaluation_method
    eval_date = st.session_state.eval_date
    
    # 계산 로직
    net_asset_per_share = total_equity / shares
    weighted_income = (net_income1 * 3 + net_income2 * 2 + net_income3 * 1) / 6
    weighted_income_per_share = weighted_income / shares
    weighted_income_per_share_50 = weighted_income_per_share * 0.5
    equity_return = (total_equity * (interest_rate / 100)) / shares
    annuity_factor = 3.7908
    goodwill = max(0, (weighted_income_per_share_50 - equity_return) * annuity_factor)
    asset_value_with_goodwill = net_asset_per_share + goodwill
    income_value = weighted_income_per_share * (100 / interest_rate)
    
    if evaluation_method == "부동산 과다법인":
        stock_value = (asset_value_with_goodwill * 0.6) + (income_value * 0.4)
        net_asset_80_percent = net_asset_per_share * 0.8
        final_value = max(stock_value, net_asset_80_percent)
        method_text = '부동산 과다법인: (자산가치×0.6 + 수익가치×0.4)'
    elif evaluation_method == "순자산가치만 평가":
        final_value = net_asset_per_share
        method_text = '순자산가치만 평가'
    else:
        stock_value = (income_value * 0.6) + (asset_value_with_goodwill * 0.4)
        net_asset_80_percent = net_asset_per_share * 0.8
        final_value = max(stock_value, net_asset_80_percent)
        method_text = '일반법인: (수익가치×0.6 + 자산가치×0.4)'
    
    total_value = final_value * shares
    owned_value = final_value * owned_shares
    increase_percentage = round((final_value / net_asset_per_share) * 100) if net_asset_per_share > 0 else 0
    
    return {
        "evalDate": eval_date,
        "netAssetPerShare": net_asset_per_share,
        "assetValueWithGoodwill": asset_value_with_goodwill,
        "incomeValue": income_value,
        "finalValue": final_value,
        "totalValue": total_value,
        "ownedValue": owned_value,
        "methodText": method_text,
        "increasePercentage": increase_percentage,
        "weightedIncome": weighted_income
    }

# 페이지 헤더
st.title("비상장주식 가치평가")

# 평가 기준일 설정
with st.expander("평가 기준일", expanded=True):
    col1, col2 = st.columns([1, 2])
    
    with col1:
        eval_date = st.date_input(
            "",
            value=st.session_state.eval_date,
            help="비상장주식 평가의 기준이 되는 날짜입니다. 보통 결산일이나 평가가 필요한 시점으로 설정합니다.",
            key="eval_date_input"
        )
    
    with col2:
        st.markdown("<div class='field-description'>평가 기준일은 자본총계, 당기순이익 등 재무정보의 기준 시점입니다. 일반적으로 가장 최근 결산일을 사용합니다.</div>", unsafe_allow_html=True)

# 회사 정보 입력
with st.expander("회사 정보", expanded=True):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<div class='section-header'>회사명</div>", unsafe_allow_html=True)
        company_name = st.text_input(
            "회사명", 
            value=st.session_state.company_name,
            help="평가 대상 회사의 정식 명칭을 입력하세요.",
            key="company_name_input",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("<div class='section-header'>자본총계 (원)</div>", unsafe_allow_html=True)
        
        # 단위 선택 추가
        total_equity_unit = st.radio(
            "단위 선택",
            options=["원", "천원"],
            horizontal=True,
            key="total_equity_unit_radio",
            label_visibility="collapsed",
            index=0 if st.session_state.total_equity_unit == "원" else 1
        )
        st.session_state.total_equity_unit = total_equity_unit
        
        # 입력값 변환 (천원 단위로 입력했다면 원 단위로 변환)
        display_value = st.session_state.total_equity
        if total_equity_unit == "천원":
            display_value = display_value // 1000
            
        # 숫자 입력 대신 텍스트 입력으로 변경하여 콤마 입력 허용
        total_equity_str = st.text_input(
            "자본총계", 
            value=format_number(display_value), 
            help="평가 기준일 현재 회사의 대차대조표상 자본총계를 입력하세요.",
            key="total_equity_input",
            label_visibility="collapsed"
        )
        
        # 콤마 제거 후 숫자로 변환
        try:
            total_equity = int(remove_commas(total_equity_str))
        except:
            total_equity = 0
        
        # 실제 값 계산 (천원 단위로 입력했다면 원 단위로 변환)
        actual_value = total_equity
        if total_equity_unit == "천원":
            actual_value = total_equity * 1000
            
        # 세션 상태 업데이트
        st.session_state.total_equity = actual_value
        
        # 금액 표시
        if total_equity_unit == "원":
            st.markdown(f"<div class='amount-display'>금액: {format_number(actual_value)}원</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='amount-display'>금액: {format_number(actual_value // 1000)}천원</div>", unsafe_allow_html=True)
        st.markdown("<div class='field-description'>재무상태표(대차대조표)상의 자본총계 금액입니다. 평가기준일 현재의 금액을 입력하세요.</div>", unsafe_allow_html=True)

# 당기순이익 입력
with st.expander("당기순이익 (최근 3개년)", expanded=True):
    st.markdown("<div class='field-description'>최근 3개 사업연도의 당기순이익을 입력하세요. 각 연도별로 가중치가 다르게 적용됩니다.</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("##### 1년 전 (가중치 3배)")
        
        # 단위 선택 추가
        net_income1_unit = st.radio(
            "단위 선택 (1년 전)",
            options=["원", "천원"],
            horizontal=True,
            key="net_income1_unit_radio",
            label_visibility="collapsed",
            index=0 if st.session_state.net_income1_unit == "원" else 1
        )
        st.session_state.net_income1_unit = net_income1_unit
        
        # 입력값 변환 (천원 단위로 입력했다면 원 단위로 변환)
        display_value = st.session_state.net_income1
        if net_income1_unit == "천원":
            display_value = display_value // 1000
            
        net_income1_str = st.text_input(
            "당기순이익 (원)", 
            value=format_number(display_value), 
            help="가장 최근 연도의 당기순이익입니다. 3배 가중치가 적용됩니다.",
            key="income_year1_input",
            label_visibility="collapsed"
        )
        
        # 콤마 제거 후 숫자로 변환
        try:
            net_income1 = int(remove_commas(net_income1_str))
        except:
            net_income1 = 0
        
        # 실제 값 계산 (천원 단위로 입력했다면 원 단위로 변환)
        actual_value = net_income1
        if net_income1_unit == "천원":
            actual_value = net_income1 * 1000
            
        # 세션 상태 업데이트
        st.session_state.net_income1 = actual_value
        
        # 금액 표시
        if net_income1_unit == "원":
            st.markdown(f"<div class='amount-display'>금액: {format_number(actual_value)}원</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='amount-display'>금액: {format_number(actual_value // 1000)}천원</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("##### 2년 전 (가중치 2배)")
        
        # 단위 선택 추가
        net_income2_unit = st.radio(
            "단위 선택 (2년 전)",
            options=["원", "천원"],
            horizontal=True,
            key="net_income2_unit_radio",
            label_visibility="collapsed",
            index=0 if st.session_state.net_income2_unit == "원" else 1
        )
        st.session_state.net_income2_unit = net_income2_unit
        
        # 입력값 변환 (천원 단위로 입력했다면 원 단위로 변환)
        display_value = st.session_state.net_income2
        if net_income2_unit == "천원":
            display_value = display_value // 1000
            
        net_income2_str = st.text_input(
            "당기순이익 (원)", 
            value=format_number(display_value), 
            help="2년 전 당기순이익입니다. 2배 가중치가 적용됩니다.",
            key="income_year2_input",
            label_visibility="collapsed"
        )
        
        # 콤마 제거 후 숫자로 변환
        try:
            net_income2 = int(remove_commas(net_income2_str))
        except:
            net_income2 = 0
        
        # 실제 값 계산 (천원 단위로 입력했다면 원 단위로 변환)
        actual_value = net_income2
        if net_income2_unit == "천원":
            actual_value = net_income2 * 1000
            
        # 세션 상태 업데이트
        st.session_state.net_income2 = actual_value
        
        # 금액 표시
        if net_income2_unit == "원":
            st.markdown(f"<div class='amount-display'>금액: {format_number(actual_value)}원</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='amount-display'>금액: {format_number(actual_value // 1000)}천원</div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown("##### 3년 전 (가중치 1배)")
        
        # 단위 선택 추가
        net_income3_unit = st.radio(
            "단위 선택 (3년 전)",
            options=["원", "천원"],
            horizontal=True,
            key="net_income3_unit_radio",
            label_visibility="collapsed",
            index=0 if st.session_state.net_income3_unit == "원" else 1
        )
        st.session_state.net_income3_unit = net_income3_unit
        
        # 입력값 변환 (천원 단위로 입력했다면 원 단위로 변환)
        display_value = st.session_state.net_income3
        if net_income3_unit == "천원":
            display_value = display_value // 1000
            
        net_income3_str = st.text_input(
            "당기순이익 (원)", 
            value=format_number(display_value), 
            help="3년 전 당기순이익입니다. 1배 가중치가 적용됩니다.",
            key="income_year3_input",
            label_visibility="collapsed"
        )
        
        # 콤마 제거 후 숫자로 변환
        try:
            net_income3 = int(remove_commas(net_income3_str))
        except:
            net_income3 = 0
        
        # 실제 값 계산 (천원 단위로 입력했다면 원 단위로 변환)
        actual_value = net_income3
        if net_income3_unit == "천원":
            actual_value = net_income3 * 1000
            
        # 세션 상태 업데이트
        st.session_state.net_income3 = actual_value
        
        # 금액 표시
        if net_income3_unit == "원":
            st.markdown(f"<div class='amount-display'>금액: {format_number(actual_value)}원</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='amount-display'>금액: {format_number(actual_value // 1000)}천원</div>", unsafe_allow_html=True)

# 주식 정보 입력
with st.expander("주식 정보", expanded=True):
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("<div class='section-header'>총 발행주식수</div>", unsafe_allow_html=True)
        
        shares_str = st.text_input(
            "총 발행주식수", 
            value=format_number(st.session_state.shares), 
            help="회사가 발행한 총 주식수입니다.",
            key="shares_input",
            label_visibility="collapsed"
        )
        
        # 콤마 제거 후 숫자로 변환
        try:
            shares = int(remove_commas(shares_str))
            if shares < 1:
                shares = 1
        except:
            shares = 1
        
        # 세션 상태 업데이트
        st.session_state.shares = shares
        
        st.markdown(f"<div class='amount-display'>총 {format_number(shares)}주</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='section-header'>액면금액 (원)</div>", unsafe_allow_html=True)
        
        share_price_str = st.text_input(
            "액면금액 (원)", 
            value=format_number(st.session_state.share_price), 
            help="주식 1주당 액면가액입니다. 일반적으로 100원, 500원, 1,000원, 5,000원 등으로 설정됩니다.",
            key="share_price_input",
            label_visibility="collapsed"
        )
        
        # 콤마 제거 후 숫자로 변환
        try:
            share_price = int(remove_commas(share_price_str))
            if share_price < 0:
                share_price = 0
        except:
            share_price = 0
        
        # 세션 상태 업데이트
        st.session_state.share_price = share_price
        
        # 금액 표시
        st.markdown(f"<div class='amount-display'>금액: {format_number(share_price)}원</div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown("<div class='section-header'>환원율</div>", unsafe_allow_html=True)
        # 환원율 10%로 고정 표시 (슬라이더 제거)
        st.markdown("<div style='font-size:14px; color:#666;'>환원율은 10%로 고정되어 있습니다.</div>", unsafe_allow_html=True)
        # 세션 상태 변수 업데이트
        st.session_state.interest_rate = 10

# 주주 정보 입력
with st.expander("주주 정보", expanded=True):
    col1, col2 = st.columns([2, 2])
    
    with col1:
        shareholder_count = st.selectbox(
            "입력할 주주 수",
            options=[1, 2, 3, 4, 5],
            index=st.session_state.shareholder_count - 1,
            key="shareholder_count_select",
            help="입력할 주주의 수를 선택하세요. 최대 5명까지 입력 가능합니다."
        )
    
    st.session_state.shareholder_count = shareholder_count
    
    st.markdown("<div style='margin:10px 0; padding:10px; background-color:#f0f7fb; border-radius:5px; font-weight:bold;'>"
                f"주주 정보를 입력하세요 (선택된 주주 수: {shareholder_count}명)"
                "</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='field-description'>회사의 주주 정보를 입력하세요. 주주별 보유 주식수는 발행주식 총수를 초과할 수 없습니다.</div>", unsafe_allow_html=True)
    
    # 총 주식수 확인을 위한 변수
    total_owned_shares = 0
    
    # 선택한 수만큼의 주주 정보 입력
    shareholders = []
    for i in range(shareholder_count):
        col1, col2 = st.columns([1, 1])
        with col1:
            name = st.text_input(
                f"주주 {i+1} 이름", 
                value=st.session_state.shareholders[i]["name"] if i < len(st.session_state.shareholders) else "",
                key=f"shareholder_name_input_{i}",
                help=f"주주 {i+1}의 이름을 입력하세요."
            )
        
        with col2:
            shares_owned_str = st.text_input(
                f"보유 주식수", 
                value=format_number(st.session_state.shareholders[i]["shares"] if i < len(st.session_state.shareholders) else 0),
                key=f"shareholder_shares_input_{i}",
                help=f"주주 {i+1}의 보유 주식수를 입력하세요."
            )
            
            # 콤마 제거 후 숫자로 변환
            try:
                shares_owned = int(remove_commas(shares_owned_str))
                if shares_owned < 0:
                    shares_owned = 0
                if shares_owned > shares:
                    shares_owned = shares
            except:
                shares_owned = 0
            
            st.markdown(f"<div class='amount-display'>{format_number(shares_owned)}주</div>", unsafe_allow_html=True)
        
        # 구분선 추가
        if i < shareholder_count - 1:
            st.markdown("<hr style='margin:10px 0; border-color:#eee;'>", unsafe_allow_html=True)
        
        shareholders.append({"name": name, "shares": shares_owned})
        total_owned_shares += shares_owned
    
    # 나머지 주주 정보 보존
    for i in range(shareholder_count, 5):
        if i < len(st.session_state.shareholders):
            shareholders.append(st.session_state.shareholders[i])
        else:
            shareholders.append({"name": "", "shares": 0})
    
    # 입력된 주식수 합계 확인
    ownership_percent = round(total_owned_shares/shares*100, 2) if shares > 0 else 0
    
    st.markdown(f"""
    <div style='margin-top:15px; padding:10px; border-radius:5px; 
         background-color:{"#e6f3e6" if total_owned_shares <= shares else "#f8d7da"}; 
         color:{"#0c5460" if total_owned_shares <= shares else "#721c24"};
         font-weight:bold;'>
        {'✅' if total_owned_shares <= shares else '⚠️'} 
        주주들의 총 보유 주식수: {format_number(total_owned_shares)}주 
        (발행주식수의 {ownership_percent}%)
        {' ※ 발행주식수를 초과했습니다.' if total_owned_shares > shares else ''}
    </div>
    """, unsafe_allow_html=True)
    
    # 대표이사 보유 주식수 설정
    owned_shares = shareholders[0]["shares"] if shareholders and shareholders[0]["name"] else 0
    
    # 세션 상태 업데이트
    st.session_state.shareholders = shareholders
    st.session_state.owned_shares = owned_shares

# 평가 방식 선택
with st.expander("평가 방식 선택", expanded=True):
    st.markdown("<div class='section-header'>비상장주식 평가 방법</div>", unsafe_allow_html=True)
    evaluation_method = st.selectbox(
        "비상장주식 평가 방법",
        ("일반법인", "부동산 과다법인", "순자산가치만 평가"),
        index=["일반법인", "부동산 과다법인", "순자산가치만 평가"].index(st.session_state.evaluation_method),
        key="evaluation_method_select",
        help="상속세 및 증여세법 시행령 제54조에 근거한 평가 방법을 선택하세요.",
        label_visibility="collapsed"
    )
    
    st.markdown("""
    <div style='background-color:#f0f7fb; padding:15px; border-radius:5px; margin-top:15px;'>
    <span style='font-weight:bold; font-size:16px;'>📌 평가방식 설명</span>
    <ul style='margin-top:10px; margin-bottom:0; padding-left:20px;'>
        <li><strong>일반법인</strong>: 대부분의 법인에 적용 (수익가치 60% + 자산가치 40%)</li>
        <li><strong>부동산 과다법인</strong>: 부동산이 자산의 50% 이상인 법인 (자산가치 60% + 수익가치 40%)</li>
        <li><strong>순자산가치만 평가</strong>: 특수한 경우 (설립 1년 미만 등) (순자산가치 100%)</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div class='field-description'>상속세 및 증여세법 시행령 제54조에 근거한 평가방법입니다. 회사의 특성에 맞는 방법을 선택하세요.</div>", unsafe_allow_html=True)

# 계산 버튼
st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

if st.button("비상장주식 평가하기", type="primary", use_container_width=True, key="evaluate_button"):
    with st.spinner("계산 중..."):
        # 세션 상태 업데이트
        st.session_state.eval_date = eval_date
        st.session_state.company_name = company_name
        st.session_state.total_equity = st.session_state.total_equity
        st.session_state.net_income1 = st.session_state.net_income1
        st.session_state.net_income2 = st.session_state.net_income2
        st.session_state.net_income3 = st.session_state.net_income3
        st.session_state.shares = shares
        st.session_state.owned_shares = owned_shares
        st.session_state.share_price = st.session_state.share_price
        st.session_state.interest_rate = 10  # 환원율 10% 고정
        st.session_state.evaluation_method = evaluation_method
        st.session_state.shareholders = shareholders
        
        # 주식 가치 계산
        st.session_state.stock_value = calculate_stock_value()
        st.session_state.evaluated = True
        
        st.success(f"✅ 계산이 완료되었습니다. 평가기준일: {eval_date.strftime('%Y년 %m월 %d일')} 기준")
        st.balloons()

# 결과 표시
if st.session_state.evaluated and st.session_state.stock_value:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("평가 결과")
    
    # 결과 데이터
    stock_value = st.session_state.stock_value
    
    # 3열 레이아웃
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("##### 순자산가치")
        st.markdown(f"<div style='font-size:20px; font-weight:bold;'>{format_number(stock_value['netAssetPerShare'])}원/주</div>", unsafe_allow_html=True)
        st.markdown(f"총 {format_number(stock_value['netAssetPerShare'] * shares)}원")
    
    with col2:
        st.markdown("##### 수익가치")
        st.markdown(f"<div style='font-size:20px; font-weight:bold;'>{format_number(stock_value['incomeValue'])}원/주</div>", unsafe_allow_html=True)
        st.markdown(f"총 {format_number(stock_value['incomeValue'] * shares)}원")
    
    with col3:
        st.markdown("##### 최종 평가액")
        st.markdown(f"<div style='font-size:24px; font-weight:bold; color:#0066cc;'>{format_number(stock_value['finalValue'])}원/주</div>", unsafe_allow_html=True)
        st.markdown(f"총 {format_number(stock_value['totalValue'])}원")
    
    # 평가 방법 설명
    st.markdown(f"""
    <div style='margin-top:20px; padding:15px; background-color:#f8f9fa; border-radius:8px;'>
    <h5>적용된 평가 방식: {stock_value['methodText']}</h5>
    <p>최종 평가액은 자본총계 {format_number(total_equity)}원을 기준으로 계산되었으며, 
    가중평균 당기순이익 {format_number(stock_value['weightedIncome'])}원과 
    환원율 {st.session_state.interest_rate}%를 적용하여 산출되었습니다.</p>
    </div>
    """, unsafe_allow_html=True)

    # 다운로드 섹션
    with st.expander("📥 평가 결과 다운로드", expanded=False):
        st.markdown("<div class='download-section'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["HTML", "CSV"])
        
        with tab1:
            if st.button("HTML 파일 생성하기", key="generate_html"):
                html_content = create_html_content()
                st.download_button(
                    label="📄 HTML 파일 다운로드",
                    data=html_content,
                    file_name=f"비상장주식_평가_{st.session_state.company_name}_{st.session_state.eval_date}.html",
                    mime="text/html"
                )
        
        with tab2:
            if st.button("CSV 파일 생성하기", key="generate_csv"):
                csv_content = create_csv_content()
                if csv_content:
                    st.download_button(
                        label="📄 CSV 파일 다운로드",
                        data=csv_content,
                        file_name=f"비상장주식_평가_{st.session_state.company_name}_{st.session_state.eval_date}.csv",
                        mime="text/csv"
                    )
        st.markdown("</div>", unsafe_allow_html=True)
