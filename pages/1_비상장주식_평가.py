import streamlit as st
import pandas as pd
import numpy as np
import datetime
import io
import base64
from PIL import Image
import re
import json
import os

# FPDF 라이브러리 추가
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False
    st.warning("PDF 생성을 위한 FPDF 라이브러리가 설치되어 있지 않습니다. 'pip install fpdf'로 설치해주세요.")

# 파일 처리 라이브러리
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import xlsx
    XLSX_AVAILABLE = True
except ImportError:
    try:
        import openpyxl
        XLSX_AVAILABLE = True
    except ImportError:
        XLSX_AVAILABLE = False

# 페이지 설정
st.set_page_config(
    page_title="비상장주식 평가",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'company_name' not in st.session_state:
    st.session_state.company_name = ""
if 'total_capital' not in st.session_state:
    st.session_state.total_capital = 1000000000
if 'profit_1' not in st.session_state:
    st.session_state.profit_1 = 386650000
if 'profit_2' not in st.session_state:
    st.session_state.profit_2 = 163401000
if 'profit_3' not in st.session_state:
    st.session_state.profit_3 = 75794000
if 'shares_total' not in st.session_state:
    st.session_state.shares_total = 4000
if 'face_value' not in st.session_state:
    st.session_state.face_value = 5000
if 'capitalization_rate' not in st.session_state:
    st.session_state.capitalization_rate = 10.0  # 환원율 10%로 고정
if 'shareholder_count' not in st.session_state:
    st.session_state.shareholder_count = 1
if 'evaluation_date' not in st.session_state:
    st.session_state.evaluation_date = datetime.date.today()

# 사이드바 메뉴
st.sidebar.title("app")
st.sidebar.page_link("비상장주식 평가", label="비상장주식 평가", icon="📊")
st.sidebar.page_link("주식가치 결과", label="주식가치 결과", icon="📈")
st.sidebar.page_link("현시점 세금계산", label="현시점 세금계산", icon="💰")
st.sidebar.page_link("미래 주식가치", label="미래 주식가치", icon="🔮")
st.sidebar.page_link("미래 세금계산", label="미래 세금계산", icon="💸")

# 숫자 포맷팅 함수
def format_number(num):
    if num is None:
        return "0"
    return f"{int(num):,}"

# 추출한 데이터를 세션 상태에 적용하는 함수
def apply_extracted_data(extracted_data):
    if 'company_name' in extracted_data and extracted_data['company_name']:
        st.session_state.company_name = extracted_data['company_name']
    if 'total_capital' in extracted_data and extracted_data['total_capital']:
        st.session_state.total_capital = extracted_data['total_capital']
    if 'profit_1' in extracted_data and extracted_data['profit_1']:
        st.session_state.profit_1 = extracted_data['profit_1']
    if 'profit_2' in extracted_data and extracted_data['profit_2']:
        st.session_state.profit_2 = extracted_data['profit_2']
    if 'profit_3' in extracted_data and extracted_data['profit_3']:
        st.session_state.profit_3 = extracted_data['profit_3']
    if 'shares_total' in extracted_data and extracted_data['shares_total']:
        st.session_state.shares_total = extracted_data['shares_total']
    if 'face_value' in extracted_data and extracted_data['face_value']:
        st.session_state.face_value = extracted_data['face_value']

# 정규식 패턴
def find_with_patterns(text, patterns):
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # 숫자만 추출
            for match in matches:
                num_str = re.sub(r'[^\d]', '', match)
                if num_str:
                    return int(num_str)
    return None

# 파일에서 데이터 추출
def extract_data_from_file(uploaded_file):
    extracted_data = {}
    
    # 파일 확장자 확인
    file_ext = uploaded_file.name.split('.')[-1].lower()
    
    # 텍스트 추출
    text_content = ""
    
    # 1. Excel 파일 처리
    if file_ext in ['xlsx', 'xls'] and XLSX_AVAILABLE:
        try:
            df = pd.read_excel(uploaded_file)
            # DataFrame을 텍스트로 변환
            text_content = df.to_string()
            
            # 열 이름으로 데이터 찾기
            for col in df.columns:
                col_lower = col.lower()
                if '회사' in col_lower or 'company' in col_lower:
                    for idx, val in df[col].items():
                        if isinstance(val, str) and len(val) > 1:
                            extracted_data['company_name'] = val
                            break
                
                if '자본' in col_lower or 'capital' in col_lower:
                    for idx, val in df[col].items():
                        if isinstance(val, (int, float)) and val > 0:
                            extracted_data['total_capital'] = int(val)
                            break
                
                if '당기순이익' in col_lower or 'profit' in col_lower:
                    profit_values = [val for idx, val in df[col].items() 
                                    if isinstance(val, (int, float)) and val > 0]
                    if len(profit_values) >= 3:
                        extracted_data['profit_1'] = int(profit_values[0])
                        extracted_data['profit_2'] = int(profit_values[1])
                        extracted_data['profit_3'] = int(profit_values[2])
                    elif len(profit_values) == 2:
                        extracted_data['profit_1'] = int(profit_values[0])
                        extracted_data['profit_2'] = int(profit_values[1])
                    elif len(profit_values) == 1:
                        extracted_data['profit_1'] = int(profit_values[0])
                
                if '주식' in col_lower or 'shares' in col_lower:
                    for idx, val in df[col].items():
                        if isinstance(val, (int, float)) and val > 0:
                            extracted_data['shares_total'] = int(val)
                            break
                
                if '액면' in col_lower or 'face' in col_lower:
                    for idx, val in df[col].items():
                        if isinstance(val, (int, float)) and val > 0:
                            extracted_data['face_value'] = int(val)
                            break
        except Exception as e:
            st.error(f"엑셀 파일 처리 중 오류가 발생했습니다: {str(e)}")
    
    # 2. Word 파일 처리
    elif file_ext in ['docx', 'doc'] and DOCX_AVAILABLE:
        try:
            doc = docx.Document(uploaded_file)
            paragraphs = [p.text for p in doc.paragraphs]
            text_content = "\n".join(paragraphs)
        except Exception as e:
            st.error(f"워드 파일 처리 중 오류가 발생했습니다: {str(e)}")
    
    # 3. PDF 파일 처리
    elif file_ext == 'pdf' and PYPDF2_AVAILABLE:
        try:
            pdf_reader = PyPDF2.PdfFileReader(uploaded_file)
            text_content = ""
            for page_num in range(pdf_reader.numPages):
                text_content += pdf_reader.getPage(page_num).extractText()
        except Exception as e:
            st.error(f"PDF 파일 처리 중 오류가 발생했습니다: {str(e)}")
    
    # 텍스트에서 패턴으로 데이터 추출
    if text_content:
        # 회사명 패턴
        company_patterns = [
            r'회사\s*명\s*[:\s]+([^\n\r,]+)',
            r'회사\s*[:\s]+([^\n\r,]+)',
            r'상호\s*[:\s]+([^\n\r,]+)'
        ]
        for pattern in company_patterns:
            matches = re.findall(pattern, text_content)
            if matches:
                extracted_data['company_name'] = matches[0].strip()
                break
        
        # 자본총계 패턴
        capital_patterns = [
            r'자본총계\s*[:\s]+([\d,\.]+)',
            r'자본\s*[:\s]+([\d,\.]+)',
            r'총자본\s*[:\s]+([\d,\.]+)',
            r'capital\s*[:\s]+([\d,\.]+)'
        ]
        extracted_data['total_capital'] = find_with_patterns(text_content, capital_patterns)
        
        # 당기순이익 패턴
        profit_patterns = [
            r'당기순이익\s*[:\s]+([\d,\.]+)',
            r'순이익\s*[:\s]+([\d,\.]+)',
            r'profit\s*[:\s]+([\d,\.]+)'
        ]
        profit_matches = []
        for pattern in profit_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            profit_matches.extend(matches)
        
        if len(profit_matches) >= 3:
            extracted_data['profit_1'] = int(re.sub(r'[^\d]', '', profit_matches[0]))
            extracted_data['profit_2'] = int(re.sub(r'[^\d]', '', profit_matches[1]))
            extracted_data['profit_3'] = int(re.sub(r'[^\d]', '', profit_matches[2]))
        elif len(profit_matches) == 2:
            extracted_data['profit_1'] = int(re.sub(r'[^\d]', '', profit_matches[0]))
            extracted_data['profit_2'] = int(re.sub(r'[^\d]', '', profit_matches[1]))
        elif len(profit_matches) == 1:
            extracted_data['profit_1'] = int(re.sub(r'[^\d]', '', profit_matches[0]))
        
        # 주식수 패턴
        shares_patterns = [
            r'발행주식수\s*[:\s]+([\d,\.]+)',
            r'주식수\s*[:\s]+([\d,\.]+)',
            r'shares\s*[:\s]+([\d,\.]+)'
        ]
        extracted_data['shares_total'] = find_with_patterns(text_content, shares_patterns)
        
        # 액면가 패턴
        face_value_patterns = [
            r'액면가\s*[:\s]+([\d,\.]+)',
            r'액면금액\s*[:\s]+([\d,\.]+)',
            r'face value\s*[:\s]+([\d,\.]+)'
        ]
        extracted_data['face_value'] = find_with_patterns(text_content, face_value_patterns)
    
    return extracted_data

# PDF 생성 함수
def generate_pdf():
    if not FPDF_AVAILABLE:
        st.error("PDF 생성을 위한 FPDF 라이브러리가 설치되어 있지 않습니다.")
        return None
    
    try:
        # PDF 객체 생성
        pdf = FPDF()
        pdf.add_page()
        
        # 기본 폰트 사용 (한글 대신 기본 폰트)
        pdf.set_font('Arial', 'B', 16)
        
        # 제목
        pdf.cell(190, 10, '비상장주식 가치평가 보고서', 0, 1, 'C')
        pdf.ln(10)
        
        # 기본 폰트 설정
        pdf.set_font('Arial', '', 12)
        
        # 평가 정보
        pdf.cell(190, 10, f'평가 기준일: {st.session_state.evaluation_date}', 0, 1)
        pdf.cell(190, 10, f'회사명: {st.session_state.company_name}', 0, 1)
        pdf.ln(5)
        
        # 재무 정보
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(190, 10, '재무 정보', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(190, 10, f'자본총계: {format_number(st.session_state.total_capital)}원', 0, 1)
        pdf.cell(190, 10, f'1년 전 당기순이익: {format_number(st.session_state.profit_1)}원 (가중치 3배)', 0, 1)
        pdf.cell(190, 10, f'2년 전 당기순이익: {format_number(st.session_state.profit_2)}원 (가중치 2배)', 0, 1)
        pdf.cell(190, 10, f'3년 전 당기순이익: {format_number(st.session_state.profit_3)}원 (가중치 1배)', 0, 1)
        pdf.ln(5)
        
        # 주식 정보
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(190, 10, '주식 정보', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(190, 10, f'총 발행주식수: {format_number(st.session_state.shares_total)}주', 0, 1)
        pdf.cell(190, 10, f'액면금액: {format_number(st.session_state.face_value)}원', 0, 1)
        pdf.cell(190, 10, f'환원율: {st.session_state.capitalization_rate}%', 0, 1)
        pdf.ln(5)
        
        # 평가 결과
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(190, 10, '평가 결과', 0, 1)
        pdf.set_font('Arial', '', 12)
        
        # 수익가치
        weighted_profit = (st.session_state.profit_1 * 3 + 
                          st.session_state.profit_2 * 2 + 
                          st.session_state.profit_1 * 1) / 6
        income_value = weighted_profit / (st.session_state.capitalization_rate / 100)
        income_value_per_share = income_value / st.session_state.shares_total
        
        # 자산가치
        asset_value = st.session_state.total_capital
        asset_value_per_share = asset_value / st.session_state.shares_total
        
        # 일반법인 평가액
        normal_value = income_value * 0.6 + asset_value * 0.4
        normal_value_per_share = normal_value / st.session_state.shares_total
        
        # 부동산 과다법인 평가액
        real_estate_value = income_value * 0.4 + asset_value * 0.6
        real_estate_value_per_share = real_estate_value / st.session_state.shares_total
        
        # 순자산가치 평가액
        net_asset_value = asset_value
        net_asset_value_per_share = net_asset_value / st.session_state.shares_total
        
        pdf.cell(190, 10, f'수익가치: {format_number(income_value)}원 (주당 {format_number(income_value_per_share)}원)', 0, 1)
        pdf.cell(190, 10, f'자산가치: {format_number(asset_value)}원 (주당 {format_number(asset_value_per_share)}원)', 0, 1)
        pdf.ln(5)
        
        pdf.cell(190, 10, f'일반법인 평가액: {format_number(normal_value)}원 (주당 {format_number(normal_value_per_share)}원)', 0, 1)
        pdf.cell(190, 10, f'부동산 과다법인 평가액: {format_number(real_estate_value)}원 (주당 {format_number(real_estate_value_per_share)}원)', 0, 1)
        pdf.cell(190, 10, f'순자산가치 평가액: {format_number(net_asset_value)}원 (주당 {format_number(net_asset_value_per_share)}원)', 0, 1)
        
        # PDF를 바이트로 변환
        pdf_output = pdf.output(dest='S').encode('latin-1')
        return pdf_output
    
    except Exception as e:
        st.error(f"PDF 생성 중 오류가 발생했습니다: {str(e)}")
        return None

# HTML 다운로드용 내용 생성
def create_html_content():
    # 수익가치
    weighted_profit = (st.session_state.profit_1 * 3 + 
                      st.session_state.profit_2 * 2 + 
                      st.session_state.profit_1 * 1) / 6
    income_value = weighted_profit / (st.session_state.capitalization_rate / 100)
    income_value_per_share = income_value / st.session_state.shares_total
    
    # 자산가치
    asset_value = st.session_state.total_capital
    asset_value_per_share = asset_value / st.session_state.shares_total
    
    # 일반법인 평가액
    normal_value = income_value * 0.6 + asset_value * 0.4
    normal_value_per_share = normal_value / st.session_state.shares_total
    
    # 부동산 과다법인 평가액
    real_estate_value = income_value * 0.4 + asset_value * 0.6
    real_estate_value_per_share = real_estate_value / st.session_state.shares_total
    
    # 순자산가치 평가액
    net_asset_value = asset_value
    net_asset_value_per_share = net_asset_value / st.session_state.shares_total
    
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
        <div class="info">평가 기준일: {st.session_state.evaluation_date}</div>
        <div class="info">회사명: {st.session_state.company_name}</div>
        
        <h2>재무 정보</h2>
        <div class="info">자본총계: {format_number(st.session_state.total_capital)}원</div>
        <div class="info">1년 전 당기순이익: {format_number(st.session_state.profit_1)}원 (가중치 3배)</div>
        <div class="info">2년 전 당기순이익: {format_number(st.session_state.profit_2)}원 (가중치 2배)</div>
        <div class="info">3년 전 당기순이익: {format_number(st.session_state.profit_3)}원 (가중치 1배)</div>
        
        <h2>주식 정보</h2>
        <div class="info">총 발행주식수: {format_number(st.session_state.shares_total)}주</div>
        <div class="info">액면금액: {format_number(st.session_state.face_value)}원</div>
        <div class="info">환원율: {st.session_state.capitalization_rate}%</div>
        
        <h2>평가 결과</h2>
        <div class="info">수익가치: {format_number(income_value)}원 (주당 {format_number(income_value_per_share)}원)</div>
        <div class="info">자산가치: {format_number(asset_value)}원 (주당 {format_number(asset_value_per_share)}원)</div>
        
        <div class="result">일반법인 평가액: {format_number(normal_value)}원 (주당 {format_number(normal_value_per_share)}원)</div>
        <div class="result">부동산 과다법인 평가액: {format_number(real_estate_value)}원 (주당 {format_number(real_estate_value_per_share)}원)</div>
        <div class="result">순자산가치 평가액: {format_number(net_asset_value)}원 (주당 {format_number(net_asset_value_per_share)}원)</div>
    </body>
    </html>
    """
    return html_content

# CSV 다운로드용 내용 생성
def create_csv_content():
    # 수익가치
    weighted_profit = (st.session_state.profit_1 * 3 + 
                      st.session_state.profit_2 * 2 + 
                      st.session_state.profit_1 * 1) / 6
    income_value = weighted_profit / (st.session_state.capitalization_rate / 100)
    income_value_per_share = income_value / st.session_state.shares_total
    
    # 자산가치
    asset_value = st.session_state.total_capital
    asset_value_per_share = asset_value / st.session_state.shares_total
    
    # 일반법인 평가액
    normal_value = income_value * 0.6 + asset_value * 0.4
    normal_value_per_share = normal_value / st.session_state.shares_total
    
    # 부동산 과다법인 평가액
    real_estate_value = income_value * 0.4 + asset_value * 0.6
    real_estate_value_per_share = real_estate_value / st.session_state.shares_total
    
    # 순자산가치 평가액
    net_asset_value = asset_value
    net_asset_value_per_share = net_asset_value / st.session_state.shares_total
    
    # CSV 데이터 생성
    data = {
        '항목': ['평가 기준일', '회사명', '자본총계', '1년 전 당기순이익', '2년 전 당기순이익', '3년 전 당기순이익',
                '총 발행주식수', '액면금액', '환원율', '수익가치', '자산가치', '일반법인 평가액',
                '부동산 과다법인 평가액', '순자산가치 평가액'],
        '값': [st.session_state.evaluation_date, st.session_state.company_name,
              st.session_state.total_capital, st.session_state.profit_1,
              st.session_state.profit_2, st.session_state.profit_3,
              st.session_state.shares_total, st.session_state.face_value,
              st.session_state.capitalization_rate, income_value,
              asset_value, normal_value, real_estate_value, net_asset_value],
        '주당 가치': ['', '', '', '', '', '', '', '', '', income_value_per_share,
                  asset_value_per_share, normal_value_per_share,
                  real_estate_value_per_share, net_asset_value_per_share]
    }
    
    # DataFrame 생성 후 CSV로 변환
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False).encode('utf-8')
    return csv

# 메인 애플리케이션
st.title("비상장주식 평가")

# 날짜 선택
col1, col2 = st.columns([3, 1])
with col2:
    evaluation_date = st.date_input(
        "평가 기준일",
        st.session_state.evaluation_date,
        format="YYYY/MM/DD"
    )
    st.session_state.evaluation_date = evaluation_date

# 파일 업로드 섹션 (expander로 숨김)
with st.expander("파일 업로드 (엑셀, PDF, 워드)"):
    uploaded_file = st.file_uploader("재무정보가 포함된 파일을 업로드하세요", 
                                    type=['xlsx', 'xls', 'pdf', 'docx', 'doc'])
    
    if uploaded_file is not None:
        file_details = {"파일명": uploaded_file.name, "파일크기": uploaded_file.size}
        st.write(file_details)
        
        # 데이터 추출 버튼
        if st.button("데이터 추출"):
            with st.spinner('파일에서 데이터를 추출 중입니다...'):
                extracted_data = extract_data_from_file(uploaded_file)
                
                # 추출된 데이터 표시
                if extracted_data:
                    extracted_items = []
                    if 'company_name' in extracted_data:
                        extracted_items.append(f"회사명: {extracted_data['company_name']}")
                    if 'total_capital' in extracted_data:
                        extracted_items.append(f"자본총계: {format_number(extracted_data['total_capital'])}원")
                    if 'profit_1' in extracted_data:
                        extracted_items.append(f"1년 전 당기순이익: {format_number(extracted_data['profit_1'])}원")
                    if 'profit_2' in extracted_data:
                        extracted_items.append(f"2년 전 당기순이익: {format_number(extracted_data['profit_2'])}원")
                    if 'profit_3' in extracted_data:
                        extracted_items.append(f"3년 전 당기순이익: {format_number(extracted_data['profit_3'])}원")
                    if 'shares_total' in extracted_data:
                        extracted_items.append(f"총 발행주식수: {format_number(extracted_data['shares_total'])}주")
                    if 'face_value' in extracted_data:
                        extracted_items.append(f"액면금액: {format_number(extracted_data['face_value'])}원")
                    
                    if extracted_items:
                        st.success("다음 데이터가 추출되었습니다:")
                        for item in extracted_items:
                            st.write(item)
                        
                        # 데이터 적용 버튼
                        if st.button("추출된 데이터 적용"):
                            apply_extracted_data(extracted_data)
                            st.success("데이터가 적용되었습니다.")
                    else:
                        st.warning("파일에서 추출 가능한 데이터를 찾지 못했습니다.")
                else:
                    st.warning("파일에서 데이터를 추출하지 못했습니다.")

# 회사 정보 입력
with st.expander("회사 정보", expanded=True):
    col1, col2 = st.columns([1, 3])
    with col1:
        st.write("회사명")
    with col2:
        company_name = st.text_input("회사명", value=st.session_state.company_name, label_visibility="collapsed")
        st.session_state.company_name = company_name
    
    col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
    with col1:
        st.write("자본총계 (원)")
    with col2:
        total_capital = st.number_input("자본총계 (원)", 
                                      value=st.session_state.total_capital,
                                      step=1000000,
                                      label_visibility="collapsed")
        st.session_state.total_capital = total_capital
    with col3:
        st.button("-", key="decrease_capital", help="자본총계 감소")
    with col4:
        st.button("+", key="increase_capital", help="자본총계 증가")
    
    # 자본총계 포맷팅 표시
    st.write(f"금액: {format_number(total_capital)}원")
    st.write("재무상태표(대차대조표)상의 자본총계 금액입니다. 평가기준일 현재의 금액을 입력하세요.")

# 당기순이익 정보 입력
with st.expander("당기순이익 (최근 3개년)", expanded=True):
    st.write("최근 3개 사업연도의 당기순이익을 입력하세요. 각 연도별로 가중치가 다르게 적용됩니다.")
    
    # 1년 전 (가중치 3배)
    col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
    with col1:
        st.write("1년 전 (가중치 3배)")
    with col2:
        profit_1 = st.number_input("1년 전 당기순이익", 
                                  value=st.session_state.profit_1,
                                  step=1000000,
                                  label_visibility="collapsed")
        st.session_state.profit_1 = profit_1
    with col3:
        st.button("-", key="decrease_profit_1")
    with col4:
        st.button("+", key="increase_profit_1")
    
    st.write(f"금액: {format_number(profit_1)}원")
    
    # 2년 전 (가중치 2배)
    col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
    with col1:
        st.write("2년 전 (가중치 2배)")
    with col2:
        profit_2 = st.number_input("2년 전 당기순이익", 
                                  value=st.session_state.profit_2,
                                  step=1000000,
                                  label_visibility="collapsed")
        st.session_state.profit_2 = profit_2
    with col3:
        st.button("-", key="decrease_profit_2")
    with col4:
        st.button("+", key="increase_profit_2")
    
    st.write(f"금액: {format_number(profit_2)}원")
    
    # 3년 전 (가중치 1배)
    col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
    with col1:
        st.write("3년 전 (가중치 1배)")
    with col2:
        profit_3 = st.number_input("3년 전 당기순이익", 
                                  value=st.session_state.profit_3,
                                  step=1000000,
                                  label_visibility="collapsed")
        st.session_state.profit_3 = profit_3
    with col3:
        st.button("-", key="decrease_profit_3")
    with col4:
        st.button("+", key="increase_profit_3")
    
    st.write(f"금액: {format_number(profit_3)}원")

# 주식 정보 입력
with st.expander("주식 정보", expanded=True):
    # 총 발행주식수
    col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
    with col1:
        st.write("총 발행주식수")
    with col2:
        shares_total = st.number_input("총 발행주식수", 
                                     value=st.session_state.shares_total,
                                     step=100,
                                     label_visibility="collapsed")
        st.session_state.shares_total = shares_total
    with col3:
        st.button("-", key="decrease_shares")
    with col4:
        st.button("+", key="increase_shares")
    
    st.write(f"총 {format_number(shares_total)}주")
    
    # 액면금액
    col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
    with col1:
        st.write("액면금액 (원)")
    with col2:
        face_value = st.number_input("액면금액 (원)", 
                                   value=st.session_state.face_value,
                                   step=500,
                                   label_visibility="collapsed")
        st.session_state.face_value = face_value
    with col3:
        st.button("-", key="decrease_face_value")
    with col4:
        st.button("+", key="increase_face_value")
    
    st.write(f"금액: {format_number(face_value)}원")
    
    # 환원율 (10%로 고정)
    col1, col2 = st.columns([1, 3])
    with col1:
        st.write("환원율 (%)")
    with col2:
        # 고정된 환원율 표시
        st.slider("환원율 (%)", min_value=1, max_value=20, value=int(st.session_state.capitalization_rate), 
                step=1, disabled=True, label_visibility="collapsed")
    
    st.write("수익가치 평가 시 사용되는 환원율입니다. 일반적으로 10%를 적용합니다.")

# 주주 정보 입력
with st.expander("주주 정보", expanded=True):
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.write("입력할 주주 수")
    with col2:
        shareholder_count = st.selectbox("입력할 주주 수", 
                                       options=list(range(1, 11)),
                                       index=st.session_state.shareholder_count-1,
                                       label_visibility="collapsed")
        st.session_state.shareholder_count = shareholder_count

# 결과 계산
weighted_profit = (st.session_state.profit_1 * 3 + 
                  st.session_state.profit_2 * 2 + 
                  st.session_state.profit_3 * 1) / 6
income_value = weighted_profit / (st.session_state.capitalization_rate / 100)
income_value_per_share = income_value / st.session_state.shares_total

asset_value = st.session_state.total_capital
asset_value_per_share = asset_value / st.session_state.shares_total

normal_value = income_value * 0.6 + asset_value * 0.4
normal_value_per_share = normal_value / st.session_state.shares_total

real_estate_value = income_value * 0.4 + asset_value * 0.6
real_estate_value_per_share = real_estate_value / st.session_state.shares_total

net_asset_value = asset_value
net_asset_value_per_share = net_asset_value / st.session_state.shares_total

# 평가 결과 표시
st.divider()
st.subheader("평가 결과")

col1, col2 = st.columns(2)
with col1:
    st.write("수익가치")
    st.write(f"{format_number(income_value)}원")
    st.write(f"주당 {format_number(income_value_per_share)}원")
with col2:
    st.write("자산가치")
    st.write(f"{format_number(asset_value)}원")
    st.write(f"주당 {format_number(asset_value_per_share)}원")

st.divider()
st.write("평가방법별 주식가치")

col1, col2, col3 = st.columns(3)
with col1:
    st.write("일반법인 (수익가치 60% + 자산가치 40%)")
    st.write(f"{format_number(normal_value)}원")
    st.write(f"주당 {format_number(normal_value_per_share)}원")
with col2:
    st.write("부동산 과다법인 (자산가치 60% + 수익가치 40%)")
    st.write(f"{format_number(real_estate_value)}원")
    st.write(f"주당 {format_number(real_estate_value_per_share)}원")
with col3:
    st.write("순자산가치만 평가 (순자산가치 100%)")
    st.write(f"{format_number(net_asset_value)}원")
    st.write(f"주당 {format_number(net_asset_value_per_share)}원")

# 다운로드 섹션 (expander로 숨김)
with st.expander("평가 결과 다운로드"):
    tab1, tab2, tab3 = st.tabs(["PDF", "HTML", "CSV"])
    
    with tab1:
        if st.button("PDF 형식으로 다운로드"):
            pdf_data = generate_pdf()
            if pdf_data:
                st.download_button(
                    label="📄 PDF 파일 다운로드",
                    data=pdf_data,
                    file_name=f"비상장주식_평가_{st.session_state.company_name}_{st.session_state.evaluation_date}.pdf",
                    mime="application/pdf"
                )
    
    with tab2:
        if st.button("HTML 형식으로 다운로드"):
            html_content = create_html_content()
            st.download_button(
                label="📄 HTML 파일 다운로드",
                data=html_content,
                file_name=f"비상장주식_평가_{st.session_state.company_name}_{st.session_state.evaluation_date}.html",
                mime="text/html"
            )
    
    with tab3:
        if st.button("CSV 형식으로 다운로드"):
            csv_content = create_csv_content()
            st.download_button(
                label="📄 CSV 파일 다운로드",
                data=csv_content,
                file_name=f"비상장주식_평가_{st.session_state.company_name}_{st.session_state.evaluation_date}.csv",
                mime="text/csv"
            )
