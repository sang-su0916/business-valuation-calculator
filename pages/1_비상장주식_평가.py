# 1. 비상장주식 평가 페이지
if page == "1. 비상장주식 평가":
    st.title("비상장주식 가치평가")
    
    with st.expander("회사 정보", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("회사명", value="주식회사 에이비씨")
        
        with col2:
            total_equity = st.number_input("자본총계 (원)", 
                                          value=1002804000, 
                                          min_value=0, 
                                          format="%d")
    
    with st.expander("당기순이익 (최근 3개년)", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 1년 전 (가중치 3배)")
            net_income1 = st.number_input("당기순이익 1년 전 (원)", 
                                         value=386650000, 
                                         format="%d")
            
        with col2:
            st.markdown("#### 2년 전 (가중치 2배)")
            net_income2 = st.number_input("당기순이익 2년 전 (원)", 
                                         value=163401000, 
                                         format="%d")
            
        with col3:
            st.markdown("#### 3년 전 (가중치 1배)")
            net_income3 = st.number_input("당기순이익 3년 전 (원)", 
                                         value=75794000, 
                                         format="%d")
    
    with st.expander("주식 정보", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            shares = st.number_input("총 발행주식수", 
                                   value=4000, 
                                   min_value=1, 
                                   format="%d")
            
            owned_shares = st.number_input("대표이사 보유 주식수", 
                                          value=2000, 
                                          min_value=0, 
                                          max_value=shares, 
                                          format="%d")
            
        with col2:
            share_price = st.number_input("액면금액 (원)", 
                                         value=5000, 
                                         min_value=0, 
                                         format="%d")
            
            # 환원율 슬라이더를 고정값으로 변경
            # interest_rate = st.slider("환원율 (%)", 
            #                         min_value=1, 
            #                         max_value=20, 
            #                         value=10, 
            #                         help="일반적으로 10% 사용 (시장금리 반영)")
            interest_rate = 10
            st.info("환원율: 10% (기본값으로 적용)")
    
    with st.expander("평가 방식 선택", expanded=True):
        evaluation_method = st.selectbox(
            "비상장주식 평가 방법을 선택하세요",
            ("일반법인", "부동산 과다법인", "순자산가치만 평가"),
            help="상속세 및 증여세법 시행령 제54조 근거"
        )
        
        st.markdown("""
        <div class="highlight-box">
        <h4>📌 평가방식 설명</h4>
        <ul>
            <li><strong>일반법인</strong>: 대부분의 법인에 적용 (수익가치 60% + 자산가치 40%)</li>
            <li><strong>부동산 과다법인</strong>: 부동산이 자산의 50% 이상인 법인 (자산가치 60% + 수익가치 40%)</li>
            <li><strong>순자산가치만 평가</strong>: 특수한 경우 (설립 1년 미만 등) (순자산가치 100%)</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # 데이터 불러오기/저장 기능을 숨김 처리
    with st.expander("데이터 저장 및 불러오기", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 현재 데이터 저장")
            if st.button("현재 입력값 JSON으로 다운로드"):
                input_data = {
                    "company_name": company_name,
                    "total_equity": total_equity,
                    "net_income1": net_income1,
                    "net_income2": net_income2,
                    "net_income3": net_income3,
                    "shares": shares,
                    "owned_shares": owned_shares,
                    "share_price": share_price,
                    "interest_rate": interest_rate,
                    "evaluation_method": evaluation_method
                }
                
                # 데이터프레임으로 변환하여 다운로드 링크 생성
                df = pd.DataFrame([input_data])
                st.markdown(get_table_download_link(df, f"{company_name}_평가데이터", "📥 다운로드하기"), unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 저장된 데이터 불러오기")
            uploaded_file = st.file_uploader("파일을 업로드하세요", type=["xlsx", "xls", "pdf", "doc", "docx"])
            if uploaded_file is not None:
                try:
                    df = pd.read_excel(uploaded_file)
                    st.success("파일을 성공적으로 불러왔습니다!")
                    
                    if st.button("불러온 데이터로 설정"):
                        # 데이터를 입력 필드에 설정
                        st.session_state.company_name = df.iloc[0]['company_name']
                        st.session_state.total_equity = df.iloc[0]['total_equity']
                        st.session_state.net_income1 = df.iloc[0]['net_income1']
                        st.session_state.net_income2 = df.iloc[0]['net_income2']
                        st.session_state.net_income3 = df.iloc[0]['net_income3']
                        st.session_state.shares = df.iloc[0]['shares']
                        st.session_state.owned_shares = df.iloc[0]['owned_shares']
                        st.session_state.share_price = df.iloc[0]['share_price']
                        st.session_state.interest_rate = df.iloc[0]['interest_rate']
                        st.session_state.evaluation_method = df.iloc[0]['evaluation_method']
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"파일 로드 오류: {str(e)}")
    
    if st.button("비상장주식 평가하기", type="primary", use_container_width=True):
        with st.spinner("계산 중..."):
            st.session_state.stock_value = calculate_stock_value(
                total_equity, net_income1, net_income2, net_income3, 
                shares, interest_rate, evaluation_method, owned_shares
            )
            st.session_state.evaluated = True
            # 세션 상태에 입력 값 저장
            st.session_state.company_name = company_name
            st.session_state.total_equity = total_equity
            st.session_state.shares = shares
            st.session_state.owned_shares = owned_shares
            st.session_state.share_price = share_price
            st.session_state.interest_rate = interest_rate
            st.session_state.evaluation_method = evaluation_method
            
            st.success("계산이 완료되었습니다. '2. 주식가치 결과' 탭에서 결과를 확인하세요.")
            st.balloons()
            # 페이지 자동 전환을 위한 쿼리 파라미터 설정
            st.experimental_set_query_params(page="2")
            st.experimental_rerun()
