# Crawling_data

## **네이버쇼핑**
  - **메인 페이지의 데이터 이미지**
<br/><br/><br/><br/>
 ![image](https://github.com/user-attachments/assets/c477c00a-ad93-4309-9b0b-0efc3f775b77)
<br/><br/><br/><br/>
  - **상세 페이지 데이터 이미지**
<br/><br/><br/><br/>
  ![image](https://github.com/user-attachments/assets/38918072-067e-4dac-b80b-f3dc6bb100f9)

  - 검색어, 크롤링할 페이지 수를 지정
  - selenium webdriver를 이용해 백그라운드로 크롬 실행
  - 네이버 쇼핑으로 이동 후 지정한 검색 키워드 값을 입력 후 검색 버튼 클릭
  - 가격비교 탭으로 이동
  - 네이버쇼핑은 아래로 스크롤 시 추가적인 데이터가 출력되기 때문에 하단까지 스크롤
  - 상품명, 상품가격, 등록일, 카테고리, Data-id를 크롤링하여 저장
     - 출시 예정인 경우 예외처리
  - Data-id를 이용해 해당 데이터를 상세 페이지로 이동하여 상세스펙, 가격비교를 크롤링하여 저장
  - 상세페이지에서 메인페이지로 이동 시 데이터가 일부만 보이기 때문에 다시 스크롤을 하단까지 스크롤
  - 한 페이지에서의 모든 작업이 끝나면 크롤링한 페이지 수 만큼 페이지를 이동하여 크롤링
<br/><br/><br/><br/>
## **번개장터**
  - **메인 페이지의 데이터 이미지**
<br/><br/><br/><br/>
  ![image](https://github.com/user-attachments/assets/bdb75b32-aaf7-4437-b437-30b9ba9cd3f9)
<br/><br/><br/><br/>
  - **상세 페이지 데이터 이미지**
<br/><br/><br/><br/>
  ![image](https://github.com/user-attachments/assets/9d62dc30-1b82-46c1-b8f3-1a7edc2d77d1)
  ![image](https://github.com/user-attachments/assets/4654baaa-4dfb-4992-9c4c-5ee11a34c3d5)
<br/><br/><br/><br/>
  - **판매 완료인 경우**
<br/><br/><br/><br/>
  ![image](https://github.com/user-attachments/assets/355afa11-b21d-439a-82ca-79d5f42cfb57)
<br/><br/><br/><br/>
  - 검색어, 크롤링할 페이지 수를 지정
  - selenium webdriver를 이용해 백그라운드로 크롬 실행
  - 번개장터로 이동 후 지정한 검색 키워드 값을 입력 후 검색 버튼 클릭
  - 상품명, 상품가격, 거래지역, Data-id를 크롤링하여 저장
      - 해당 데이터가 광고인 경우 예외처리
      - 판매완료인 경우 바로 상세 페이지로 넘어가지 않기 때문에 해당 창에서 한번 더 클릭하여 상세로 이동
      - 예약중인 경우 기존과 동일하여(상세로 이동) 동일하게 처리
  - Data-id를 이용해 해당 데이터를 상세 페이지로 이동하여 등록일시, 카테고리, 상품정보, 상품 태그를 크롤링하여 저장
  - 한 페이지에서의 모든 작업이 끝나면 크롤링한 페이지 수 만큼 페이지를 이동하여 크롤링
