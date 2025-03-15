import streamlit as st
import pandas as pd
import numpy as np
import locale

# 숫자 형식화를 위한 로케일 설정 - 한국어 로케일로 변경
try:
    locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'ko_KR')
    except:
        locale.setlocale(locale.LC_ALL, '')

# 페이지 레이아웃 개선을 위한 CSS
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
    .formatted-amount {
        color: #0066cc;
        font-weight: bold;
        margin-top: 0.2rem;
        font-size: 0.9rem;
    }
    /* 입력 필드 정렬 */
    .stNumberInput {
        width: 100%;
    }
    /* 금액 표시 스타일 */
    .amount-display {
        color: #0066cc;
        font-weight: bold;
        padding: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'company_name' not in st.session_state:
    st.session_state.company_name = "주식회사 에이비씨"
if 'total_equity' not in st.session_state:
    st.session_state.total_equity = 1002804000
if 'net_income1' not in st.session_state:
    st.session_state.net_income1 = 386650000
if 'net_income2' not in st.session_state:
    st.session_state.net_income2 = 163401000
if 'net_income3' not in st.session_state:
    st.session_state.net_income3 = 75794000
if 'shares' not in st.session_state:
    st.session_state.shares = 4000
if 'owned_shares' not in st.session_state:
    st.session_state.owned_shares = 2000
if 'share_price' not in st.session_state:
    st.session_state.share_price = 5000
if 'interest_rate' not in st.session_state:
    st.session_state.interest_rate = 10
if 'evaluation_method' not in st.session_state:
    st.session_state.evaluation_method = "일반법인"
if 'stock_value' not in st.session_state:
    st.session_state.stock_value = None
if 'evaluated' not in st.session_state:
    st.session_state.evaluated = False
if 'shareholders' not in st.session_state:
    st.session_state.shareholders = [
        {"name": "대표이사", "shares": 2000},
        {"name": "", "shares": 0},
        {"name": "", "shares": 0},
        {"name": "", "shares": 0},
        {"name": "", "shares": 0}
    ]
if 'shareholder_count' not in st.session_state:
    st.session_state.shareholder_count = 1

# 숫자 형식화 함수
def format_number(num):
    try:
        return "{:,}".format(int(num))  # 더 간단하고 확실한 방법
    except:
        return str(num)

# 페이지 헤더
st.title("비상장주식 가치평가")

# 회사 정보 입력
with st.expander("회사 정보", expanded=True):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        company_name = st.text_input("회사명", value=st.session_state.company_name)
    
    with col2:
        total_equity = st.number_input("자본총계 (원)", 
                                     value=st.session_state.total_equity, 
                                     min_value=0, 
                                     format="%d")
        st.markdown(f"<div class='amount-display'>금액: {format_number(total_equity)}원</div>", unsafe_allow_html=True)

# 당기순이익 입력 - key 충돌 해결
with st.expander("당기순이익 (최근 3개년)", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("##### 1년 전 (가중치 3배)")
        # key를 명확하게 구분
        net_income1 = st.number_input("당기순이익 (원)", 
                                    value=st.session_state.net_income1, 
                                    format="%d",
                                    key="income_year1_input")
        st.markdown(f"<div class='amount-display'>금액: {format_number(net_income1)}원</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("##### 2년 전 (가중치 2배)")
        net_income2 = st.number_input("당기순이익 (원)", 
                                    value=st.session_state.net_income2, 
                                    format="%d",
                                    key="income_year2_input")
        st.markdown(f"<div class='amount-display'>금액: {format_number(net_income2)}원</div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown("##### 3년 전 (가중치 1배)")
        net_income3 = st.number_input("당기순이익 (원)", 
                                    value=st.session_state.net_income3, 
                                    format="%d",
                                    key="income_year3_input")
        st.markdown(f"<div class='amount-display'>금액: {format_number(net_income3)}원</div>", unsafe_allow_html=True)

# 주식 정보 입력
with st.expander("주식 정보", expanded=True):
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        shares = st.number_input("총 발행주식수", 
                               value=st.session_state.shares, 
                               min_value=1, 
                               format="%d",
                               key="shares_input")
        st.markdown(f"<div class='amount-display'>총 {format_number(shares)}주</div>", unsafe_allow_html=True)
        
    with col2:
        share_price = st.number_input("액면금액 (원)", 
                                    value=st.session_state.share_price, 
                                    min_value=0, 
                                    format="%d",
                                    key="share_price_input")
        st.markdown(f"<div class='amount-display'>금액: {format_number(share_price)}원</div>", unsafe_allow_html=True)
        
    with col3:
        interest_rate = st.slider("환원율 (%)", 
                                min_value=1, 
                                max_value=20, 
                                value=st.session_state.interest_rate,
                                key="interest_rate_slider", 
                                help="일반적으로 10% 사용 (시장금리 반영)")

# 주주 정보 입력
with st.expander("주주 정보", expanded=True):
    col1, col2 = st.columns([2, 2])
    
    with col1:
        shareholder_count = st.selectbox(
            "입력할 주주 수",
            options=[1, 2, 3, 4, 5],
            index=st.session_state.shareholder_count - 1,
            key="shareholder_count_select"
        )
    
    st.session_state.shareholder_count = shareholder_count
    
    st.markdown("<div style='margin:10px 0; padding:10px; background-color:#f0f7fb; border-radius:5px; font-weight:bold;'>"
                f"주주 정보를 입력하세요 (선택된 주주 수: {shareholder_count}명)"
                "</div>", unsafe_allow_html=True)
    
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
                key=f"shareholder_name_input_{i}"
            )
        with col2:
            shares_owned = st.number_input(
                f"보유 주식수", 
                value=st.session_state.shareholders[i]["shares"] if i < len(st.session_state.shareholders) else 0, 
                min_value=0,
                max_value=shares,
                format="%d",
                key=f"shareholder_shares_input_{i}"
            )
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

# 평가 방식 선택
with st.expander("평가 방식 선택", expanded=True):
    evaluation_method = st.selectbox(
        "비상장주식 평가 방법",
        ("일반법인", "부동산 과다법인", "순자산가치만 평가"),
        index=["일반법인", "부동산 과다법인", "순자산가치만 평가"].index(st.session_state.evaluation_method),
        key="evaluation_method_select"
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

# 비상장주식 가치 계산 함수
def calculate_stock_value():
    # 계산 로직 (이전과 동일)
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
    increase_percentage = round((final_value / net_asset_per_share) * 100)
    
    return {
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

# 계산 버튼
st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
st.markdown("""
<style>
.big-button {
    background-color: #4CAF50;
    color: white;
    padding: 12px 20px;
    font-size: 16px;
    border-radius: 5px;
    border: none;
    cursor: pointer;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

if st.button("비상장주식 평가하기", type="primary", use_container_width=True, key="evaluate_button"):
    with st.spinner("계산 중..."):
        # 세션 상태 업데이트
        st.session_state.company_name = company_name
        st.session_state.total_equity = total_equity
        st.session_state.net_income1 = net_income1
        st.session_state.net_income2 = net_income2
        st.session_state.net_income3 = net_income3
        st.session_state.shares = shares
        st.session_state.owned_shares = owned_shares
        st.session_state.share_price = share_price
        st.session_state.interest_rate = interest_rate
        st.session_state.evaluation_method = evaluation_method
        st.session_state.shareholders = shareholders
        
        # 주식 가치 계산
        st.session_state.stock_value = calculate_stock_value()
        st.session_state.evaluated = True
        
        st.success("✅ 계산이 완료되었습니다. '주식가치 결과' 페이지에서 결과를 확인하세요.")
        st.balloons()
