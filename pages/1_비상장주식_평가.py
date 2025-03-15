import streamlit as st
import pandas as pd
import numpy as np
import locale

# 숫자 형식화를 위한 로케일 설정
locale.setlocale(locale.LC_ALL, '')

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

# 숫자 형식화 함수
def format_number(num):
    return locale.format_string("%d", int(num), grouping=True)

# 페이지 헤더
st.title("비상장주식 가치평가")

# 회사 정보 입력
with st.expander("회사 정보", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input("회사명", value=st.session_state.company_name)
    
    with col2:
        total_equity = st.number_input("자본총계 (원)", 
                                     value=st.session_state.total_equity, 
                                     min_value=0, 
                                     format="%d")
        st.text(f"표시 금액: {format_number(total_equity)}원")

# 당기순이익 입력
with st.expander("당기순이익 (최근 3개년)", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("1년 전 (가중치 3배)")
        net_income1 = st.number_input("당기순이익 1년 전 (원)", 
                                    value=st.session_state.net_income1, 
                                    format="%d")
        st.text(f"표시 금액: {format_number(net_income1)}원")
        
    with col2:
        st.subheader("2년 전 (가중치 2배)")
        net_income2 = st.number_input("당기순이익 2년 전 (원)", 
                                    value=st.session_state.net_income2, 
                                    format="%d")
        st.text(f"표시 금액: {format_number(net_income2)}원")
        
    with col3:
        st.subheader("3년 전 (가중치 1배)")
        net_income3 = st.number_input("당기순이익 3년 전 (원)", 
                                    value=st.session_state.net_income3, 
                                    format="%d")
        st.text(f"표시 금액: {format_number(net_income3)}원")

# 주식 정보 입력
with st.expander("주식 정보", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        shares = st.number_input("총 발행주식수", 
                               value=st.session_state.shares, 
                               min_value=1, 
                               format="%d")
        st.text(f"표시 금액: {format_number(shares)}주")
        
    with col2:
        share_price = st.number_input("액면금액 (원)", 
                                    value=st.session_state.share_price, 
                                    min_value=0, 
                                    format="%d")
        st.text(f"표시 금액: {format_number(share_price)}원")
        
        interest_rate = st.slider("환원율 (%)", 
                                min_value=1, 
                                max_value=20, 
                                value=st.session_state.interest_rate, 
                                help="일반적으로 10% 사용 (시장금리 반영)")

# 주주 정보 입력
with st.expander("주주 정보", expanded=True):
    st.info("회사의 주주 정보를 입력하세요 (최대 5명)")
    
    # 총 주식수 확인을 위한 변수
    total_owned_shares = 0
    
    # 5명의 주주 정보 입력
    shareholders = []
    for i in range(5):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(
                f"주주 {i+1} 이름", 
                value=st.session_state.shareholders[i]["name"] if i < len(st.session_state.shareholders) else "",
                key=f"shareholder_name_{i}"
            )
        with col2:
            shares_owned = st.number_input(
                f"보유 주식수", 
                value=st.session_state.shareholders[i]["shares"] if i < len(st.session_state.shareholders) else 0, 
                min_value=0,
                max_value=shares,
                format="%d",
                key=f"shareholder_shares_{i}"
            )
            st.text(f"표시 금액: {format_number(shares_owned)}주")
        
        shareholders.append({"name": name, "shares": shares_owned})
        total_owned_shares += shares_owned
    
    # 입력된 주식수 합계 확인
    if total_owned_shares > shares:
        st.error(f"입력된 주주들의 총 보유 주식수({format_number(total_owned_shares)}주)가 발행주식수({format_number(shares)}주)를 초과합니다.")
    else:
        st.success(f"주주들의 총 보유 주식수: {format_number(total_owned_shares)}주 (발행주식수의 {round(total_owned_shares/shares*100, 2)}%)")
    
    # 대표이사 보유 주식수 설정 (첫 번째 주주를 대표이사로 간주)
    owned_shares = shareholders[0]["shares"] if shareholders and shareholders[0]["name"] else 0

# 평가 방식 선택
with st.expander("평가 방식 선택", expanded=True):
    evaluation_method = st.selectbox(
        "비상장주식 평가 방법을 선택하세요",
        ("일반법인", "부동산 과다법인", "순자산가치만 평가"),
        index=["일반법인", "부동산 과다법인", "순자산가치만 평가"].index(st.session_state.evaluation_method),
        help="상속세 및 증여세법 시행령 제54조 근거"
    )
    
    st.info("""
    📌 **평가방식 설명**
    - **일반법인**: 대부분의 법인에 적용 (수익가치 60% + 자산가치 40%)
    - **부동산 과다법인**: 부동산이 자산의 50% 이상인 법인 (자산가치 60% + 수익가치 40%)
    - **순자산가치만 평가**: 특수한 경우 (설립 1년 미만 등) (순자산가치 100%)
    """)

# 비상장주식 가치 계산 함수
def calculate_stock_value():
    # 1. 순자산가치 계산
    net_asset_per_share = total_equity / shares
    
    # 2. 영업권 계산
    weighted_income = (net_income1 * 3 + net_income2 * 2 + net_income3 * 1) / 6
    weighted_income_per_share = weighted_income / shares
    weighted_income_per_share_50 = weighted_income_per_share * 0.5
    equity_return = (total_equity * (interest_rate / 100)) / shares
    annuity_factor = 3.7908
    goodwill = max(0, (weighted_income_per_share_50 - equity_return) * annuity_factor)
    
    # 3. 순자산가치 + 영업권
    asset_value_with_goodwill = net_asset_per_share + goodwill
    
    # 4. 손익가치 계산
    income_value = weighted_income_per_share * (100 / interest_rate)
    
    # 5. 최종가치 계산
    if evaluation_method == "부동산 과다법인":
        # 부동산 과다법인
        stock_value = (asset_value_with_goodwill * 0.6) + (income_value * 0.4)
        net_asset_80_percent = net_asset_per_share * 0.8
        final_value = max(stock_value, net_asset_80_percent)
        method_text = '부동산 과다법인: (자산가치×0.6 + 수익가치×0.4)'
    elif evaluation_method == "순자산가치만 평가":
        # 순자산가치만 적용
        final_value = net_asset_per_share
        method_text = '순자산가치만 평가'
    else:
        # 일반법인
        stock_value = (income_value * 0.6) + (asset_value_with_goodwill * 0.4)
        net_asset_80_percent = net_asset_per_share * 0.8
        final_value = max(stock_value, net_asset_80_percent)
        method_text = '일반법인: (수익가치×0.6 + 자산가치×0.4)'
    
    # 총 가치
    total_value = final_value * shares
    owned_value = final_value * owned_shares
    
    # 증가율 계산
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
if st.button("비상장주식 평가하기", type="primary", use_container_width=True):
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
        
        st.success("계산이 완료되었습니다. '주식가치 결과' 페이지에서 결과를 확인하세요.")
        st.balloons()
