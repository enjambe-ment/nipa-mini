import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime


# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

# 웹드라이버 초기화
driver = webdriver.Chrome(options=chrome_options)


# PostgreSQL 연결 설정 (본인의 DB 정보로 수정)
DB_CONFIG = {
    'host': '193.122.124.108',
    'database': 'testdb',
    'user': 'test01',
    'password': 'test1234',
    'port': 5432
}


def connect_db():
    """데이터베이스 연결"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"DB 연결 오류: {e}")
        return None


def get_disease_list_from_page(driver, page_index):
    """특정 페이지에서 질병 목록 추출"""
    disease_data = []
    
    try:
        url = f"https://www.snuh.org/health/nMedInfo/nList.do?pageIndex={page_index}&sortType=&searchNWord=&searchKey="
        
        print(f"[페이지 {page_index}] 로딩 중...")
        driver.get(url)
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        thumb_container = soup.find('div', class_='thumbType04')
        
        if not thumb_container:
            print(f"[페이지 {page_index}] thumbType04 div를 찾을 수 없습니다.")
            return [], False
        
        items = thumb_container.find_all('div', class_='item')
        print(f"[페이지 {page_index}] {len(items)}개 item 발견")
        
        for item in items:
            strong_tag = item.find('strong')
            if not strong_tag:
                continue
            
            disease_name = strong_tag.get_text(strip=True)
            link = item.find('a', href=True)
            if not link:
                continue
            
            href = link.get('href', '')
            
            if disease_name:
                if href.startswith('./'):
                    full_url = f"https://www.snuh.org/health/nMedInfo/{href[2:]}"
                elif href.startswith('/'):
                    full_url = f"https://www.snuh.org{href}"
                else:
                    full_url = f"https://www.snuh.org/health/nMedInfo/{href}"
                
                full_url = full_url.replace('/./', '/')
                
                disease_data.append({
                    'disease_name': disease_name,
                    'url': full_url,
                    'page': page_index
                })
        
        print(f"[페이지 {page_index}] {len(disease_data)}개 질병 수집")
        return disease_data, len(disease_data) > 0
        
    except Exception as e:
        print(f"[페이지 {page_index}] 오류: {e}")
        return [], False


def get_all_disease_list(driver, max_pages=200):
    """모든 페이지에서 질병 목록 추출"""
    all_diseases = []
    consecutive_empty = 0
    
    print("=" * 60)
    print("전체 페이지 크롤링 시작")
    print("=" * 60)
    
    for page_index in range(1, max_pages + 1):
        disease_list, has_data = get_disease_list_from_page(driver, page_index)
        
        if has_data:
            all_diseases.extend(disease_list)
            consecutive_empty = 0
        else:
            consecutive_empty += 1
            print(f"[경고] 페이지 {page_index}에 데이터가 없습니다. ({consecutive_empty}/3)")
            
            if consecutive_empty >= 3:
                print(f"\n연속 3페이지 데이터 없음. 크롤링 종료 (마지막 페이지: {page_index-3})")
                break
        
        time.sleep(1)
    
    # 중복 제거
    unique_diseases = []
    seen_urls = set()
    for disease in all_diseases:
        if disease['url'] not in seen_urls:
            unique_diseases.append(disease)
            seen_urls.add(disease['url'])
    
    print(f"\n총 {len(unique_diseases)}개의 질병 정보 수집 완료 (중복 제거 후)")
    return unique_diseases


def get_disease_detail(driver, url, disease_name):
    """개별 질병 페이지에서 상세 정보 추출"""
    try:
        driver.get(url)
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # 병명 추출
        disease_name_kr = ""
        disease_name_eng = ""
        
        title_elem = soup.find('h3')
        if title_elem:
            title_text = title_elem.get_text(strip=True)
            if '[' in title_text and ']' in title_text:
                disease_name_kr = title_text.split('[')[0].strip()
                disease_name_eng = title_text.split('[')[1].split(']')[0].strip()
            else:
                disease_name_kr = title_text
        else:
            disease_name_kr = disease_name
        
        # 진료과 추출
        department = ""
        dept_div = soup.find('div', class_='viewRow tooltipRow')
        if dept_div:
            em_tag = dept_div.find('em')
            if em_tag and '진료과' in em_tag.get_text():
                p_tag = dept_div.find('p')
                if p_tag:
                    dept_links = p_tag.find_all('a')
                    if dept_links:
                        departments = [link.get_text(strip=True) for link in dept_links]
                        department = ', '.join(departments)
        
        if not department:
            all_viewrows = soup.find_all('div', class_='viewRow')
            for viewrow in all_viewrows:
                em_tag = viewrow.find('em')
                if em_tag and '진료과' in em_tag.get_text():
                    p_tag = viewrow.find('p')
                    if p_tag:
                        dept_links = p_tag.find_all('a')
                        if dept_links:
                            departments = [link.get_text(strip=True) for link in dept_links]
                            department = ', '.join(departments)
                        break
        
        # 증상 추출
        symptoms = ""
        symptom_div = soup.find('div', id='section-증상')
        if symptom_div:
            p_tags = symptom_div.find_all('p')
            if p_tags:
                symptoms_list = [p.get_text(strip=True) for p in p_tags if p.get_text(strip=True)]
                symptoms = ' '.join(symptoms_list)
        
        if not symptoms:
            symptom_headers = soup.find_all('h5')
            for header in symptom_headers:
                if '증상' in header.get_text():
                    parent_div = header.find_parent('div')
                    if parent_div:
                        p_tags = parent_div.find_all('p')
                        if p_tags:
                            symptoms_list = [p.get_text(strip=True) for p in p_tags if p.get_text(strip=True)]
                            symptoms = ' '.join(symptoms_list)
                            break
        
        if not symptoms:
            definition_div = soup.find('div', id='section-정의')
            if definition_div:
                p_tags = definition_div.find_all('p')
                if p_tags:
                    symptoms_list = [p.get_text(strip=True) for p in p_tags[:2] if p.get_text(strip=True)]
                    symptoms = ' '.join(symptoms_list)
        
        result = {
            'disease_name_kr': disease_name_kr,
            'disease_name_eng': disease_name_eng,
            'department': department if department else None,
            'symptoms': symptoms if symptoms else None,
            'url': url
        }
        
        return result
        
    except Exception as e:
        print(f"  ✗ 오류: {e}")
        return None


def batch_insert_to_db(conn, data_list):
    """배치로 데이터 삽입 (20개씩)"""
    try:
        cursor = conn.cursor()
        
        # 테이블명과 컬럼명은 실제 DB 스키마에 맞게 수정하세요
        insert_query = """
            INSERT INTO snuh_diseases 
            (disease_name_kr, disease_name_eng, department, symptoms, url, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (url) DO UPDATE SET
                disease_name_kr = EXCLUDED.disease_name_kr,
                disease_name_eng = EXCLUDED.disease_name_eng,
                department = EXCLUDED.department,
                symptoms = EXCLUDED.symptoms,
                created_at = NOW()
        """
        
        # 데이터 준비
        values = [
            (
                data['disease_name_kr'],
                data['disease_name_eng'],
                data['department'],
                data['symptoms'],
                data['url'],
                datetime.now()
            )
            for data in data_list
        ]
        
        cursor.executemany(insert_query, values)
        conn.commit()
        cursor.close()
        
        print(f" → DB 저장: {len(data_list)}개")
        return True
        
    except Exception as e:
        print(f"\n  DB 배치 삽입 오류: {e}")
        conn.rollback()
        return False


def main():
    print("=" * 60)
    print("서울대학교병원 질병정보 크롤링 → DB 저장")
    print("=" * 60)
    
    # DB 연결
    conn = connect_db()
    if not conn:
        print("데이터베이스 연결 실패. 프로그램을 종료합니다.")
        return
    
    try:
        # Step 1: 질병 목록 수집
        print("\n[Step 1] 질병 목록 수집 중...")
        disease_list = get_all_disease_list(driver, max_pages=200)
        
        if not disease_list:
            print("\n질병 목록을 찾을 수 없습니다.")
            return
        
        print(f"\n총 {len(disease_list)}개 질병 발견")
        
        # Step 2: 상세 정보 크롤링 및 DB 저장
        print(f"\n[Step 2] 상세 정보 크롤링 및 DB 저장 시작...")
        print("-" * 60)
        
        batch_data = []
        total = len(disease_list)
        success_count = 0
        fail_count = 0
        
        for idx, disease in enumerate(disease_list, 1):
            print(f"[{idx}/{total}] {disease['disease_name'][:40]}...", end=" ")
            
            detail = get_disease_detail(driver, disease['url'], disease['disease_name'])
            
            if detail:
                batch_data.append(detail)
                print("✓", end="")
                success_count += 1
                
                # 20개마다 배치로 DB에 저장
                if len(batch_data) >= 20:
                    batch_insert_to_db(conn, batch_data)
                    batch_data = []  # 초기화
                
            else:
                print("✗")
                fail_count += 1
            
            time.sleep(1.5)
        
        # 남은 데이터 저장
        if batch_data:
            print()
            batch_insert_to_db(conn, batch_data)
        
        # Step 3: 결과 출력
        print("\n" + "=" * 60)
        print("[Step 3] 크롤링 완료")
        print("=" * 60)
        print(f"\n✅ 총 수집: {len(disease_list)}개")
        print(f"✅ 성공: {success_count}개")
        print(f"✗ 실패: {fail_count}개")
        print(f"✅ DB 저장 완료!")
        
    except Exception as e:
        print(f"\n오류: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()
        driver.quit()
        print("\n완료!")


if __name__ == "__main__":
    main()
