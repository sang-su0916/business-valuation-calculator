# 코드 끝부분에 다운로드 기능 추가하기
# 참고사항 밑에 추가하세요 (약 394줄 근처)

    # 다운로드 섹션 추가
    st.subheader("📥 세금 계산 결과 다운로드")
    
    # HTML 보고서 다운로드 버튼
    if st.button("세금 분석 보고서 다운로드", type="primary"):
        # 보고서용 HTML 생성
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>비상장주식 세금 분석 보고서 - {company_name}</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 30px; color: #333; line-height: 1.6; }}
                .container {{ max-width: 1000px; margin: 0 auto; }}
                h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
                h2 {{ color: #3498db; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-top: 30px; }}
                h3 {{ color: #2c3e50; margin-top: 25px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .tax-box {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #3498db; }}
                .tax-amount {{ font-size: 24px; font-weight: bold; color: #e74c3c; margin: 10px 0; }}
                .tax-rate {{ color: #27ae60; font-weight: bold; }}
                .footer {{ margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #777; text-align: center; }}
                .best-option {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #27ae60; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>비상장주식 세금 분석 보고서</h1>
                
                <h2>기본 정보</h2>
                <table>
                    <tr>
                        <th>항목</th>
                        <th>내용</th>
                    </tr>
                    <tr>
                        <td>회사명</td>
                        <td>{company_name}</td>
                    </tr>
                    <tr>
                        <td>평가 기준일</td>
                        <td>{eval_date.strftime('%Y년 %m월 %d일')}</td>
                    </tr>
                    <tr>
                        <td>주당 평가액</td>
                        <td>{simple_format(stock_value['finalValue'])}원</td>
                    </tr>
                    <tr>
                        <td>대표이사 보유주식 가치</td>
                        <td>{simple_format(stock_value['ownedValue'])}원</td>
                    </tr>
                    <tr>
                        <td>회사 총가치</td>
                        <td>{simple_format(stock_value['totalValue'])}원</td>
                    </tr>
                    <tr>
                        <td>가족법인 여부</td>
                        <td>{"예" if is_family_corp else "아니오"}</td>
                    </tr>
                </table>
                
                <h2>세금 분석 요약</h2>
                
                <div class="tax-box">
                    <h3>증여세</h3>
                    <div class="tax-amount">{simple_format(tax_details['inheritanceTax'])}원</div>
                    <div class="tax-rate">실효세율: {tax_details['inheritanceRate']:.1f}%</div>
                    <p>주식을 타인에게 무상으로 증여할 경우 발생하는 세금입니다. 증여 받은 사람이 납부합니다.</p>
                    
                    <h4>적용 세율:</h4>
                    <ul>
                        <li>1억 이하: 10%</li>
                        <li>1억~5억: 20%</li>
                        <li>5억~10억: 30%</li>
                        <li>10억~30억: 40%</li>
                        <li>30억 초과: 50%</li>
                    </ul>
                </div>
                
                <div class="tax-box">
                    <h3>양도소득세</h3>
                    <div class="tax-amount">{simple_format(tax_details['transferTax'])}원</div>
                    <div class="tax-rate">실효세율: {tax_details['transferRate']:.1f}%</div>
                    <p>주식을 매각하여 발생한 이익(양도차익)에 대해 부과되는 세금입니다. 기본공제 250만원이 적용됩니다.</p>
                    
                    <h4>적용 세율:</h4>
                    <ul>
                        <li>3억 이하: 22%</li>
                        <li>3억 초과: 27.5%</li>
                    </ul>
                    
                    <p>취득가액: {simple_format(tax_details['acquisitionValue'])}원</p>
                    <p>양도차익: {simple_format(tax_details['transferProfit'])}원</p>
                </div>
                
                <div class="tax-box">
                    <h3>청산소득세</h3>
                    <div class="tax-amount">{simple_format(tax_details['liquidationTax'])}원</div>
                    <div class="tax-rate">실효세율: {tax_details['liquidationRate']:.1f}%</div>
                    <p>법인 청산 시 발생하는 세금으로, 법인세와 잔여재산 분배에 따른 배당소득세로 구성됩니다.</p>
                    
                    <h4>적용 세율:</h4>
                    <ul>
                        {"<li>가족법인 200억 이하: 19%</li><li>200억~3,000억: 21%</li><li>3,000억 초과: 24%</li>" if is_family_corp else "<li>2억 이하: 9%</li><li>2억~200억: 19%</li><li>200억~3,000억: 21%</li><li>3,000억 초과: 24%</li>"}
                        <li>배당소득세: 15.4%</li>
                    </ul>
                </div>
                
                <div class="best-option">
                    <h3>최적의 세금 옵션</h3>
                    <p>현재 기업가치 수준에서는 <strong>{best_option}</strong>가 세금 부담이 가장 적습니다.</p>
                    
                    <table>
                        <tr>
                            <th>세금 유형</th>
                            <th>세액</th>
                            <th>실효세율</th>
                        </tr>
                        <tr>
                            <td>증여세</td>
                            <td>{simple_format(tax_details['inheritanceTax'])}원</td>
                            <td>{tax_details['inheritanceRate']:.1f}%</td>
                        </tr>
                        <tr>
                            <td>양도소득세</td>
                            <td>{simple_format(tax_details['transferTax'])}원</td>
                            <td>{tax_details['transferRate']:.1f}%</td>
                        </tr>
                        <tr>
                            <td>청산소득세</td>
                            <td>{simple_format(tax_details['liquidationTax'])}원</td>
                            <td>{tax_details['liquidationRate']:.1f}%</td>
                        </tr>
                    </table>
                </div>
                
                <div class="footer">
                    <p>※ 이 보고서의 세금 계산은 참고용으로만 사용하시기 바랍니다. 실제 세금은 개인 상황, 보유기간, 대주주 여부, 사업 형태 등에 따라 달라질 수 있습니다.</p>
                    <p>© {datetime.now().year} 기업가치 평가 계산기. 모든 권리 보유.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        st.download_button(
            label="📄 HTML 보고서 다운로드",
            data=html_content,
            file_name=f"세금분석보고서_{company_name}_{eval_date.strftime('%Y%m%d')}.html",
            mime="text/html"
        )
    
    # CSV 다운로드 버튼
    if st.button("CSV 파일 다운로드"):
        # CSV 데이터 생성
        data = {
            '항목': [
                '회사명', '평가 기준일', '주당 평가액', '회사 총가치', '대표이사 보유주식 가치',
                '가족법인 여부', '증여세', '증여세 실효세율', '양도소득세', '양도소득세 실효세율',
                '청산소득세', '청산소득세 실효세율', '취득가액', '양도차익', '최적세금옵션'
            ],
            '값': [
                company_name, str(eval_date), stock_value['finalValue'], stock_value['totalValue'], stock_value['ownedValue'],
                "예" if is_family_corp else "아니오", tax_details['inheritanceTax'], f"{tax_details['inheritanceRate']:.1f}%",
                tax_details['transferTax'], f"{tax_details['transferRate']:.1f}%", tax_details['liquidationTax'],
                f"{tax_details['liquidationRate']:.1f}%", tax_details['acquisitionValue'], tax_details['transferProfit'],
                best_option
            ]
        }
        
        # DataFrame 생성 후 CSV로 변환
        df = pd.DataFrame(data)
        csv = df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📄 CSV 파일 다운로드",
            data=csv,
            file_name=f"세금분석데이터_{company_name}_{eval_date.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
