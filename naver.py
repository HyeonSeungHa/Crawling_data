import time, os
import datetime as dt
import json
import traceback


# selenium의 webdriver를 사용하기 위한 import
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options
from dotenv import load_dotenv


from Settings.Logger.logging_config import naver_logger as logger 


load_dotenv()
settings  = os.environ # .env에 들어있는 설정 내용들이 여기 있다.
RUNNING_MODE = settings.get('RUNNING_MODE')
RESULT_DIR_PATH = settings.get('RESULT_DIR_PATH')
CHROMEDRIVER_PATH = settings.get('CHROMEDRIVER_PATH')
CHROMEBROWSER_PATH = settings.get('CHROMEBROWSER_PATH')

##############################################################################
# 네이버 쇼핑
##############################################################################

# 크롬 브라우저 실행 후 네이버 쇼핑으로 이동
# 크롬 브라우저 실행 후 네이버 쇼핑으로 이동
def mv_naver_shopping():
    try:
        logger.info('Open chromedriver & Naver shopping start')
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        option.add_argument('--no-sandbox')
        option.add_argument('--window-size=1920,1080') # Chromedriver size 변경
        option.binary_location = CHROMEBROWSER_PATH
        
        # driver = webdriver.Chrome(options=option)
        s = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=s, options=option)

        
        # firefox_options = Options()
        # firefox_options.add_argument('--headless')
        # firefox_options.add_argument('--window-size=1920,1080')
        # s = Service('crawl_module/chromedriver_mac_arm64/geckodriver')
        # driver = webdriver.Firefox(options=firefox_options,service=s)
        
        
        driver.get('https://shopping.naver.com/home')
        
        # time.sleep(7)
        time.sleep(3)
        logger.info('Open chromedriver & Naver shopping complete')
        
        return driver
    except Exception as e:
        logger.error('Open err chromedriver : ' + str(e))
        logger.error(traceback.format_exc())

        return False
    
    
# 검색어 입력, 검색 버튼 클릭, 가격비교 탭으로 이동
def naver_search(driver, key: str = None):
    try:
        logger.info(f'Keyword search start :: {key}')
        ## 검색어 입력 창
        driver.find_element(By.XPATH, '//*[@id="gnb-gnb"]/div[2]/div/div[2]/div/div[2]/form/div[1]/div[1]/input').send_keys(key)
        ## 검색어 버튼 클릭
        driver.find_element(By.XPATH, '//*[@id="gnb-gnb"]/div[2]/div/div[2]/div/div[2]/form/div[1]/div[1]/button[2]').click()
        ## '가격비교' 탭 클릭
        driver.find_element(By.XPATH, '//*[@id="content"]/div[1]/div[1]/ul/li[2]/a').click()
        logger.info(f'Keyword search completed :: {key}')
        
        return True
    except Exception as e:
        logger.error('Keyword search err : ' + str(e))
        logger.error(traceback.format_exc())

        return False
    
# 스크롤 다운
def naver_scroll_down(driver):
    try:
        logger.info('Scroll down start')
        # 스크롤 높이 가져옴
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # 끝까지 스크롤 다운
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # 1초 대기
            # time.sleep(7)
            time.sleep(2)

            # 스크롤 다운 후 스크롤 높이 다시 가져옴
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        logger.info('Scroll down complete')
        
        return True
    except Exception as e:
        logger.error('Scroll down err : ' + str(e))
        logger.error(traceback.format_exc())

        return False
    
# 브랜드 카탈로그 브랜드 명, 브랜드별 가격
def naver_get_product_mall(driver, dict, count: int = 0, data_index: int = 0):
    try:
        logger.info('Start get product mall data')
        dict['Product'][data_index]['가격비교'] = {}
        for index in range(1, count+1):
            try:
                logger.info(f'Total :: {count} :: current :: {index}')
                get_tag = driver.find_element(By.XPATH, f'//*[@id="content"]/div[1]/div/div[2]/div[2]/table/tbody/tr[{index}]/td[1]/div/a/img')
                brnd_nm = get_tag.get_attribute('alt')
                brnd_price = driver.find_element(By.XPATH, f'//*[@id="content"]/div[1]/div/div[2]/div[2]/table/tbody/tr[{index}]/td[2]/a/em').text
            except NoSuchElementException:
                try:
                    brnd_nm = driver.find_element(By.XPATH, f'//*[@id="content"]/div[1]/div/div[2]/div[2]/table/tbody/tr[{index}]/td[1]/div/a').text
                    brnd_price = driver.find_element(By.XPATH, f'//*[@id="content"]/div[1]/div/div[2]/div[2]/table/tbody/tr[{index}]/td[2]/a/em').text
                # 브랜드 공식 판매처만 존재하는 경우
                except NoSuchElementException:
                    try:
                        brnd_nm = driver.find_element(By.XPATH, f'//*[@id="content"]/div[1]/div/div[2]/div[2]/div/div[2]/div[1]/div[1]/div/a').text
                        brnd_price = driver.find_element(By.XPATH, f'//*[@id="content"]/div[1]/div/div[2]/div[2]/div/div[2]/div[1]/a').text.split('원')[0]
                        logger.info('Only brand')
                    except NoSuchElementException:
                        brnd_nm = '브랜드명'
                        brnd_price = '없음'
                        logger.info('No brand')
            finally:
                dict['Product'][data_index]['가격비교'][brnd_nm] = brnd_price
                time.sleep(3)
            logger.info('Get product mall data complete')
        return True
    except Exception as e:
        logger.error(f'Get product mall data err : ' + str(e))
        logger.error(traceback.format_exc())

        return False
    
# 제품 스펙
def naver_get_spec(driver, dict, count, data_index: int = 0):
    try:
        logger.info('Get spec data start')
        dict['Product'][data_index]['상세스펙'] = {}
        if count == 0:
            logger.error('No spec')
            dict['Product'][data_index]['상세스펙'] = '없음'
            return True
        else:
            for index in range(1, count):
                logger.info(f'Total :: {count-1} :: current :: {index}')
                spec_data = driver.find_element(By.XPATH, f'//*[@id="container"]/div[2]/div[1]/div[3]/span[{index}]').text
                if spec_data =='':
                    continue
                dict['Product'][data_index]['상세스펙'][spec_data.split(' : ')[0]] = spec_data.split(' : ')[1]
                time.sleep(3)
            time.sleep(3)
            logger.info('Get spec data complete')

            return True
    except Exception as e:
        logger.error('Get spec data err : ' + str(e))
        logger.error(traceback.format_exc())

        return False
    
    
# 카테고리
def naver_get_category(dict, cate_data, data_index: int = 0):
    try:
        logger.info('Get category start')
        cate_list = []
        dict['Product'][data_index]['카테고리'] = {}
        if cate_data:
            for cate_index, cate in enumerate(cate_data):
                logger.info(f'Total :: {len(cate_data)} :: current :: {cate_index + 1}')
                cate_list.append(cate.text)
                time.sleep(3)
            # 구분자 '>'
            cate_list = ' > '.join(cate_list)

            dict['Product'][data_index]['카테고리'] = cate_list
            logger.info('Get category complete')
            
            return True
        else:
            logger.error('No cate')
            dict['Product'][data_index]['카테고리'] = '없음'

            return True
        
    except Exception as e:
        logger.error('Get category err : ' + str(e))
        logger.error(traceback.format_exc())

        return False
    
    
    
# Get content
def naver_get_content(driver, dict, key, page: int = 0):
    try:
        logger.info('Get content data start')
        # data index
        data_index = 1
        title = None
        price = None
        dict['Product'] = {}
        for page_index in range(page):
            try:
                # page_index = 0 인 경우 1페이지
                if page_index == 0: pass
                # 2페이지부터 화면 하단 버튼 클릭을 통해 페이지 이동
                else:
                    driver.find_element(By.XPATH, f'//*[@id="content"]/div[1]/div[4]/div/a[{page_index}]').click()
                    time.sleep(3)
            except NoSuchElementException:
                logger.error('No next page')
                dict['총 페이지'] = f'요청 페이지 수 :: {page} :: 유효페이지 :: {page_index}'
                break
            # 스크롤 다운
            return_scroll = naver_scroll_down(driver=driver)
            if return_scroll == True:
                # contents 갯수 확인
                contents = driver.find_elements(By.XPATH, '//*[@id="content"]/div[1]/div[2]/div/div')
                logger.info(f'Total page :: {page} :: current page :: {page_index + 1} :: content :: {len(contents)}')
                return_scroll = None
                for div_index in range(1, len(contents) + 1):
                    logger.info(f'Total :: {len(contents)} :: current :: {div_index}')
                    time.sleep(3)
                    dict['Product'][data_index] = {}
                    
                    date = driver.find_element(By.XPATH, f'//*[@id="content"]/div[1]/div[2]/div/div[{div_index}]/div/div/div[2]/div[5]/span[1]').text.split(' ')[1]
                    # 상품 명, 상품 가격 text 가져오기
                    try:                                        
                        title = driver.find_element(By.XPATH, f'//*[@id="content"]/div[1]/div[2]/div/div[{div_index}]/div/div/div[2]/div[1]').text
                        price = driver.find_element(By.XPATH, f'//*[@id="content"]/div[1]/div[2]/div/div[{div_index}]/div/div/div[2]/div[2]/strong/span/span[2]/em').text
                    # 상품 가격 element가 다른 경우 
                    except NoSuchElementException:
                        try:
                            title = driver.find_element(By.XPATH, f'//*[@id="content"]/div[1]/div[2]/div/div[{div_index}]/div/div/div[2]/div[1]').text
                            price = driver.find_element(By.XPATH, f'//*[@id="content"]/div[1]/div[2]/div/div[{div_index}]/div/div/div[2]/div[2]/strong/span/span/em').text
                            logger.error(f'NoSuchElementException(different element) :: Get price :: current :: {div_index}')
                        except NoSuchElementException:
                            logger.error('No price(출시예정)')
                            # 마지막 데이터일 경우 해당 data_index 키 삭제
                            if (page == page_index + 1) & (len(contents) == div_index): del dict['Product'][data_index]
                            continue
                        
                    finally:
                        if price is None: continue
                        dict['Product'][data_index]['상품명'] = title
                        dict['Product'][data_index]['상품가격'] = price
                        dict['Product'][data_index]['등록일'] = date
                        title = None
                        price = None
                        logger.info('Get product name, price, registration date')
                    # 카테고리
                    try:
                        get_all_span = driver.find_element(By.XPATH, f'//*[@id="content"]/div[1]/div[2]/div/div[{div_index}]/div/div/div[2]/div[3]')
                        span_contents = get_all_span.find_elements(By.TAG_NAME, 'span')
                        return_cate = naver_get_category(dict=dict, cate_data=span_contents, data_index=data_index)
                    
                    except NoSuchElementException:
                        dict['Product'][data_index]['카테고리'] = {}
                        dict['Product'][data_index]['카테고리'] = '없음'
                        logger.error('No cate')
                        return_cate = True
                        pass

                    time.sleep(3)
                    if return_cate == True:
                        data_id = driver.find_element(By.XPATH, f'//*[@id="content"]/div[1]/div[2]/div/div[{div_index}]/div/div/div[1]/div/a').get_attribute('data-i')
                        dict['Product'][data_index]['Data-id'] = data_id
                        # 상세로 이동
                        driver.get(f'https://search.shopping.naver.com/catalog/{data_id}?query={key}')
                        try:
                            # 상품 스펙
                            get_all_a = driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div[1]/div[3]')
                            a_contents = get_all_a.find_elements(By.TAG_NAME, 'span')
                            
                            return_spec = naver_get_spec(driver=driver, dict=dict, count=len(a_contents), data_index=data_index)
                            time.sleep(3)
                        except NoSuchElementException:
                            logger.error('No spec')

                            dict['Product'][data_index]['상세스펙'] = {}
                            dict['Product'][data_index]['상세스펙'] = '없음'
                            
                            return_spec = True
                            pass
                        if return_spec == True:
                            # 브랜드 카탈로그
                            try: 
                                get_all_li = driver.find_element(By.XPATH, '//*[@id="content"]/div[1]/div/div[2]/div[2]/table/tbody')
                                cnt_li_tag = get_all_li.find_elements(By.TAG_NAME, 'tr')
                            except NoSuchElementException:
                                cnt_li_tag = [' ']
                            return_product = naver_get_product_mall(driver=driver, dict=dict, count=len(cnt_li_tag), data_index=data_index)
                            if return_product == True:
                                driver.back()
                                logger.info('Move main page')
                                # 상세 페이지에서 메인 소스로 갈 시 데이터의 일부만 보이므로 scroll_down
                                return_scroll = naver_scroll_down(driver=driver)
                                if return_scroll == True:
                                    data_index += 1
                                pass
                            pass
                        pass
                    time.sleep(3)
                pass
            time.sleep(2)
        logger.info('Get content data complete')
        return dict
    
    except Exception as e:
        logger.error('Get content data err : ' + str(e))
        logger.error(traceback.format_exc())
        return False
    
    
        

# Naver main
def naver_crawl(crawl_keyword , crawl_page_count , task_seq):
    try:
        start = time.time()
        now = dt.datetime.now()
        now_ymd = now.strftime('%Y-%m-%d')
        now_ymd_hms = now.strftime('%Y-%m-%d %H:%M:%S')
        dict = {}
        project_name = 'NSW'
        page_num = int(crawl_page_count)
        key = crawl_keyword
        
        driver = mv_naver_shopping()
        if driver.session_id is not None:
            return_search = naver_search(driver=driver, key=key)
            if return_search == True:
                return_scroll = naver_scroll_down(driver=driver)
                if return_scroll == True:
                    dict['사이트'] = project_name
                    dict['검색어'] = key
                    dict['날짜'] = now_ymd_hms
                    dict['총 페이지'] = page_num
                    result = naver_get_content(driver=driver, dict=dict, key=key, page=page_num)
                else:
                    logger.error('Main :: scroll_down err')
            else:
                logger.error('Main :: search err')
        else:
            logger.error('Main :: get driver err')
            
        
        logger.info('Quit driver')
        driver.quit()
        end = time.time()
        processing_time = end - start

        logger.info(f"크롤링이 완료되었습니다. {processing_time}초")
        # 초를 시, 분, 초로 변환
        minutes, seconds = divmod(processing_time, 60)
        hours, minutes = divmod(minutes, 60)
        logger.info(f"총 처리 건수 :: {len(result['Product'])}건 :::: 처리 시간 :: {int(hours)}시간 {int(minutes)}분 {int(seconds)}초")
        return result
    except:
        raise Exception("네이버쇼핑 크롤링 작업중 에러 발생")
