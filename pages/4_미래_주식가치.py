import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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

# 숫자 형식화 함수
def format_number(num):
    try:
        return "{:,}".format(int(num))
    except:
        return str(num)

# CSS 스타일 추가
st.markdown("""
<style>
    .info-box {
        background-color: #f0f7fb;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
        color: #0c5460;
    }
    .growth-panel {
        background-color: #fff8e1;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
        border-left: 4px solid #ffc107;
    }
    .sidebar-guide {
        background-color: #e8f4f8;
        padding: 10px 15px;
        border-radius: 5px;
        margin-top: 10px;
        font-size: 0.9em;
        border-left: 3px solid #4dabf7;
    }
    .result-highlight {
        font-size: 24px;
        font-weight: bold;
        color: #333;
        margin: 10px 0;
    }
    .percentage-up {
        color: #28a745;
        font-weight: bold;
    }
    .chart-container {
        margin-top: 20px;
        margin-bottom: 30px;
    }
    .explanation-text {
        font-size: 0.95em;
        color: #555;
        margin: 15px 0;
        line-height: 1.5;
    }
    .download-section {
        background-color: #f0f7fb;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
    }
    .warning-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    .info-box-light {
        background-color: #e2f0fb;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# PDF 생성 함수
def generate_pdf(current_value, future_value, company_name, growth_rate, future_years):
    try:
        # FPDF 라이브러리 자동 설치 시도
        try:
            from fpdf import FPDF
        except ImportError:
            try:
                import subprocess
                subprocess.check_call(['pip', 'install', 'fpdf'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                from fpdf import FPDF
            except:
                return None
        
        # PDF 객체 생성
        pdf = FPDF()
        pdf.add_page()
        
        # 기본 폰트 설정 (한글 지원 제한)
        pdf.set_font('Arial', 'B', 16)
        
        # 제목
        pdf.cell(190, 10, 'Future Stock Value Prediction Report', 0, 1, 'C')
        pdf.ln(5)
        
        # 회사 정보
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(190, 10, f'Company: {company_name}', 0, 1)
        pdf.ln(5)
        
        # 예측 정보
        pdf.set_font('Arial', '', 11)
        pdf.cell(190, 10, f'Growth Rate: {growth_rate}% per year', 0, 1)
        pdf.cell(190, 10, f'Prediction Period: {future_years} years', 0, 1)
        pdf.ln(5)
        
        # 현재 및 미래 가치
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(190, 10, 'Valuation Results:', 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.cell(190, 10, f'Current Value per Share: {format_number(current_value["finalValue"])} KRW', 0, 1)
        pdf.cell(190, 10, f'Future Value per Share: {format_number(future_value["finalValue"])} KRW', 0, 1)
        pdf.cell(190, 10, f'Current Total Company Value: {format_number(current_value["totalValue"])} KRW', 0, 1)
        pdf.cell(190, 10, f'Future Total Company Value: {format_number(future_value["totalValue"])} KRW', 0, 1)
        
        # 증가율
        value_increase = (future_value["finalValue"] / current_value["finalValue"] - 1) * 100
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(190, 10, f'Expected Value Increase: +{value_increase:.1f}% (after {future_years} years)', 0, 1)
        
        # 생성일
        pdf.ln(10)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(190, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d")}', 0, 1)
        
        # PDF를 바이트로 변환
        try:
            return pdf.output(dest='S').encode('latin-1')
        except Exception as e:
            return None
    except Exception as e:
        return None

# HTML 다운로드용 내용 생성
def create_html_content(current_value, future_value, company_name, growth_rate, future_years):
    target_year = datetime.now().year + future_years
    value_increase = (future_value["finalValue"] / current_value["finalValue"] - 1) * 100
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>미래 주식가치 예측 보고서 - {company_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            h2 {{ color: #3498db; margin-top: 20px; }}
            .info {{ margin-bottom: 5px; }}
            .value-box {{ background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; }}
            .current {{ border-left: 4px solid #3498db; }}
            .future {{ border-left: 4px solid #e67e22; }}
            .result {{ margin-top: 10px; font-weight: bold; }}
            .increase {{ color: #27ae60; font-weight: bold; font-size: 1.2em; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            table, th, td {{ border: 1px solid #ddd; }}
            th, td {{ padding: 12px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>미래 주식가치 예측 보고서</h1>
        
        <h2>회사 정보</h2>
        <div class="info">회사명: {company_name}</div>
        
        <h2>예측 정보</h2>
        <div class="info">적용 성장률: 연 {growth_rate}% (복리)</div>
        <div class="info">예측 기간: {future_years}년 (기준: {datetime.now().year}년 → 예측: {target_year}년)</div>
        
        <div class="value-box current">
            <h3>현재 가치</h3>
            <div class="info">주당 가치: {format_number(current_value["finalValue"])}원</div>
            <div class="info">회사 총가치: {format_number(current_value["totalValue"])}원</div>
        </div>
        
        <div class="value-box future">
            <h3>미래 가치</h3>
            <div class="info">주당 가치: {format_number(future_value["finalValue"])}원</div>
            <div class="info">회사 총가치: {format_number(future_value["totalValue"])}원</div>
        </div>
        
        <div style="text-align: center; margin: 20px 0;">
            <p>예상 가치 증가율: <span class="increase">+{value_increase:.1f}%</span> ({future_years}년 후)</p>
        </div>
        
        <h2>세부 계산 내역</h2>
        <table>
            <tr>
                <th>항목</th>
                <th>금액 (원)</th>
            </tr>
            <tr>
                <td>미래 자본총계</td>
                <td>{format_number(future_value["futureTotalEquity"])}</td>
            </tr>
            <tr>
                <td>1주당 순자산가치</td>
                <td>{format_number(future_value["netAssetPerShare"])}</td>
            </tr>
            <tr>
                <td>1주당 손익가치</td>
                <td>{format_number(future_value["incomeValue"])}</td>
            </tr>
            <tr>
                <td>미래 주당 평가액</td>
                <td>{format_number(future_value["finalValue"])}</td>
            </tr>
            <tr>
                <td>미래 회사 총 주식가치</td>
                <td>{format_number(future_value["totalValue"])}</td>
            </tr>
        </table>
        
        <div style="margin-top: 30px; padding: 10px; background-color: #edf7ed; border-radius: 5px;">
            <p><b>참고:</b> 이 예측은 선택한 성장률이 일정하게 유지된다는 가정 하에 계산됩니다. 실제 기업의 성장은 다양한 요인에 따라 변동될 수 있습니다.</p>
        </div>
        
        <div style="margin-top: 30px; text-align: center; color: #777; font-size: 0.9em;">
            <p>생성일: {datetime.now().strftime('%Y년 %m월 %d일')}</p>
        </div>
    </body>
    </html>
    """
    return html_content

# CSV 다운로드용 내용 생성
def create_csv_content(current_value, future_value, company_name, growth_rate, future_years):
    # 현재 년도 계산
    current_year = datetime.now().year
    target_year = current_year + future_years
    
    # 가치 증가율 계산
    value_increase = (future_value["finalValue"] / current_value["finalValue"] - 1) * 100
    
    # CSV 데이터 생성
    data = {
        '항목': [
            '회사명', '성장률', '예측기간', 
            '예측 시작 연도', '예측 종료 연도',
            '현재 주당 가치', '미래 주당 가치', 
            '현재 회사 총가치', '미래 회사 총가치',
            '가치 증가율',
            '미래 자본총계', '미래 1주당 순자산가치', 
            '미래 1주당 손익가치', '미래 주당 평가액'
        ],
        '값': [
            company_name, f"{growth_rate}%", f"{future_years}년",
            str(current_year), str(target_year),
            current_value["finalValue"], future_value["finalValue"],
            current_value["totalValue"], future_value["totalValue"],
            f"{value_increase:.1f}%",
            future_value["futureTotalEquity"], future_value["netAssetPerShare"],
            future_value["incomeValue"], future_value["finalValue"]
        ]
    }
    
    # DataFrame 생성 후 CSV로 변환
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False).encode('utf-8')
    return csv

# 미래 주식가치 계산 함수
def calculate_future_stock_value(stock_value, total_equity, shares, owned_shares, 
                               interest_rate, evaluation_method, growth_rate, future_years):
    if not stock_value:
        return None
    
    # 복리 성장률 적용
    growth_factor = (1 + (growth_rate / 100)) ** future_years
    
    # 미래 자산 및 수익 계산
    future_total_equity = total_equity * growth_factor
    future_weighted_income = stock_value["weightedIncome"] * growth_factor
    
    # 1. 순자산가치 계산
    net_asset_per_share = future_total_equity / shares
    
    # 2. 영업권 계산
    weighted_income_per_share = future_weighted_income / shares
    weighted_income_per_share_50 = weighted_income_per_share * 0.5
    equity_return = (future_total_equity * (interest_rate / 100)) / shares
    annuity_factor = 3.7908
    goodwill = max(0, (weighted_income_per_share_50 - equity_return) * annuity_factor)
    
    # 3. 순자산가치 + 영업권
    asset_value_with_goodwill = net_asset_per_share + goodwill
    
    # 4. 손익가치 계산
    income_value = weighted_income_per_share * (100 / interest_rate)
    
    # 5. 최종가치 계산
    if evaluation_method == "부동산 과다법인":
        # 부동산 과다법인
        stock_value_calc = (asset_value_with_goodwill * 0.6) + (income_value * 0.4)
        net_asset_80_percent = net_asset_per_share * 0.8
        final_value = max(stock_value_calc, net_asset_80_percent)
        method_text = '부동산 과다법인: (자산가치×0.6 + 수익가치×0.4)'
    elif evaluation_method == "순자산가치만 평가":
        # 순자산가치만 적용
        final_value = net_asset_per_share
        method_text = '순자산가치만 평가'
    else:
        # 일반법인
        stock_value_calc = (income_value * 0.6) + (asset_value_with_goodwill * 0.4)
        net_asset_80_percent = net_asset_per_share * 0.8
        final_value = max(stock_value_calc, net_asset_80_percent)
        method_text = '일반법인: (수익가치×0.6 + 자산가치×0.4)'
    
    # 총 가치
    total_value = final_value * shares
    owned_value = final_value * owned_shares
    
    return {
        "netAssetPerShare": net_asset_per_share,
        "assetValueWithGoodwill": asset_value_with_goodwill,
        "incomeValue": income_value,
        "finalValue": final_value,
        "totalValue": total_value,
        "ownedValue": owned_value,
        "methodText": method_text,
        "futureTotalEquity": future_total_equity,
        "futureWeightedIncome": future_weighted_income,
        "growthRate": growth_rate,
        "futureYears": future_years
    }

# 페이지 헤더
st.title("미래 주식가치 예측")

if not st.session_state.get('evaluated', False):
    st.warning("먼저 '비상장주식 평가' 페이지에서 평가를 진행해주세요.")
    st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>비상장주식 평가</b> 메뉴를 클릭하여 평가를 먼저 진행하세요.</div>", unsafe_allow_html=True)
else:
    stock_value = st.session_state.stock_value
    company_name = st.session_state.company_name
    total_equity = st.session_state.total_equity
    shares = st.session_state.shares
    owned_shares = st.session_state.owned_shares
    interest_rate = st.session_state.interest_rate
    evaluation_method = st.session_state.evaluation_method
    eval_date = st.session_state.get('eval_date', None)
    
    # 현재 주식 가치 정보 표시
    with st.expander("현재 주식 가치", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**회사명:** {company_name}")
            st.markdown(f"**주당 평가액:** {format_number(stock_value['finalValue'])}원")
        with col2:
            st.markdown(f"**회사 총가치:** {format_number(stock_value['totalValue'])}원")
            st.markdown(f"**적용 평가방식:** {stock_value['methodText']}")
        
        if eval_date:
            st.markdown(f"**평가 기준일:** {eval_date.strftime('%Y년 %m월 %d일')}")
    
    # 미래 가치 예측 설명
    st.markdown("""
    <div class="explanation-text">
        <p>기업 가치는 시간이 지남에 따라 성장할 수 있습니다. 이 페이지에서는 회사의 예상 성장률을 적용하여 
        미래 시점의 주식 가치를 예측합니다. 성장률과 예측 기간을 선택하면 현재 가치를 기준으로 
        미래 가치를 계산합니다.</p>
        <p>계산된 미래 가치는 현재 가치와 함께 비교 차트로 표시되며, 성장에 따른 가치 증가율도 확인할 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("미래 가치 계산 입력")
    
    # 성장률 및 예측 기간 선택
    with st.container():
        st.markdown("<div class='growth-panel'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            growth_rate = st.selectbox(
                "연평균 성장률 (%)",
                [5, 10, 15, 20, 25, 30],
                index=1,  # 기본값 10%
                help="회사의 연평균 성장률 예상치입니다. 과거 실적과 미래 전망을 고려하여 선택하세요."
            )
            st.markdown(f"<small>선택한 성장률 {growth_rate}%는 매년 복리로 적용됩니다.</small>", unsafe_allow_html=True)
        
        with col2:
            future_years = st.selectbox(
                "예측 기간 (년)",
                [5, 10, 15, 20, 30],
                index=1,  # 기본값 10년
                help="미래 가치를 예측할 기간을 선택하세요."
            )
            target_year = datetime.now().year + future_years
            st.markdown(f"<small>{target_year}년 기준으로 예측합니다.</small>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    if 'future_stock_value' not in st.session_state:
        st.session_state.future_stock_value = None
    if 'future_evaluated' not in st.session_state:
        st.session_state.future_evaluated = False
    
    # 계산 버튼
    if st.button("미래 가치 계산하기", type="primary", use_container_width=True):
        with st.spinner("계산 중..."):
            # 미래 주식 가치 계산
            st.session_state.future_stock_value = calculate_future_stock_value(
                stock_value, total_equity, shares, owned_shares, 
                interest_rate, evaluation_method, growth_rate, future_years
            )
            st.session_state.future_evaluated = True
            
            st.success("계산이 완료되었습니다.")
            st.balloons()
    
    # 미래 가치 결과 표시
    if st.session_state.future_evaluated and st.session_state.future_stock_value:
        future_stock_value = st.session_state.future_stock_value
        
        st.markdown("---")
        st.subheader("미래 주식가치 평가 결과")
        
        # 예측 요약 정보
        target_year = datetime.now().year + future_years
        st.markdown(f"""
        <div class="info-box">
            <h4>예측 정보 요약</h4>
            <ul>
                <li><b>기준 시점:</b> {datetime.now().year}년</li>
                <li><b>예측 시점:</b> {target_year}년 ({future_years}년 후)</li>
                <li><b>적용 성장률:</b> 연 {growth_rate}% (복리)</li>
                <li><b>적용 평가방식:</b> {future_stock_value['methodText']}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 현재 vs 미래 가치 비교 표시
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div style='text-align: center;'><h4>현재 가치</h4></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='result-highlight' style='text-align: center;'>{format_number(stock_value['finalValue'])}원/주</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center;'>회사 총가치: {format_number(stock_value['totalValue'])}원</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div style='text-align: center;'><h4>미래 가치</h4></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='result-highlight' style='text-align: center;'>{format_number(future_stock_value['finalValue'])}원/주</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center;'>회사 총가치: {format_number(future_stock_value['totalValue'])}원</div>", unsafe_allow_html=True)
        
        # 증가율 정보 표시
        value_increase = (future_stock_value["finalValue"] / stock_value["finalValue"] - 1) * 100
        st.markdown(f"""
        <div style='text-align: center; margin: 20px 0;'>
            <span style='font-size: 18px;'>예상 가치 증가율: </span>
            <span class='percentage-up' style='font-size: 24px;'>+{value_increase:.1f}%</span>
            <span style='font-size: 18px;'> ({future_years}년 후)</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 차트 표시 - 현재와 미래 가치 비교
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['현재', f'{future_years}년 후'],
            y=[stock_value["finalValue"], future_stock_value["finalValue"]],
            marker_color=['lightblue', 'orange'],
            text=[format_number(stock_value["finalValue"]), format_number(future_stock_value["finalValue"])],
            textposition='auto'
        ))
        fig.update_layout(
            title='주당 가치 비교',
            yaxis_title='주당 가치 (원)',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 성장 세부 내역
        with st.expander("미래 가치 계산 세부내역", expanded=False):
            details_df = pd.DataFrame({
                "항목": [
                    "미래 자본총계", 
                    "1주당 순자산가치", 
                    "1주당 손익가치", 
                    "미래 주당 평가액", 
                    "미래 회사 총 주식가치", 
                    "미래 대표이사 보유주식 가치"
                ],
                "금액 (원)": [
                    format_number(future_stock_value["futureTotalEquity"]),
                    format_number(future_stock_value["netAssetPerShare"]),
                    format_number(future_stock_value["incomeValue"]),
                    format_number(future_stock_value["finalValue"]),
                    format_number(future_stock_value["totalValue"]),
                    format_number(future_stock_value["ownedValue"])
                ]
            })
            
            st.dataframe(
                details_df,
                column_config={
                    "항목": st.column_config.TextColumn("항목"),
                    "금액 (원)": st.column_config.TextColumn("금액 (원)", width="large"),
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.markdown("""
            <div class="explanation-text">
                <p><b>계산 방법 설명:</b></p>
                <ol>
                    <li>선택한 연평균 성장률을 복리로 적용하여 미래 자본총계와 가중평균 당기순이익을 계산합니다.</li>
                    <li>계산된 미래 자산과 수익을 기반으로 비상장주식 평가방법을 적용합니다.</li>
                    <li>적용된 평가방법에 따라 최종 주당 가치와 회사 총가치를 산출합니다.</li>
                </ol>
                <p>이 예측은 선택한 성장률이 일정하게 유지된다는 가정 하에 계산됩니다. 실제 기업 성장은 다양한 요인에 따라 변동될 수 있습니다.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 평가 결과 다운로드 섹션 추가
        st.markdown("---")
        with st.expander("📥 평가 결과 다운로드", expanded=False):
            st.markdown("<div class='download-section'>", unsafe_allow_html=True)
            tab1, tab2, tab3 = st.tabs(["PDF", "HTML", "CSV"])
            
            # PDF 다운로드 탭
            with tab1:
                if st.button("PDF 생성하기", key="generate_pdf", type="primary"):
                    with st.spinner("PDF 생성 중..."):
                        pdf_data = generate_pdf(stock_value, future_stock_value, company_name, growth_rate, future_years)
                        
                        if pdf_data:
                            st.success("PDF 생성 완료!")
                            st.download_button(
                                label="📄 PDF 파일 다운로드",
                                data=pdf_data,
                                file_name=f"미래주식가치_{company_name}_{target_year}.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.warning("PDF 생성에 실패했습니다. HTML 형식으로 다운로드해보세요.")
                            st.info("또는 'pip install fpdf fpdf2' 명령으로 필요한 라이브러리를 설치해보세요.")
            
            # HTML 다운로드 탭
            with tab2:
                if st.button("HTML 보고서 생성하기", key="generate_html"):
                    html_content = create_html_content(stock_value, future_stock_value, company_name, growth_rate, future_years)
                    
                    st.download_button(
                        label="📄 HTML 파일 다운로드",
                        data=html_content,
                        file_name=f"미래주식가치_{company_name}_{target_year}.html",
                        mime="text/html"
                    )
                    
                    st.info("HTML 파일을 다운로드 후 브라우저에서 열어 인쇄하면 PDF로 저장할 수 있습니다.")
            
            # CSV 다운로드 탭
            with tab3:
                if st.button("CSV 데이터 생성하기", key="generate_csv"):
                    csv_content = create_csv_content(stock_value, future_stock_value, company_name, growth_rate, future_years)
                    
                    st.download_button(
                        label="📄 CSV 파일 다운로드",
                        data=csv_content,
                        file_name=f"미래주식가치_{company_name}_{target_year}.csv",
                        mime="text/csv"
                    )
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # 미래 세금 계산 버튼
        if st.button("미래 세금 계산하기", type="primary", use_container_width=True):
            try:
                st.switch_page("5_미래_세금계산.py")
            except:
                st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>미래 세금계산</b> 메뉴를 클릭하여 이동하세요.</div>", unsafe_allow_html=True)
