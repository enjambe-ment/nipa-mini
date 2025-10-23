import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument('--headless')  # 백그라운드 실행
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

# 웹드라이버 초기화
driver = webdriver.Chrome(options=chrome_options)

def get_disease_list_from_page(driver, page_index):
    """특정 페이지에서 질병 목록 추출"""
    disease_data = []
    
    try:
        url = f"https://www.amc.seoul.kr/asan/healthinfo/disease/diseaseList.do?pageIndex={page_index}&partId=&diseaseKindId=&searchKeyword="
        
        print(f"[페이지 {page_index}] 로딩 중...")
        driver.get(url)
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # 질병 링크 찾기 - diseaseDetail.do 링크
        disease_links = soup.find_all('a', href=lambda x: x and 'diseaseDetail.do' in x)
        
        if not disease_links:
            print(f"[페이지 {page_index}] 질병 목록을 찾을 수 없습니다.")
            return [], False
        
        print(f"[페이지 {page_index}] {len(disease_links)}개 질병 발견")
        
        for link in disease_links:
            href = link.get('href', '')
            disease_name = link.get_text(strip=True)
            
            if disease_name:
                # URL 정리
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('./'):
                    full_url = f"https://www.amc.seoul.kr/asan/healthinfo/disease/{href[2:]}"
                elif href.startswith('/'):
                    full_url = f"https://www.amc.seoul.kr{href}"
                else:
                    full_url = f"https://www.amc.seoul.kr/asan/healthinfo/disease/{href}"
                
                disease_data.append({
                    'disease_name': disease_name,
                    'url': full_url,
                    'page': page_index
                })
        
        return disease_data, len(disease_data) > 0
        
    except Exception as e:
        print(f"[페이지 {page_index}] 오류: {e}")
        return [], False

def get_all_disease_list(driver, max_pages=200):
    """모든 페이지에서 질병 목록 추출"""
    all_diseases = []
    consecutive_empty = 0
    
    print("=" * 60)
    print("서울아산병원 질환백과 크롤링 시작")
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
        
        # 질병명 추출 (한글명, 영문명)
        disease_name_kr = disease_name
        disease_name_eng = ""
        
        # 질병명이 "질병명(영문명)" 형태일 경우 분리
        if '(' in disease_name and ')' in disease_name:
            disease_name_kr = disease_name.split('(')[0].strip()
            disease_name_eng = disease_name.split('(')[1].split(')')[0].strip()
        
        # 증상 추출
        symptoms = []
        symptom_section = soup.find('dt', string='증상')
        if symptom_section:
            symptom_dd = symptom_section.find_next_sibling('dd')
            if symptom_dd:
                symptom_items = symptom_dd.find_all('li')
                if symptom_items:
                    symptoms = [item.get_text(strip=True) for item in symptom_items]
                else:
                    symptoms_text = symptom_dd.get_text(strip=True)
                    if symptoms_text:
                        symptoms = [symptoms_text]
        
        symptoms_str = ', '.join(symptoms) if symptoms else "정보 없음"
        
        # 진료과 추출
        departments = []
        dept_section = soup.find('dt', string='진료과')
        if dept_section:
            dept_dd = dept_section.find_next_sibling('dd')
            if dept_dd:
                dept_links = dept_dd.find_all('a')
                if dept_links:
                    departments = [link.get_text(strip=True) for link in dept_links]
                else:
                    dept_text = dept_dd.get_text(strip=True)
                    if dept_text:
                        departments = [dept_text]
        
        departments_str = ', '.join(departments) if departments else "정보 없음"
        
        # 동의어 추출
        synonyms = []
        synonym_section = soup.find('dt', string='동의어')
        if synonym_section:
            synonym_dd = synonym_section.find_next_sibling('dd')
            if synonym_dd:
                synonym_text = synonym_dd.get_text(strip=True)
                if synonym_text:
                    # 쉼표나 공백으로 분리
                    synonyms = [s.strip() for s in synonym_text.replace(',', ' ').split() if s.strip()]
        
        synonyms_str = ', '.join(synonyms) if synonyms else "정보 없음"
        
        # 관련질환 추출
        related_diseases = []
        related_section = soup.find('dt', string='관련질환')
        if related_section:
            related_dd = related_section.find_next_sibling('dd')
            if related_dd:
                related_links = related_dd.find_all('a')
                if related_links:
                    related_diseases = [link.get_text(strip=True) for link in related_links]
                else:
                    related_text = related_dd.get_text(strip=True)
                    if related_text:
                        related_diseases = [related_text]
        
        related_diseases_str = ', '.join(related_diseases) if related_diseases else "정보 없음"
        
        result = {
            'disease_name_kr': disease_name_kr,
            'disease_name_eng': disease_name_eng,
            'symptoms': symptoms_str,
            'department': departments_str,
            'synonyms': synonyms_str,
            'related_diseases': related_diseases_str,
            'url': url
        }
        
        return result
        
    except Exception as e:
        print(f"  ✗ 오류: {e}")
        return None

def save_to_csv(data_list, filename):
    """크롤링 데이터를 CSV 파일로 저장"""
    try:
        df = pd.DataFrame(data_list)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n✓ '{filename}' 저장 완료")
        print(f"총 {len(data_list)}개 질병 정보")
        
        print(f"\n[통계]")
        print(f"- 증상 정보: {len(df[df['symptoms'] != '정보 없음'])}개")
        print(f"- 진료과 정보: {len(df[df['department'] != '정보 없음'])}개")
        print(f"- 동의어: {len(df[df['synonyms'] != '정보 없음'])}개")
        print(f"- 관련질환: {len(df[df['related_diseases'] != '정보 없음'])}개")
        print(f"- 영문명: {len(df[df['disease_name_eng'] != ''])}개")
        
        # 샘플 출력
        print(f"\n[데이터 샘플]")
        print(df[['disease_name_kr', 'symptoms', 'department']].head())
        
    except Exception as e:
        print(f"저장 오류: {e}")

def save_progress(data_list):
    """진행 상황 백업"""
    try:
        if len(data_list) > 0:
            df = pd.DataFrame(data_list)
            df.to_csv('amc_progress.csv', index=False, encoding='utf-8-sig')
    except:
        pass

def main():
    print("=" * 60)
    print("서울아산병원 질환백과 크롤링")
    print("=" * 60)
    
    try:
        # Step 1: 질병 목록 수집
        print("\n[Step 1] 질병 목록 수집 중...")
        disease_list = get_all_disease_list(driver, max_pages=200)
        
        if not disease_list:
            print("\n질병 목록을 찾을 수 없습니다.")
            return
        
        print(f"\n총 {len(disease_list)}개 질병 발견")
        print("\n[샘플 10개]")
        for i, d in enumerate(disease_list[:10], 1):
            print(f"  {i}. {d['disease_name']}")
        
        # Step 2: 상세 정보 크롤링
        print(f"\n[Step 2] 상세 정보 크롤링 시작...")
        print(f"총 {len(disease_list)}개 질병 크롤링 예정")
        print("-" * 60)
        
        all_data = []
        total = len(disease_list)
        
        for idx, disease in enumerate(disease_list, 1):
            print(f"[{idx}/{total}] {disease['disease_name'][:40]}...", end=" ")
            
            detail = get_disease_detail(driver, disease['url'], disease['disease_name'])
            if detail:
                all_data.append(detail)
                print("✓")
            else:
                print("✗")
            
            # 20개마다 백업
            if idx % 20 == 0:
                save_progress(all_data)
                print(f"  [백업: {len(all_data)}개]")
            
            time.sleep(1.5)
        
        # Step 3: 최종 저장
        print("\n" + "=" * 60)
        print("[Step 3] 최종 저장")
        print("=" * 60)
        
        if all_data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'amc_diseases_{timestamp}.csv'
            save_to_csv(all_data, filename)
            print(f"\n✅ 크롤링 완료!")
            print(f"수집: {len(disease_list)}개 → 저장: {len(all_data)}개")
        else:
            print("저장할 데이터가 없습니다.")
        
    except Exception as e:
        print(f"\n오류: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()
        print("\n완료!")

if __name__ == "__main__":
    main()
