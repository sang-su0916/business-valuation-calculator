import streamlit as st
import pandas as pd
import numpy as np
import locale
from datetime import datetime
import io
import tempfile
import os
import base64
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import docx2txt
import PyPDF2
import re
import openpyxl

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
    .file-uploader-section {
        border: 1px dashed #ccc;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin-bottom: 15px;
    }
    .hidden-section {
        display: none;
    }
    .stDownloadButton button {
        width: 100%;
    }
    .download-button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 15px;
        border-radius: 5px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 10px 0;
        cursor: pointer;
        border: none;
        width: 100%;
    }
    .tool-icon {
        margin-right: 5px;
    }
    .custom-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #f0f2f6;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 5px 10px;
        margin-right: 10px;
        cursor: pointer;
        font-size: 14px;
        transition: background-color 0.3s;
    }
    .custom-button:hover {
        background-color: #e1e4e8;
    }
    .custom-button.active {
        background-color: #cce5ff;
        border-color: #99caff;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'eval_date' not in st.session_state:
    st.session_state.eval_date = datetime.now().date()
if 'company_name' not in st.session_state:
    st.session_state.company_name = "주식회사 에이비씨"
if 'total_equity' not in st.session_state:
    st.session_state.total_equity = 1000000000
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
    st.session_state.interest_rate = 10  # 환원율 10%로 고정
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
if 'show_tools' not in st.session_state:
    st.session_state.show_tools = False

# 숫자 형식화 함수
def format_number(num):
    try:
        return "{:,}".format(int(num))
    except:
        return str(num)

# 숫자 추출 함수
def extract_number(text):
    if text is None:
        return None
    
    # 숫자와 쉼표, 점만 남기고 모두 제거
    text = re.sub(r'[^0-9,.]', '', str(text))
    
    # 쉼표 제거
    text = text.replace(',', '')
    
    # 숫자로 변환 시도
    try:
        return float(text)
    except:
        return None

# 파일에서 데이터 추출 함수
def extract_data_from_file(file):
    extracted_data = {}
    
    # 파일 확장자 가져오기
    file_extension = file.name.split('.')[-1].lower()
    
    if file_extension in ['xlsx', 'xls']:
        # 엑셀 파일 처리
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
            tmp_file.write(file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            workbook = openpyxl.load_workbook(tmp_file_path, data_only=True)
            sheet = workbook.active
            
            # 엑셀 데이터를 텍스트로 변환
            text_content = []
            for row in sheet.iter_rows():
                row_data = []
                for cell in row:
                    if cell.value is not None:
                        row_data.append(str(cell.value))
                if row_data:
                    text_content.append(' '.join(row_data))
            
            text_content = '\n'.join(text_content)
            
            # 데이터 추출
            extracted_data = extract_data_from_text(text_content)
            
            os.unlink(tmp_file_path)
            
        except Exception as e:
            st.error(f"엑셀 파일 처리 중 오류 발생: {e}")
    
    elif file_extension == 'pdf':
        # PDF 파일 처리
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            text_content = ""
            with open(tmp_file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page_num in range(len(pdf_reader.pages)):
                    text_content += pdf_reader.pages[page_num].extract_text()
            
            # 데이터 추출
            extracted_data = extract_data_from_text(text_content)
            
            os.unlink(tmp_file_path)
            
        except Exception as e:
            st.error(f"PDF 파일 처리 중 오류 발생: {e}")
    
    elif file_extension in ['doc', 'docx']:
        # 워드 파일 처리
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
            tmp_file.write(file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            text_content = docx2txt.process(tmp_file_path)
            
            # 데이터 추출
            extracted_data = extract_data_from_text(text_content)
            
            os.unlink(tmp_file_path)
            
        except Exception as e:
            st.error(f"워드 파일 처리 중 오류 발생: {e}")
    
    return extracted_data

# 텍스트에서 데이터 추출
def extract_data_from_text(text):
    data = {}
    
    # 자본금 검색
    capital_patterns = [
        r'자본금.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        r'자본.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        r'capital.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
    ]
    
    # 자산 검색
    asset_patterns = [
        r'자산.*?총계.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        r'총자산.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        r'자산.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        r'assets.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
    ]
    
    # 부채 검색
    debt_patterns = [
        r'부채.*?총계.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        r'총부채.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        r'부채.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        r'liabilities.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
    ]
    
    # 자본총계(순자산) 검색
    equity_patterns = [
        r'자본.*?총계.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        r'순자산.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        r'equity.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
    ]
    
    # 당기순이익 검색
    income_patterns = [
        r'당기순이익.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        r'순이익.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        r'net income.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
    ]
    
    # 발행주식수 검색
    shares_patterns = [
        r'발행.*?주식.*?수.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        r'총.*?주식.*?수.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        r'주식.*?수.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        r'shares.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
    ]
    
    # 액면가 검색
    share_price_patterns = [
        r'액면.*?가액.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        r'액면가.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        r'par value.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
    ]
    
    # 회사명 검색
    company_patterns = [
        r'회사명[:\s]*([^\n\r]*)',
        r'상호[:\s]*([^\n\r]*)',
        r'company name[:\s]*([^\n\r]*)'
    ]
    
    # 회사명 추출
    for pattern in company_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['company_name'] = match.group(1).strip()
            break
    
    # 자본금 추출
    for pattern in capital_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['capital'] = extract_number(match.group(1))
            break
    
    # 자산 추출
    for pattern in asset_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['assets'] = extract_number(match.group(1))
            break
    
    # 부채 추출
    for pattern in debt_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['debt'] = extract_number(match.group(1))
            break
    
    # 자본총계(순자산) 추출
    for pattern in equity_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['total_equity'] = extract_number(match.group(1))
            break
    
    # 당기순이익 추출 (최근 3개년 - 여러 개 검색)
    income_matches = []
    for pattern in income_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            value = extract_number(match.group(1))
            if value is not None:
                income_matches.append(value)
    
    # 최대 3개의 당기순이익 저장
    if len(income_matches) >= 1:
        data['net_income1'] = income_matches[0]
    if len(income_matches) >= 2:
        data['net_income2'] = income_matches[1]
    if len(income_matches) >= 3:
        data['net_income3'] = income_matches[2]
    
    # 발행주식수 추출
    for pattern in shares_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['shares'] = extract_number(match.group(1))
            break
    
    # 액면가 추출
    for pattern in share_price_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['share_price'] = extract_number(match.group(1))
            break
    
    return data

# PDF 생성 함수
def create_input_data_pdf():
    buffer = io.BytesIO()
    
    # PDF 문서 생성
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # 스타일 설정
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Korean', fontName='Helvetica', fontSize=12))
    
    # 컨텐츠 추가
    content = []
    
    # 제목
    title_style = styles['Heading1']
    content.append(Paragraph("비상장주식 가치평가 입력 데이터", title_style))
    content.append(Spacer(1, 20))
    
    # 기본 정보
    content.append(Paragraph("1. 기본 정보", styles['Heading2']))
    content.append(Spacer(1, 10))
    
    # 회사 정보 테이블
    company_data = [
        ["평가 기준일", str(st.session_state.eval_date)],
        ["회사명", st.session_state.company_name],
        ["자본총계", f"{format_number(st.session_state.total_equity)}원"]
    ]
    
    company_table = Table(company_data, colWidths=[150, 300])
    company_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    content.append(company_table)
    content.append(Spacer(1, 20))
    
    # 당기순이익 정보
    content.append(Paragraph("2. 당기순이익 (최근 3개년)", styles['Heading2']))
    content.append(Spacer(1, 10))
    
    income_data = [
        ["구분", "금액", "가중치"],
        ["1년 전", f"{format_number(st.session_state.net_income1)}원", "3배"],
        ["2년 전", f"{format_number(st.session_state.net_income2)}원", "2배"],
        ["3년 전", f"{format_number(st.session_state.net_income3)}원", "1배"]
    ]
    
    income_table = Table(income_data, colWidths=[150, 200, 100])
    income_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    content.append(income_table)
    content.append(Spacer(1, 20))
    
    # 주식 정보
    content.append(Paragraph("3. 주식 정보", styles['Heading2']))
    content.append(Spacer(1, 10))
    
    shares_data = [
        ["총 발행주식수", f"{format_number(st.session_state.shares)}주"],
        ["액면금액", f"{format_number(st.session_state.share_price)}원"],
        ["환원율", f"{st.session_state.interest_rate}%"]
    ]
    
    shares_table = Table(shares_data, colWidths=[150, 300])
    shares_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    content.append(shares_table)
    content.append(Spacer(1, 20))
    
    # 주주 정보
    content.append(Paragraph("4. 주주 정보", styles['Heading2']))
    content.append(Spacer(1, 10))
    
    shareholder_data = [["주주명", "보유 주식수"]]
    
    total_shares = 0
    for i in range(st.session_state.shareholder_count):
        if st.session_state.shareholders[i]["name"]:
            shareholder_data.append([
                st.session_state.shareholders[i]["name"],
                f"{format_number(st.session_state.shareholders[i]['shares'])}주"
            ])
            total_shares += st.session_state.shareholders[i]["shares"]
    
    shareholder_table = Table(shareholder_data, colWidths=[225, 225])
    shareholder_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    content.append(shareholder_table)
    content.append(Spacer(1, 10))
    content.append(Paragraph(f"주주들의 총 보유 주식수: {format_number(total_shares)}주 (발행주식수의 {round(total_shares/st.session_state.shares*100, 2)}%)", styles['Normal']))
    content.append(Spacer(1, 20))
    
    # 평가 방식
    content.append(Paragraph("5. 평가 방식", styles['Heading2']))
    content.append(Spacer(1, 10))
    
    method_data = [["선택한 평가 방식", st.session_state.evaluation_method]]
    
    method_table = Table(method_data, colWidths=[150, 300])
    method_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    content.append(method_table)
    content.append(Spacer(1, 10))
    
    # 평가 방식 설명
    method_explanation = ""
    if st.session_state.evaluation_method == "일반법인":
        method_explanation = "일반법인: 대부분의 법인에 적용 (수익가치 60% + 자산가치 40%)"
    elif st.session_state.evaluation_method == "부동산 과다법인":
        method_explanation = "부동산 과다법인: 부동산이 자산의 50% 이상인 법인 (자산가치 60% + 수익가치 40%)"
    else:
        method_explanation = "순자산가치만 평가: 특수한 경우 (설립 1년 미만 등) (순자산가치 100%)"
    
    content.append(Paragraph(method_explanation, styles['Normal']))
    
    # PDF 생성
    doc.build(content)
    buffer.seek(0)
    
    return buffer

# 파일 다운로드를 위한 함수
def get_binary_file_downloader_html(bin_data, file_label='File', file_name='file.pdf'):
    b64 = base64.b64encode(bin_data.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}" class="download-button">📥 {file_label} 다운로드</a>'
    return href

# 도구 토글 버튼
tools_expander = st.expander("고급 도구 (데이터 업로드/다운로드)", expanded=st.session_state.show_tools)

with tools_expander:
    st.markdown("### 파일에서 데이터 불러오기")
    
    uploaded_file = st.file_uploader(
        "엑셀, PDF, 워드 파일에서 데이터를 자동으로 추출합니다",
        type=["xlsx", "xls", "pdf", "doc", "docx"],
        help="지원 파일: 엑셀(.xlsx, .xls), PDF(.pdf), 워드(.doc, .docx)"
    )
    
    if uploaded_file is not None:
        with st.spinner("파일에서 데이터를 추출 중입니다..."):
            extracted_data = extract_data_from_file(uploaded_file)
            
            if extracted_data:
                st.success("파일에서 다음 데이터를 추출했습니다.")
                
                # 추출된 데이터 표시
                extracted_items = []
                
                if 'company_name' in extracted_data:
                    extracted_items.append(f"회사명: {extracted_data['company_name']}")
                
                if 'total_equity' in extracted_data:
                    extracted_items.append(f"자본총계: {format_number(extracted_data['total_equity'])}원")
                
                if 'net_income1' in extracted_data:
                    extracted_items.append(f"1년 전 당기순이익: {format_number(extracted_data['net_income1'])}원")
                
                if 'net_income2' in extracted_data:
                    extracted_items.append(f"2년 전 당기순이익: {format_number(extracted_data['net_income2'])}원")
                
                if 'net_income3' in extracted_data:
                    extracted_items.append(f"3년 전 당기순이익: {format_number(extracted_data['net_income3'])}원")
                
                if 'shares' in extracted_data:
                    extracted_items.append(f"총 발행주식수: {format_number(extracted_data['shares'])}주")
                
                if 'share_price' in extracted_data:
                    extracted_items.append(f"액면금액: {format_number(extracted_data['share_price'])}원")
                
                # 추출된 데이터 표시
                if extracted_items:
                    for item in extracted_items:
                        st.write(f"✓ {item}")
                
                    # 데이터 적용 버튼
                    if st.button("추출된 데이터 적용하기"):
                        # 추출된 데이터를 세션 상태에 적용
                        if 'company_name' in extracted_data:
                            st.session_state.company_name = extracted_data['company_name']
                        
                        if 'total_equity' in extracted_data:
                            st.session_state.total_equity = extracted_data['total_equity']
                        
                        if 'net_income1' in extracted_data:
                            st.session_state.net_income1 = extracted_data['net_income1']
