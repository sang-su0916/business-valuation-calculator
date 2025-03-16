# HTML 다운로드 탭 부분 수정 (tab2 부분)
with tab2:
    if st.button("보고서 생성하기", key="generate_report"):
        with st.spinner("보고서 생성 중..."):
            # 그래프를 이미지로 변환
            import io
            import base64
            from plotly.io import to_image
            
            # 원형 차트 생성 (파이차트)
            labels = ['순자산가치', '영업권 가치']
            values = [stock_value["netAssetPerShare"], stock_value["assetValueWithGoodwill"] - stock_value["netAssetPerShare"]]
            
            pie_fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
            pie_fig.update_layout(
                title_text='주당 가치 구성',
                width=500,
                height=400
            )
            
            # 막대 차트 생성
            bar_fig = go.Figure()
            bar_fig.add_trace(go.Bar(
                x=['순자산가치', '손익가치', '최종평가액'],
                y=[stock_value["netAssetPerShare"], stock_value["incomeValue"], stock_value["finalValue"]],
                marker_color=['lightblue', 'lightgreen', 'coral']
            ))
            bar_fig.update_layout(
                title_text='주요 가치 비교 (주당)',
                width=500,
                height=400
            )
            
            # 그래프를 이미지로 변환하여 base64 인코딩
            try:
                pie_img = to_image(pie_fig, format="png", engine="kaleido")
                bar_img = to_image(bar_fig, format="png", engine="kaleido")
                
                pie_base64 = base64.b64encode(pie_img).decode('utf-8')
                bar_base64 = base64.b64encode(bar_img).decode('utf-8')
                
                graphs_success = True
            except Exception as e:
                graphs_success = False
                st.error(f"그래프 생성 중 오류: {str(e)}")
                st.info("먼저 필요한 라이브러리를 설치하세요: pip install plotly kaleido")
            
            # 결과 테이블에 스타일 적용 
            # DataTable 생성을 위한 함수
            def create_styled_table(dataframe):
                html_table = """
                <table style="width:100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #4285f4; color: white;">
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">항목</th>
                            <th style="padding: 12px; text-align: right; border: 1px solid #ddd;">금액 (원)</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                
                # 행 스타일을 번갈아가며 적용
                for idx, row in dataframe.iterrows():
                    bg_color = "#f2f2f2" if idx % 2 == 0 else "white"
                    html_table += f"""
                        <tr style="background-color: {bg_color};">
                            <td style="padding: 10px; text-align: left; border: 1px solid #ddd;">{row['항목']}</td>
                            <td style="padding: 10px; text-align: right; border: 1px solid #ddd; font-weight: bold;">{row['금액 (원)']}</td>
                        </tr>
                    """
                
                html_table += """
                    </tbody>
                </table>
                """
                return html_table
            
            styled_table = create_styled_table(results_df)
            
            # 완성된 HTML 보고서 생성
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>주식가치 평가 보고서 - {company_name}</title>
                <style>
                    body {{ 
                        font-family: 'Arial', sans-serif; 
                        margin: 0; 
                        padding: 0;
                        color: #333;
                        line-height: 1.6;
                    }}
                    .container {{
                        max-width: 1000px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background-color: #4285f4;
                        color: white;
                        padding: 20px;
                        text-align: center;
                        border-radius: 5px 5px 0 0;
                        margin-bottom: 30px;
                    }}
                    .header h1 {{ 
                        margin: 0; 
                        font-size: 28px;
                    }}
                    .company-info {{
                        display: flex;
                        justify-content: space-between;
                        background-color: #f5f5f5;
                        padding: 15px;
                        border-radius: 5px;
                        margin-bottom: 20px;
                        border-left: 5px solid #4285f4;
                    }}
                    .info-item {{
                        margin: 0;
                        font-size: 16px;
                    }}
                    .info-item strong {{
                        color: #4285f4;
                    }}
                    .section {{
                        margin-bottom: 30px;
                    }}
                    .section-title {{
                        border-bottom: 2px solid #4285f4;
                        padding-bottom: 10px;
                        color: #4285f4;
                        font-size: 20px;
                    }}
                    .graphs-container {{
                        display: flex;
                        justify-content: space-between;
                        flex-wrap: wrap;
                        margin: 20px 0;
                    }}
                    .graph {{
                        width: 48%;
                        margin-bottom: 20px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                        border-radius: 5px;
                        overflow: hidden;
                    }}
                    .summary-box {{
                        background-color: #e8f4f8;
                        padding: 15px;
                        border-radius: 5px;
                        border-left: 5px solid #34a853;
                        margin: 20px 0;
                    }}
                    .highlight {{
                        color: #34a853;
                        font-weight: bold;
                    }}
                    .footer {{
                        margin-top: 30px;
                        padding-top: 15px;
                        border-top: 1px solid #ddd;
                        font-size: 12px;
                        color: #666;
                        text-align: center;
                    }}
                    @media print {{
                        body {{ 
                            -webkit-print-color-adjust: exact; 
                            print-color-adjust: exact;
                        }}
                        .no-print {{
                            display: none;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>주식가치 평가 보고서</h1>
                    </div>
                    
                    <div class="company-info">
                        <p class="info-item"><strong>회사명:</strong> {company_name}</p>
                        <p class="info-item"><strong>평가 기준일:</strong> {eval_date}</p>
                        <p class="info-item"><strong>적용 평가방식:</strong> {stock_value["methodText"]}</p>
                    </div>
                    
                    <div class="section">
                        <h2 class="section-title">주요 계산 결과</h2>
                        {styled_table}
                    </div>
                    
                    <div class="summary-box">
                        자본총계({format_number(total_equity)}원) 대비 평가 회사가치는 <span class="highlight">{stock_value["increasePercentage"]}%</span>로 평가되었습니다.
                    </div>
            """
            
            # 그래프가 성공적으로 생성된 경우 HTML에 추가
            if graphs_success:
                html_content += f"""
                    <div class="section">
                        <h2 class="section-title">시각화 분석</h2>
                        <div class="graphs-container">
                            <div class="graph">
                                <img src="data:image/png;base64,{pie_base64}" alt="주당 가치 구성" style="width:100%;">
                            </div>
                            <div class="graph">
                                <img src="data:image/png;base64,{bar_base64}" alt="주요 가치 비교" style="width:100%;">
                            </div>
                        </div>
                    </div>
                """
            
            # HTML 마무리
            html_content += f"""
                    <div class="section">
                        <h2 class="section-title">결론 및 권장사항</h2>
                        <p>상기 평가 결과는 상속세 및 증여세법 시행령 제54조에 근거하여 계산되었습니다. 해당 평가액은 다음 목적으로 활용할 수 있습니다:</p>
                        <ul>
                            <li>비상장주식 양도 시 참고 가격</li>
                            <li>상속 또는 증여 시 과세 표준 산정의 기초 자료</li>
                            <li>회사의 기업가치 상승을 위한 전략 수립의 기준점</li>
                        </ul>
                    </div>
                    
                    <div class="footer">
                        <p>본 보고서는 참고용으로만 사용하시고, 정확한 세금 계산을 위해서는 전문가와 상담하시기 바랍니다.</p>
                        <p>© {datetime.now().year} 기업가치 평가 계산기. 모든 권리 보유.</p>
                    </div>
                </div>
                
                <!-- 인쇄 안내 (화면에서만 표시) -->
                <div class="no-print" style="text-align:center; margin:30px 0; padding:15px; background-color:#f5f5f5; border-radius:5px;">
                    <p style="font-weight:bold;">PDF로 저장하려면 브라우저의 인쇄 기능을 사용하세요.</p>
                    <p>인쇄 설정에서 배경 그래픽 옵션을 활성화하세요.</p>
                    <button onclick="window.print()" style="padding:10px 20px; background:#4285f4; color:white; border:none; border-radius:5px; cursor:pointer;">인쇄하기</button>
                </div>
            </body>
            </html>
            """
            
            # 다운로드 버튼 표시
            st.success("보고서가 생성되었습니다!")
            st.download_button(
                label="📄 HTML 보고서 다운로드",
                data=html_content,
                file_name=f"주식가치_평가보고서_{company_name}_{eval_date}.html",
                mime="text/html"
            )
            
            # 미리보기 표시
            st.markdown("### 보고서 미리보기")
            st.components.v1.html(html_content, height=500, scrolling=True)
            
            # PDF 변환 안내
            st.info("PDF로 저장하려면 HTML 파일을 다운로드한 후 브라우저에서 열어 인쇄 기능을 사용하세요. (대상을 '다른 이름으로 PDF 저장'으로 선택)")
