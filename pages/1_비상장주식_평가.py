# 환원율 고정 부분 수정 (st.slider 대신 고정값으로 표시)
# 주식 정보 입력 부분 중 환원율 관련 코드 수정

# 기존 코드:
"""
with col3:
    st.markdown("<div class='section-header'>환원율 (%)</div>", unsafe_allow_html=True)
    interest_rate = st.slider(
        "환원율 (%)", 
        min_value=1, 
        max_value=20, 
        value=st.session_state.interest_rate,
        key="interest_rate_slider", 
        help="수익가치 평가에 사용되는 환원율입니다. 일반적으로 시장금리를 반영하여 10%를 사용합니다.",
        label_visibility="collapsed"
    )
    st.markdown("<div class='field-description'>수익가치 평가 시 사용되는 할인율입니다. 일반적으로 10%를 적용합니다.</div>", unsafe_allow_html=True)
"""

# 수정 코드:
"""
with col3:
    st.markdown("<div class='section-header'>환원율 (%)</div>", unsafe_allow_html=True)
    # 환원율 10%로 고정
    interest_rate = 10
    st.markdown(f"<div style='font-size: 24px; font-weight: bold; color: #0066cc; padding: 10px 0;'>{interest_rate}%</div>", unsafe_allow_html=True)
    st.markdown("<div class='field-description'>수익가치 평가 시 사용되는 할인율입니다. 환원율은 10%로 고정되어 있습니다.</div>", unsafe_allow_html=True)
"""

# PDF 다운로드 기능 추가 (페이지 하단)
# HTML 다운로드 함수 외에 PDF 다운로드 기능 추가

# PDF 다운로드 함수
"""
def generate_pdf():
    try:
        # 필요한 라이브러리 import
        from fpdf import FPDF
        import tempfile
        
        # PDF 생성
        pdf = FPDF()
        pdf.add_page()
        
        # 폰트 설정
        pdf.add_font('NanumGothic', '', './NanumGothic.ttf', uni=True)
        pdf.set_font('NanumGothic', '', 12)
        
        # 제목
        pdf.set_font('NanumGothic', '', 16)
        pdf.cell(0, 10, '비상장주식 가치평가 데이터', 0, 1, 'C')
        pdf.ln(5)
        
        # 기본 정보
        pdf.set_font('NanumGothic', '', 12)
        pdf.cell(0, 10, f"평가 기준일: {st.session_state.eval_date.strftime('%Y년 %m월 %d일')}", 0, 1)
        pdf.cell(0, 10, f"회사명: {st.session_state.company_name}", 0, 1)
        pdf.cell(0, 10, f"자본총계: {format_number(st.session_state.total_equity)}원", 0, 1)
        pdf.ln(5)
        
        # 당기순이익
        pdf.cell(0, 10, "당기순이익 (최근 3개년)", 0, 1)
        pdf.cell(60, 8, "1년 전 (가중치 3배)", 1)
        pdf.cell(60, 8, f"{format_number(st.session_state.net_income1)}원", 1, 1)
        pdf.cell(60, 8, "2년 전 (가중치 2배)", 1)
        pdf.cell(60, 8, f"{format_number(st.session_state.net_income2)}원", 1, 1)
        pdf.cell(60, 8, "3년 전 (가중치 1배)", 1)
        pdf.cell(60, 8, f"{format_number(st.session_state.net_income3)}원", 1, 1)
        pdf.ln(5)
        
        # 주식 정보
        pdf.cell(0, 10, "주식 정보", 0, 1)
        pdf.cell(60, 8, "총 발행주식수", 1)
        pdf.cell(60, 8, f"{format_number(st.session_state.shares)}주", 1, 1)
        pdf.cell(60, 8, "액면금액", 1)
        pdf.cell(60, 8, f"{format_number(st.session_state.share_price)}원", 1, 1)
        pdf.cell(60, 8, "환원율", 1)
        pdf.cell(60, 8, f"{st.session_state.interest_rate}%", 1, 1)
        pdf.ln(5)
        
        # 주주 정보
        pdf.cell(0, 10, "주주 정보", 0, 1)
        total_shares = 0
        for i in range(st.session_state.shareholder_count):
            if st.session_state.shareholders[i]["name"]:
                pdf.cell(60, 8, st.session_state.shareholders[i]["name"], 1)
                pdf.cell(60, 8, f"{format_number(st.session_state.shareholders[i]['shares'])}주", 1, 1)
                total_shares += st.session_state.shareholders[i]["shares"]
        pdf.cell(0, 10, f"주주들의 총 보유 주식수: {format_number(total_shares)}주 (발행주식수의 {round(total_shares/st.session_state.shares*100, 2)}%)", 0, 1)
        pdf.ln(5)
        
        # 평가 방식
        pdf.cell(0, 10, "평가 방식", 0, 1)
        pdf.cell(60, 8, "선택한 평가 방식", 1)
        pdf.cell(60, 8, st.session_state.evaluation_method, 1, 1)
        
        # 평가 방식 설명
        if st.session_state.evaluation_method == "일반법인":
            method_explanation = "일반법인: 대부분의 법인에 적용 (수익가치 60% + 자산가치 40%)"
        elif st.session_state.evaluation_method == "부동산 과다법인":
            method_explanation = "부동산 과다법인: 부동산이 자산의 50% 이상인 법인 (자산가치 60% + 수익가치 40%)"
        else:
            method_explanation = "순자산가치만 평가: 특수한 경우 (설립 1년 미만 등) (순자산가치 100%)"
        
        pdf.cell(0, 10, method_explanation, 0, 1)
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_path = temp_file.name
            pdf.output(temp_path)
        
        # 파일 읽기
        with open(temp_path, "rb") as f:
            return f.read()
            
    except Exception as e:
        st.error(f"PDF 생성 중 오류 발생: {e}")
        return None

# PDF 다운로드 함수 (Base64 인코딩)
def get_pdf_download_link():
    try:
        pdf_data = generate_pdf()
        if pdf_data:
            b64 = base64.b64encode(pdf_data).decode()
            return f'<a href="data:application/pdf;base64,{b64}" download="비상장주식_평가_데이터.pdf" class="download-button">📊 평가 데이터 PDF 다운로드</a>'
        else:
            return "PDF 생성에 실패했습니다."
    except Exception as e:
        return f"PDF 다운로드 링크 생성 실패: {e}"
"""

# HTML/CSV 다운로드 탭에 PDF 다운로드 옵션 추가
"""
with tabs[1]:
    st.markdown("### 데이터 다운로드")
    st.markdown("평가 데이터를 다운로드 할 수 있습니다.")
    
    # CSV 다운로드
    st.markdown(get_csv_download_link(), unsafe_allow_html=True)
    
    # HTML 다운로드 (PDF 형식으로 볼 수 있음)
    st.markdown(get_html_download_link(), unsafe_allow_html=True)
    
    # PDF 다운로드 (새로 추가)
    try:
        from fpdf import FPDF
        st.markdown(get_pdf_download_link(), unsafe_allow_html=True)
    except ImportError:
        st.warning("PDF 다운로드 기능을 사용하려면 'fpdf' 라이브러리가 필요합니다.")
        st.markdown('''
        ```
        pip install fpdf
        ```
        ''')
"""

# 페이지 하단에 PDF 다운로드 버튼 추가 (계산 버튼 아래)
"""
st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

if st.button("비상장주식 평가하기", type="primary", use_container_width=True, key="evaluate_button"):
    with st.spinner("계산 중..."):
        # 세션 상태 업데이트
        st.session_state.eval_date = eval_date
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
        
        st.success(f"✅ 계산이 완료되었습니다. 평가기준일: {eval_date.strftime('%Y년 %m월 %d일')} 기준 - '주식가치 결과' 페이지에서 결과를 확인하세요.")
        st.balloons()

# PDF 다운로드 버튼 (페이지 하단에 추가)
if st.session_state.evaluated:
    st.markdown("<div style='margin-top: 20px;'>", unsafe_allow_html=True)
    try:
        from fpdf import FPDF
        st.markdown(get_pdf_download_link(), unsafe_allow_html=True)
    except ImportError:
        st.download_button(
            label="📄 평가 데이터 다운로드",
            data=get_html_download_link(),
            file_name="비상장주식_평가_데이터.html",
            mime="text/html"
        )
    st.markdown("</div>", unsafe_allow_html=True)
"""
