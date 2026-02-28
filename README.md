# 수요예측 대시보드

## 실행 방법
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 배포 (Streamlit Cloud)
1. GitHub에 이 폴더 전체 업로드
2. share.streamlit.io 접속 → New App 생성
3. app.py 선택 후 Deploy

## 데이터 파일
- `forecast_data.csv` : 2025.06~2026.02 월별 수요예측량
- `actual_data.csv`   : 2025.08~2026.01 실수주 실적

## 기능
- 년월 드롭다운 (2025.06 ~ 2026.02)
- 브랜드 필터 (시디즈/퍼시스/일룸/데스커)
- 공급단 필터 (시디즈제품/의자양지상품/베트남제품)
- 탭1: 브랜드·공급단 분석 (막대/도넛/히트맵/달성률)
- 탭2: 월별 시계열 추이
- 탭3: 시리즈·품목별 상세 + 차이량 차트
- 탭4: 전체 데이터 조회 및 CSV 다운로드
