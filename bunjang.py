"""
번개장터 크롤링 모듈
"""
import json
import traceback
import time, os
import datetime as dt


# selenium의 webdriver를 사용하기 위한 import
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException , ElementNotInteractableException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options
from dotenv import load_dotenv


from Settings.Logger.logging_config import bunjang_logger as logger

load_dotenv()
settings  = os.environ # .env에 들어있는 설정 내용들이 여기 있다.
RUNNING_MODE = settings.get('RUNNING_MODE')
RESULT_DIR_PATH = settings.get('RESULT_DIR_PATH')
CHROMEDRIVER_PATH = settings.get('CHROMEDRIVER_PATH')
CHROMEBROWSER_PATH = settings.get('CHROMEBROWSER_PATH')


# 크롬 브라우저 실행 후 번개장터로 이동
def mv_bunjang():
    try:
        logger.info('Open chromedriver & Bunjag start')
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
        
        
        
        driver.get('https://m.bunjang.co.kr')
        time.sleep(5)
        logger.info('Open chromedriver & Bunjag complete')
        
        return driver
    except Exception as e:
        logger.error('Open err chromedriver : ' + str(e))
        logger.error(traceback.format_exc())
        
        return False
    
# 검색어 입력, 검색 버튼 클릭
def bunjang_search(driver, key):
    try:
        logger.info(f'Keyword search start :: {key}')
        ## 검색어 입력 창
        driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[1]/div[1]/div[1]/input').send_keys(key)
        ## 검색어 버튼 클릭
        driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[1]/div[1]/div[1]/a').click()
        logger.info(f'Keyword search completed :: {key}')

        return True
    except Exception as e:
        logger.error('Keyword search err : ' + str(e))
        logger.error(traceback.format_exc())

        return False
    
# Get tag data
def bunjang_get_tag(driver, count):
    try:
        logger.info("Get tag data start")
        list = []
        # 태그 데이터 가져오기
        for index in range(1, count + 1):
            tag_data = driver.find_element(By.XPATH, f'//*[@id="root"]/div/div/div[4]/div[1]/div/div[5]/div[1]/div/div[1]/div[2]/div[2]/div[3]/div[2]/a[{index}]').text
            list.append(tag_data)
        # 구분자 ', '로 join
        list = ', '.join(list)
        logger.info('Get tag data complete')
        return list
    except Exception as e:
        logger.error('Get tag err : ' + str(e))
        logger.error(traceback.format_exc())
        return False
    
    
# Get detail data
def bunjang_get_detail_data(driver, dict, data_index):
    try:
        logger.info('Get detail data start')
        time.sleep(3)
        dict_keys = ['상품상태', '교환여부', '배송비']

        for index in range(1,4):
            time.sleep(3)
            try:
                dict['Product'][data_index][dict_keys[index-1]] = driver.find_element(By.XPATH, f'//*[@id="root"]/div/div/div[4]/div[1]/div/div[2]/div/div[2]/div/div[1]/div[2]/div[2]/div[{index}]/div[2]').text
            except NoSuchElementException:
                with open('/home/ml/work/selenium/html_log/log_html.html', 'w', encoding='UTF-8') as file:
                    file.write(driver.page_source)
                    file.close()
                    logger.error(driver.current_url)                                                                                
        # 등록 일시 
        dict['Product'][data_index]['등록일시'] = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[4]/div[1]/div/div[2]/div/div[2]/div/div[1]/div[2]/div[1]/div/div[3]').text
        
        # 카테고리
        cate = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[4]/div[1]/div/div[1]/div').text
        dict['Product'][data_index]['카테고리'] = cate.replace('\n', ' > ')
        
        # 상품 정보
        dict['Product'][data_index]['상품정보'] = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[4]/div[1]/div/div[5]/div[1]/div/div[1]/div[2]/div[1]').text
        # 상품 태그
        get_all_a = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[4]/div[1]/div/div[5]/div[1]/div/div[1]/div[2]/div[2]/div[3]/div[2]')
        a_tags = get_all_a.find_elements(By.TAG_NAME, 'a')
        tag_data = bunjang_get_tag(driver=driver, count=len(a_tags))
        # 태그 데이터가 있을 시 '#' 포함
        if '#' in tag_data:
            dict['Product'][data_index]['상품태그'] = tag_data
        else:
            dict['Product'][data_index]['상품태그'] = '없음'
            logger.info('No tag')
        logger.info('Get detail data complete')
        driver.back()
        logger.info('Move main page')

        return True
    except Exception as e:
        logger.error('Get detail data err' + str(e))
        logger.error(traceback.format_exc())

        return False
    
    
# Get content
def bunjang_get_content(driver, dict, key, page: int = 0):
    try:
        logger.info('Get content data start')
        time.sleep(3)
        data_index = 1
        dict['Product'] = {}
        time.sleep(3)
        # 번개장터는 1페이지가 a태그 2의 값이라 2로 시작
        for page_index in range(2, page + 2):
            try:
                if page_index == 2: pass
                else:
                    driver.find_element(By.XPATH, f'//*[@id="root"]/div/div/div[4]/div/div[5]/div/a[{page_index}]').click()
                    time.sleep(3)
            except ElementNotInteractableException:
                logger.error('No next page')
                dict['총 페이지'] = f'요청 페이지 수 :: {page} :: 유효페이지 :: {page_index - 2}'
                break
            contents = driver.find_elements(By.XPATH, '//*[@id="root"]/div/div/div[4]/div/div[4]/div/div')
            logger.info(f'Total page :: {page} :: current page :: {page_index - 1} :: content :: {len(contents)}')
            for div_index in range(1, len(contents) + 1):
                logger.info(f'Total :: {len(contents)} :: current :: {div_index}')
                dict['Product'][data_index] = {}   
                address = driver.find_element(By.XPATH, f'//*[@id="root"]/div/div/div[4]/div/div[4]/div/div[{div_index}]/a/div[3]').text
                # 주소에 '광고'가 있을 경우 pass
                if '광고' in address:
                    logger.info('AD')
                    continue
                # 광고가 아닌 것만 스크랩핑
                else:
                    data_pid = driver.find_element(By.XPATH, f'//*[@id="root"]/div/div/div[4]/div/div[4]/div/div[{div_index}]/a').get_attribute('data-pid')
                    title = driver.find_element(By.XPATH, f'//*[@id="root"]/div/div/div[4]/div/div[4]/div/div[{div_index}]/a/div[2]/div[1]').text
                    price = driver.find_element(By.XPATH, f'//*[@id="root"]/div/div/div[4]/div/div[4]/div/div[{div_index}]/a/div[2]/div[2]/div[1]').text
                    
                    dict['Product'][data_index]['상품명'] = title
                    dict['Product'][data_index]['상품가격'] = price
                    dict['Product'][data_index]['거래지역'] = address
                    dict['Product'][data_index]['Data-id'] = data_pid
                    
                    try:
                        check_soldout = driver.find_element(By.XPATH, f'//*[@id="root"]/div/div/div[4]/div/div[4]/div/div[{div_index}]/a/div[1]/div[2]/div/img').get_attribute('alt')
                        if check_soldout == '판매 완료':
                            logger.info('Sold out data')
                            driver.get(f'https://m.bunjang.co.kr/products/{data_pid}?q={key}')
                            time.sleep(3)
                            mv_detail = 1
                            while True:
                                if 'content_owner' in driver.current_url:
                                    logger.info('Load detail page complete')
                                    break
                                elif mv_detail % 2 == 0:
                                    driver.find_element(By.CLASS_NAME, 'Productsstyle__SoldoutProductWrapper-sc-13cvfvh-33.ewWeeg').click()
                                    logger.info(f'Load detail page ... {mv_detail}')
                                    time.sleep(1)
                                    mv_detail += 1
                                else:
                                    driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[4]/div[1]/div/div[2]/div[1]/a/div[2]/div[1]').click()
                                    logger.info(f'Load detail page ... {mv_detail}')
                                    time.sleep(1)
                                    mv_detail += 1
                            time.sleep(5)
                            return_detail = bunjang_get_detail_data(driver=driver, dict=dict, data_index=data_index)
                            driver.back()
                        else:
                            # 예약중인 경우
                            # 상세로 이동
                            driver.get(f'https://m.bunjang.co.kr/products/{data_pid}?q={key}')
                            time.sleep(3)
                            return_detail = bunjang_get_detail_data(driver=driver, dict=dict, data_index=data_index)
                    except NoSuchElementException:
                        # page_source = driver.page_source
                        # with open('Results/VMW.text' , 'w') as file:
                        #     file.write(page_source)
                        #     pass
                        
                        # 상세로 이동
                        driver.get(f'https://m.bunjang.co.kr/products/{data_pid}?q={key}')
                        time.sleep(3)
                        return_detail = bunjang_get_detail_data(driver=driver, dict=dict, data_index=data_index)
                    
                    
                    if return_detail == True:   
                        data_index += 1
                    else:
                        logger.error('detail err')
                    time.sleep(3)

        logger.info('Get content data complete')
        return dict
    except Exception as e:
        logger.error('Get content data err : ' + str(e))
        logger.error(traceback.format_exc())

        return False
    
    
# Bunjang main
def bunjang_crawl(crawl_keyword , crawl_page_count , task_seq):
    try:
        start = time.time()
        dict = {}
        project_name = '번개장터'
        page_num = crawl_page_count
        key = crawl_keyword
        now = dt.datetime.now()
        now_ymd = now.strftime('%Y-%m-%d')
        now_ymd_hms = now.strftime('%Y-%m-%d %H:%M:%S')
        
        driver = mv_bunjang()
        if driver.session_id is not None:
            return_search = bunjang_search(driver=driver, key=key)
            if return_search == True:
                dict['사이트'] = project_name
                dict['검색어'] = key
                dict['날짜'] = now_ymd_hms
                dict['총 페이지'] = page_num
                result = bunjang_get_content(driver=driver, dict=dict, key=key, page=page_num)
            else:
                logger.error('Main :: search err')
        else:
            logger.error('Main :: get driver err')
            
        logger.info('Quit driver')
        driver.quit()

        # 처리 시간
        end = time.time()
        processing_time = end - start

        # 초를 시, 분, 초로 변환
        minutes, seconds = divmod(processing_time, 60)
        hours, minutes = divmod(minutes, 60)
        logger.info(f"총 처리 건수 :: {len(result['Product'])}건 :::: 처리 시간 :: {int(hours)}시간 {int(minutes)}분 {int(seconds)}초")
        return result
    except:
        raise Exception("번개장터 크롤링 작업중 에러 발생")