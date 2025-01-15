from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import csv
from datetime import datetime

class NaverNewsCrawler:
    def __init__(self):
        self.headers_list = ["번호", "제목", "언론사", "발행시간", "링크"]
        self.chrome_options = Options()
        self.chrome_options.add_argument('--start-maximized')
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        self.scroll_pause_time = 1  # 스크롤 대기 시간 (초)
        self.max_scroll_attempts = 100  # 최대 스크롤 시도 횟수

    def setup_driver(self):
        driver = webdriver.Chrome(options=self.chrome_options)
        return driver

    def get_article_info(self, article, idx):
        try:
            title_elem = article.find_element(By.CSS_SELECTOR, "a.news_tit")
            title = title_elem.get_attribute("title")
            link = title_elem.get_attribute("href")
            press = article.find_element(By.CSS_SELECTOR, "a.press").text
            pub_time = article.find_element(By.CSS_SELECTOR, "span.info").text
            return {"번호": idx, "제목": title, "언론사": press, "발행시간": pub_time, "링크": link}
        except Exception as e:
            print(f"기사 정보 추출 실패 (번호: {idx}): {str(e)}")
            return None

    def crawl(self, keyword="python", save_interval=20):
        all_articles = []
        driver = self.setup_driver()
        unique_links = set()
        idx = 1  # 기사 번호 초기화

        try:
            driver.get(f"https://search.naver.com/search.naver?where=news&query={keyword}")
            time.sleep(2)

            last_height = driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0

            while scroll_attempts < self.max_scroll_attempts:
                print(f"스크롤링 시도: {scroll_attempts + 1}/{self.max_scroll_attempts}")

                # 뉴스 기사 추출
                articles = driver.find_elements(By.CSS_SELECTOR, "div.news_wrap.api_ani_send, div.news_area")
                for article in articles:
                    article_info = self.get_article_info(article, idx)
                    if article_info and article_info["링크"] not in unique_links:
                        unique_links.add(article_info["링크"])
                        all_articles.append([
                            article_info[header] for header in self.headers_list
                        ])
                        print(f"기사 {idx} 수집 완료: {article_info['제목'][:30]}...")
                        idx += 1

                        # 저장 주기에 따라 중간 저장
                        if len(all_articles) % save_interval == 0:
                            self.save_to_csv(all_articles, filename=f"temp_{keyword}.csv")
                            print(f"{save_interval}개의 기사 중간 저장 완료.")

                # 스크롤 내려서 더 많은 뉴스 로드
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(self.scroll_pause_time)

                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print("더 이상 새로운 기사가 없습니다. 크롤링 종료.")
                    break
                last_height = new_height
                scroll_attempts += 1

        except Exception as e:
            print(f"크롤링 중 오류 발생: {str(e)}")
        finally:
            driver.quit()

        return all_articles

    def save_to_csv(self, articles, filename=None):
        """크롤링 결과를 CSV 파일로 저장"""
        if not filename:
            filename = f"naver_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        try:
            with open(filename, mode="w", encoding="utf-8-sig", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(self.headers_list)
                writer.writerows(articles)
            print(f"저장 완료: {filename}")
            return True
        except Exception as e:
            print(f"파일 저장 중 오류 발생: {str(e)}")
            return False

def main():
    crawler = NaverNewsCrawler()
    articles = crawler.crawl(keyword="테스트", save_interval=50)  # 50개마다 저장
    if articles:
        crawler.save_to_csv(articles)

if __name__ == "__main__":
    main()
