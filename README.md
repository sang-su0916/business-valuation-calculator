# 기업가치 약식 평가계산기

상속세 및 증여세법에 따른 비상장주식 평가와 세금 계산을 위한 간단한 웹 애플리케이션입니다.

## 기능

1. 비상장주식 가치 평가
2. 주식가치 평가 결과 확인
3. 현시점 세금 계산 (상속증여세, 양도소득세, 청산소득세)
4. 미래 주식가치 예측 (5년, 10년, 15년, 20년, 30년)
5. 미래시점 세금 계산

## 설치 및 실행 방법

### 1. 로컬 컴퓨터에서 실행하기

#### 필요한 소프트웨어
- Python 3.7 이상 ([다운로드](https://www.python.org/downloads/))
- Git ([다운로드](https://git-scm.com/downloads))

#### 설치 단계
1. 이 저장소를 복제합니다:
```
git clone https://github.com/사용자이름/기업가치-약식-평가계산기.git
cd 기업가치-약식-평가계산기
```

2. 가상환경을 생성하고 활성화합니다:
```
# Windows에서
python -m venv venv
venv\Scripts\activate

# Mac/Linux에서
python -m venv venv
source venv/bin/activate
```

3. 필요한 패키지를 설치합니다:
```
pip install -r requirements.txt
```

4. 애플리케이션을 실행합니다:
```
streamlit run app.py
```

5. 웹 브라우저가 자동으로 열리며 애플리케이션이 표시됩니다.

### 2. Streamlit Cloud에서 실행하기

1. [Streamlit Cloud](https://streamlit.io/cloud) 계정을 만듭니다.
2. 이 저장소를 자신의 GitHub 계정에 복제합니다.
3. Streamlit Cloud에서 "New app" 버튼을 클릭합니다.
4. 저장소, 브랜치, 파일 경로(app.py)를 지정합니다.
5. "Deploy"를 클릭하면 몇 분 내에 앱이 배포됩니다.

## 사용 방법

1. **비상장주식 평가**
   - 회사 기본 정보, 재무 현황, 주식 정보를 입력합니다.
   - 평가 방식을 선택합니다.
   - "계산" 버튼을 클릭합니다.

2. **주식가치 결과**
   - 계산된 주당 평가액과 총 주식가치를 확인합니다.

3. **현시점 세금계산**
   - 증여세, 양도소득세, 청산소득세 등이 계산됩니다.

4. **미래 주식가치**
   - 성장률과 예측 기간을 선택합니다.
   - 미래 시점의 예상 주식가치가 계산됩니다.

5. **미래 세금계산**
   - 미래 시점의 예상 세금이 계산됩니다.

## 참고사항

- 이 계산기는 참고용으로만 사용하시고, 정확한 세금 계산을 위해서는 전문가와 상담하시기 바랍니다.
- 상속세 및 증여세법 시행령 제54조에 근거한 계산 방식을 사용합니다.
