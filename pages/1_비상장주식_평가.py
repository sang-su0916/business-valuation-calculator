import streamlit as st
import pandas as pd
import numpy as np
import locale
from datetime import datetime
import io
import tempfile
import os
import base64
import docx2txt
import re
import openpyxl
import PyPDF2
import csv

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
    .tools-button {
        position: fixed;
        right: 20px;
        bottom: 20px;
        z-index: 1000;
        padding: 8px 16px;
        background-color: #4CAF50;
        color: white;
        border-radius: 20px;
        border: none;
        cursor: pointer;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
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

# CSV 다운로드 함수
def get_csv_download_link(filename="비상장주식_평가_데이터.csv"):
    # CSV 생성
    csv_string = io.StringIO()
    csv_writer = csv.writer(csv_string)
    
    # 헤더 추가
    csv_writer.writerow(['구분', '값'])
    
    # 기본 정보
    csv_writer.writerow(['평가 기준일', str(st.session_state.eval_date)])
    csv_writer.writerow(['회사명', st.session_state.company_name])
    csv_writer.writerow(['자본총계', f"{format_number(st.session_state.total_equity)}원"])
    
    # 당기순이익
    csv_writer.writerow(['1년 전 당기순이익 (가중치 3배)', f"{format_number(st.session_state.net_income1)}원"])
    csv_writer.writerow(['2년 전 당기순이익 (가중치 2배)', f"{format_number(st.session_state.net_income2)}원"])
    csv_writer.writerow(['3년 전 당기순이익 (가중치 1배)', f"{format_number(st.session_state.net_income3)}원"])
    
    # 주식 정보
    csv_writer.writerow(['총 발행주식수', f"{format_number(st.session_state.shares)}주"])
    csv_writer.writerow(['액면금액', f"{format_number(st.session_state.share_price)}원"])
    csv_writer.writerow(['환원율', f"{st.session_state.interest_rate}%"])
    
    # 주주 정보
    for i in range(st.session_state.shareholder_count):
        if st.session_state.shareholders[i]["name"]:
            csv_writer.writerow([
                f"주주 {i+1} - {st.session_state.shareholders[i]['name']}",
                f"{format_number(st.session_state.shareholders[i]['shares'])}주"
            ])
    
    # 평가 방식
    csv_writer.writerow(['평가 방식', st.session_state.evaluation_method])
    
    # Base64 인코딩
    b64 = base64.b64encode(csv_string.getvalue().encode()).decode()
    
    # 다운로드 링크 생성
    href = f'<a href="data:text/csv;base64,{b64}" download="{filename}" class="download-button">📥 평가 데이터 CSV 다운로드</a>'
    return href

# HTML 다운로드 함수 (PDF 대체용)
def get_html_download_link(filename="비상장주식_평가_데이터.html"):
    # HTML 문서 생성
    html_string = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>비상장주식 가치평가 - {st.session_state.company_name}</title>
        <style>
            body {{ font-family: 'Malgun Gothic', 'Nanum Gothic', sans-serif; margin: 40px; line-height: 1.6; color: #333; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .section {{ margin-bottom: 30px; }}
            .footer {{ margin-top: 50px; text-align: center; font-size: 12px; color: #777; }}
            .highlight {{ font-weight: bold; color: #3498db; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>비상장주식 가치평가 데이터</h1>
                <p>평가 기준일: {st.session_state.eval_date.strftime('%Y년 %m월 %d일')}</p>
            </div>
            
            <div class="section">
                <h2>1. 기본 정보</h2>
                <table>
                    <tr>
                        <th>회사명</th>
                        <td>{st.session_state.company_name}</td>
                    </tr>
                    <tr>
                        <th>자본총계</th>
                        <td>{format_number(st.session_state.total_equity)}원</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h2>2. 당기순이익 (최근 3개년)</h2>
                <table>
                    <tr>
                        <th>구분</th>
                        <th>금액</th>
                        <th>가중치</th>
                    </tr>
                    <tr>
                        <td>1년 전</td>
                        <td>{format_number(st.session_state.net_income1)}원</td>
                        <td>3배</td>
                    </tr>
                    <tr>
                        <td>2년 전</td>
                        <td>{format_number(st.session_state.net_income2)}원</td>
                        <td>2배</td>
                    </tr>
                    <tr>
                        <td>3년 전</td>
                        <td>{format_number(st.session_state.net_income3)}원</td>
                        <td>1배</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h2>3. 주식 정보</h2>
                <table>
                    <tr>
                        <th>총 발행주식수</th>
                        <td>{format_number(st.session_state.shares)}주</td>
                    </tr>
                    <tr>
                        <th>액면금액</th>
                        <td>{format_number(st.session_state.share_price)}원</td>
                    </tr>
                    <tr>
                        <th>환원율</th>
                        <td>{st.session_state.interest_rate}%</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h2>4. 주주 정보</h2>
                <table>
                    <tr>
                        <th>주주명</th>
                        <th>보유 주식수</th>
                    </tr>
    """
    
    # 주주 정보 추가
    total_shares = 0
    for i in range(st.session_state.shareholder_count):
        if st.session_state.shareholders[i]["name"]:
            html_string += f"""
                    <tr>
                        <td>{st.session_state.shareholders[i]["name"]}</td>
                        <td>{format_number(st.session_state.shareholders[i]["shares"])}주</td>
                    </tr>
            """
            total_shares += st.session_state.shareholders[i]["shares"]
    
    html_string += f"""
                </table>
                <p>주주들의 총 보유 주식수: {format_number(total_shares)}주 (발행주식수의 {round(total_shares/st.session_state.shares*100, 2)}%)</p>
            </div>
            
            <div class="section">
                <h2>5. 평가 방식</h2>
                <table>
                    <tr>
                        <th>선택한 평가 방식</th>
                        <td>{st.session_state.evaluation_method}</td>
                    </tr>
                </table>
    """
    
    # 평가 방식 설명 추가
    method_explanation = ""
    if st.session_state.evaluation_method == "일반법인":
        method_explanation = "일반법인: 대부분의 법인에 적용 (수익가치 60% + 자산가치 40%)"
    elif st.session_state.evaluation_method == "부동산 과다법인":
        method_explanation = "부동산 과다법인: 부동산이 자산의 50% 이상인 법인 (자산가치 60% + 수익가치 40%)"
    else:
        method_explanation = "순자산가치만 평가: 특수한 경우 (설립 1년 미만 등) (순자산가치 100%)"
    
    html_string += f"""
                <p>{method_explanation}</p>
            </div>
            
            <div class="footer">
                <p>본 문서는 상속세 및 증여세법 시행령 제54조에 근거한 비상장주식 평가를 위한 기초자료입니다.</p>
                <p>© {datetime.now().year} 비상장주식 가치평가 시스템</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Base64 인코딩
    b64 = base64.b64encode(html_string.encode()).decode()
    
    # 다운로드 링크 생성
    href = f'<a href="data:text/html;base64,{b64}" download="{filename}" class="download-button">📄 평가 데이터 HTML 다운로드</a>'
    return href

# 도구 표시 토글 함수
def toggle_tools():
    st.session_state.show_tools = not st.session_state.show_tools

# 페이지 헤더
st.title("비상장주식 가치평가")

# 도구 토글 버튼 (고정 위치)
st.markdown(
    f"""
    <button 
        onclick="document.getElementById('tools').{'scrollIntoView({{behavior:\"smooth\"}}); document.querySelector(\".streamlit-expanderHeader\").click()' if not st.session_state.show_tools else ''}"
        class="tools-button"
    >
        {'🔍 고급 도구' if not st.session_state.show_tools else '🔍 고급 도구'}
    </button>
    """,
    unsafe_allow_html=True
)

# 고급 도구 섹션
tools_expander = st.expander("🔍 고급 도구 (데이터 업로드/다운로드)", expanded=st.session_state.show_tools)

with tools_expander:
    st.markdown('<div id="tools"></div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["📂 파일 업로드", "📥 데이터 다운로드"])
    
    with tabs[0]:
        st.markdown("### 파일에서 데이터 불러오기")
        st.markdown("엑셀, PDF, 워드 파일에서 데이터를 자동으로 추출합니다.")
        
        uploaded_file = st.file_uploader(
            "파일 선택",
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
                        extracted_items.append(f"액면금액: {format_number(extracted_data['share
