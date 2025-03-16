import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import locale

# 숫자 형식화를 위한 로케일 설정
try:
    locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'ko_KR')
    except:
        locale.setlocale(locale.LC_ALL, '')

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

# 페이지 헤더
st.title("주식가치 평가 결과")

# CSS 스타일 추가
st.markdown("""
<style>
    .info-box {
        background-color: #f0f7fb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0 20px 0;
        color: #0c5460;
    }
    .button-description {
        font-size: 0.9em;
        color: #555;
        margin: 5px 0 20px 0;
        padding: 8px;
        background-color: #f8f9fa;
        border-radius: 4px;
    }
    .sidebar-guide {
        background-color: #e8f4f8;
        padding: 10px 15px;
        border-radius: 5px;
        margin-top: 10px;
        font-size: 0.9em;
        border-left: 3px solid #4dabf7;
    }
    .chart-container {
        margin-bottom: 20px;
    }
    .next-steps-header {
        margin-top: 25px;
        margin-bottom: 15px;
        color: #333;
    }
    .footer-note {
        margin-top: 30px;
        font-size: 0.85em;
        color: #666;
        border-top: 1px solid #eee;
        padding-top: 10px;
    }
    .download-section {
        background-color: #f0f7fb;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 결과 확인
if not st.session_state.get('evaluated', False):
    st.warning("먼저 '비상장주식 평가' 페이지에서 평가를 진행해주세요.")
    st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>비상장주식 평가</b> 메뉴를 클릭하여 이동하세요.</div>", unsafe_allow_html=True)
else:
    stock_value = st.session_state.stock_value
    company_name = st.session_state.company_name
    total_equity = st.session_state.total_equity
    eval_date = st.session_state.get('eval_date', None)
    
    # 평가일자 정보 추가
    date_info = f" ({eval_date.strftime('%Y년 %m월 %d일')} 기준)" if eval_date else ""
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 회사명: {company_name}")
    with col2:
        st.markdown(f"### 적용 평가방식: {stock_value['methodText']}")
    
    # 평가 기준일 표시 (있는 경우)
    if eval_date:
        st.markdown(f"<div class='info-box'>평가 기준일: {eval_date.strftime('%Y년 %m월 %d일')}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("주요 계산결과")
    
    # 결과 표 생성
    results_df = pd.DataFrame({
        "항목": [
            "1주당 순자산가치", 
            "1주당 손익가치", 
            "영업권 고려 후 자산가치", 
            "최종 주당 평가액", 
            "회사 총 주식가치", 
            "대표이사 보유주식 가치"
        ],
        "금액 (원)": [
            format_number(stock_value["netAssetPerShare"]),
            format_number(stock_value["incomeValue"]),
            format_number(stock_value["assetValueWithGoodwill"]),
            format_number(stock_value["finalValue"]),
            format_number(stock_value["totalValue"]),
            format_number(stock_value["ownedValue"])
        ]
    })
    
    # 스타일링된 데이터프레임 표시
    st.dataframe(
        results_df,
        column_config={
            "항목": st.column_config.TextColumn("항목"),
            "금액 (원)": st.column_config.TextColumn("금액 (원)", width="large"),
        },
        hide_index=True,
        use_container_width=True,
        height=280
    )
    
    # 증가율 정보 표시
    st.info(f"자본총계({format_number(total_equity)}원) 대비 평가 회사가치는 **{stock_value['increasePercentage']}%**로 평가되었습니다.")
    
    # 차트 표시
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        # 원형 차트 생성
        labels = ['순자산가치', '영업권 가치']
        values = [stock_value["netAssetPerShare"], stock_value["assetValueWithGoodwill"] - stock_value["netAssetPerShare"]]
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
        fig.update_layout(title_text='주당 가치 구성')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 막대 차트 생성
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['순자산가치', '손익가치', '최종평가액'],
            y=[stock_value["netAssetPerShare"], stock_value["incomeValue"], stock_value["finalValue"]],
            marker_color=['lightblue', 'lightgreen', 'coral']
        ))
        fig.update_layout(title_text='주요 가치 비교 (주당)')
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 다운로드 섹션 추가
    with st.expander("📥 평가 결과 다운로드", expanded=False):
        st.markdown("<div class='download-section'>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["PDF", "HTML", "CSV"])
        
        with tab1:
            if st.button("PDF 생성하기", key="generate_pdf", type="primary"):
                try:
                    # 바로 처리 시도
                    import subprocess
                    subprocess.check_call(['pip', 'install', 'fpdf2'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    from fpdf import FPDF
                    
                    with st.spinner("PDF 생성 중..."):
                        # 간단한 PDF 생성
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font('Helvetica', 'B', 16)
                        pdf.cell(0, 10, 'Stock Valuation Report', 0, 1, 'C')
                        
                        pdf.ln(10)
                        pdf.set_font('Helvetica', '', 12)
                        pdf.cell(0, 10, f'Company: {company_name}', 0, 1)
                        pdf.cell(0, 10, f'Date: {eval_date}', 0, 1)
                        pdf.cell(0, 10, f'Valuation Method: {stock_value["methodText"]}', 0, 1)
                        pdf.ln(5)
                        
                        # 결과 데이터 추가
                        pdf.set_font('Helvetica', 'B', 14)
                        pdf.cell(0, 10, 'Valuation Results', 0, 1)
                        pdf.set_font('Helvetica', '', 12)
                        
                        pdf.cell(0, 10, f'Net Asset Value per Share: {format_number(stock_value["netAssetPerShare"])} KRW', 0, 1)
                        pdf.cell(0, 10, f'Income Value per Share: {format_number(stock_value["incomeValue"])} KRW', 0, 1)
                        pdf.cell(0, 10, f'Asset Value with Goodwill: {format_number(stock_value["assetValueWithGoodwill"])} KRW', 0, 1)
                        pdf.cell(0, 10, f'Final Value per Share: {format_number(stock_value["finalValue"])} KRW', 0, 1)
                        pdf.cell(0, 10, f'Total Company Value: {format_number(stock_value["totalValue"])} KRW', 0, 1)
                        
                        if 'increasePercentage' in stock_value:
                            pdf.ln(5)
                            pdf.cell(0, 10, f'Value Increase Percentage: {stock_value["increasePercentage"]}%', 0, 1)
                        
                        # PDF 데이터 얻기
                        pdf_data = pdf.output()
                        
                        # 다운로드 버튼 표시
                        st.success("PDF 생성 완료!")
                        st.download_button(
                            label="📄 PDF 파일 다운로드",
                            data=pdf_data,
                            file_name=f"주식가치_평가결과_{company_name}_{eval_date}.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error("PDF 생성에 실패했습니다.")
                    st.info("HTML 혹은 CSV 형식으로 다운로드해 보세요.")
                    st.code("pip install fpdf2", language="bash")
        
        with tab2:
            if st.button("HTML 파일 생성하기", key="generate_html"):
                # HTML 내용 생성
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>주식가치 평가 결과 - {company_name}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        h1 {{ color: #2c3e50; text-align: center; }}
                        h2 {{ color: #3498db; margin-top: 20px; }}
                        .info {{ margin-bottom: 5px; }}
                        .result {{ margin-top: 10px; font-weight: bold; }}
                        .results-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                        .results-table th, .results-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        .results-table th {{ background-color: #f2f2f2; }}
                    </style>
                </head>
                <body>
                    <h1>주식가치 평가 결과</h1>
                    
                    <h2>평가 정보</h2>
                    <div class="info">회사명: {company_name}</div>
                    <div class="info">평가 기준일: {eval_date}</div>
                    <div class="info">적용 평가방식: {stock_value["methodText"]}</div>
                    
                    <h2>주요 계산결과</h2>
                    <table class="results-table">
                        <tr>
                            <th>항목</th>
                            <th>금액 (원)</th>
                        </tr>
                        <tr>
                            <td>1주당 순자산가치</td>
                            <td>{format_number(stock_value["netAssetPerShare"])}</td>
                        </tr>
                        <tr>
                            <td>1주당 손익가치</td>
                            <td>{format_number(stock_value["incomeValue"])}</td>
                        </tr>
                        <tr>
                            <td>영업권 고려 후 자산가치</td>
                            <td>{format_number(stock_value["assetValueWithGoodwill"])}</td>
                        </tr>
                        <tr>
                            <td>최종 주당 평가액</td>
                            <td>{format_number(stock_value["finalValue"])}</td>
                        </tr>
                        <tr>
                            <td>회사 총 주식가치</td>
                            <td>{format_number(stock_value["totalValue"])}</td>
                        </tr>
                        <tr>
                            <td>대표이사 보유주식 가치</td>
                            <td>{format_number(stock_value["ownedValue"])}</td>
                        </tr>
                    </table>
                    
                    <div class="result">자본총계({format_number(total_equity)}원) 대비 평가 회사가치는 <b>{stock_value["increasePercentage"]}%</b>로 평가되었습니다.</div>
                    
                    <p>※ 평가 결과는 참고용으로만 사용하시고, 정확한 세금 계산을 위해서는 전문가와 상담하시기 바랍니다.</p>
                </body>
                </html>
                """
                
                st.download_button(
                    label="📄 HTML 파일 다운로드",
                    data=html_content,
                    file_name=f"주식가치_평가결과_{company_name}_{eval_date}.html",
                    mime="text/html"
                )
        
        with tab3:
            if st.button("CSV 파일 생성하기", key="generate_csv"):
                # CSV 데이터 생성
                data = {
                    '항목': [
                        '회사명', '평가 기준일', '적용 평가방식',
                        '1주당 순자산가치', '1주당 손익가치', '영업권 고려 후 자산가치',
                        '최종 주당 평가액', '회사 총 주식가치', '대표이사 보유주식 가치',
                        '자본총계 대비 증가율'
                    ],
                    '값': [
                        company_name, str(eval_date), stock_value['methodText'],
                        stock_value["netAssetPerShare"], stock_value["incomeValue"], stock_value["assetValueWithGoodwill"],
                        stock_value["finalValue"], stock_value["totalValue"], stock_value["ownedValue"],
                        f"{stock_value['increasePercentage']}%"
                    ]
                }
                
                # DataFrame 생성 후 CSV로 변환
                df = pd.DataFrame(data)
                csv = df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="📄 CSV 파일 다운로드",
                    data=csv,
                    file_name=f"주식가치_평가결과_{company_name}_{eval_date}.csv",
                    mime="text/csv"
                )
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 다음 단계 안내
    st.markdown("<h3 class='next-steps-header'>📌 다음 단계 안내</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div class='info-box'>
    평가된 주식가치 결과를 바탕으로 다음 단계를 진행할 수 있습니다:
    <ul>
        <li><b>현시점 세금 계산하기</b>: 상속세, 증여세, 양도소득세 등을 계산합니다.</li>
        <li><b>미래 주식가치 계산하기</b>: 성장률을 적용하여 미래 주식가치를 예측합니다.</li>
    </ul>
    아래 버튼을 클릭하거나 왼쪽 사이드바에서 메뉴를 선택하여 진행하세요.
    </div>
    """, unsafe_allow_html=True)
    
    # 버튼 행
    col1, col2 = st.columns(2)
    with col1:
        if st.button("현시점 세금 계산하기", type="primary", use_container_width=True):
            # 버튼 클릭 시 페이지 전환을 시도하지만 실패할 경우를 대비해 안내 메시지 추가
            st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>현시점 세금계산</b> 메뉴를 클릭하여 이동하세요.</div>", unsafe_allow_html=True)
            try:
                st.switch_page("3_현시점_세금계산.py")
            except:
                pass  # 오류 메시지 표시하지 않음
        st.markdown("<div class='button-description'>상속세, 증여세, 양도소득세 등 현시점 기준 세금을 계산합니다.</div>", unsafe_allow_html=True)
    
    with col2:
        if st.button("미래 주식가치 계산하기", type="primary", use_container_width=True):
            # 사이드바 이동 안내 메시지
            st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>미래 주식가치</b> 메뉴를 클릭하여 이동하세요.</div>", unsafe_allow_html=True)
            try:
                st.switch_page("4_미래_주식가치.py")
            except:
                pass  # 오류 메시지 표시하지 않음
        st.markdown("<div class='button-description'>회사의 성장을 고려하여 미래 시점의 주식가치를 예측합니다.</div>", unsafe_allow_html=True)
    
    # 추가 안내
    st.markdown("""
    <div class='footer-note'>
    * 평가 결과는 참고용으로만 사용하시고, 정확한 세금 계산을 위해서는 전문가와 상담하시기 바랍니다.
    </div>
    """, unsafe_allow_html=True)
