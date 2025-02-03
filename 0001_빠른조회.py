import requests
import json
import yaml
import pandas as pd
import time
from datetime import datetime

# Pandas 출력 옵션 설정
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.unicode.east_asian_width', True)  # 한글 width 조정

# 설정 파일 로드
with open('config.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)

APP_KEY = _cfg['APP_KEY']
APP_SECRET = _cfg['APP_SECRET']
ACCESS_TOKEN = ""
CANO = _cfg['CANO']
ACNT_PRDT_CD = _cfg['ACNT_PRDT_CD']
URL_BASE = _cfg['URL_BASE']

def get_access_token():
    """토큰 발급"""
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    return res.json().get("access_token", "")

# 조회할 종목 리스트
itm_no_dict = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "373220": "LG에너지솔루션",
    "207940": "삼성바이오로직스",
    "005380": "현대차",
    "000270": "기아",
    "068270": "셀트리온",
    "105560": "KB금융",
    "005935": "삼성전자우",
    "035420": "NAVER",
    "329180": "현대중공업",
    "055550": "신한지주",
    "012330": "현대모비스",
    "138040": "메리츠금융지주",
    "005490": "POSCO홀딩스",
    "028260": "삼성물산",
    "096770": "SK이노베이션",
    "012450": "한화에어로스페이스",
    "000810": "삼성화재",
    "032830": "삼성생명",
    "042660": "대우조선해양",
    "259960": "크래프톤",
    "086790": "하나금융지주",
    "010130": "고려아연",
    "035720": "카카오",
    "011200": "HMM",
    "051910": "LG화학",
    "009540": "한국조선해양",
    "034020": "두산에너빌리티",
    "006400": "삼성SDI",
    "267260": "현대일렉트릭",
    "033780": "KT&G",
    "066570": "LG전자",
    "015760": "한국전력",
    "402340": "SK스퀘어",
    "024110": "기업은행",
    "030200": "KT",
    "316140": "우리금융지주",
    "017670": "SK텔레콤",
    "003550": "LG",
    "010140": "삼성중공업",
    "086280": "현대글로비스",
    "003670": "포스코인터내셔널",
    "042700": "한미반도체",
    "034730": "SK",
    "000100": "유한양행",
    "323410": "카카오뱅크",
    "009150": "삼성전기",
    "352820": "하이브",
    "018260": "삼성에스디에스",
    "003490": "대한항공",
    "326030": "SK바이오팜",
    "443060": "카카오페이",
    "090430": "아모레퍼시픽",
    "047050": "대우건설",
    "010120": "LS ELECTRIC",
    "005830": "DB손해보험",
    "010950": "S-Oil",
    "267250": "현대중공업지주",
    "064350": "현대로템",
    "005387": "현대차2우B",
    "011790": "SKC",
    "021240": "웅진코웨이",
    "180640": "한진칼",
    "047810": "한국항공우주",
    "003230": "삼양식품",
    "161390": "한국타이어앤테크놀로지",
    "088980": "맥쿼리인프라",
    "079550": "LIG넥스원",
    "010620": "현대미포조선",
    "450080": "한화생명",
    "006800": "미래에셋증권",
    "029780": "삼성카드",
    "241560": "두산밥캣",
    "051900": "LG생활건강",
    "272210": "한화시스템",
    "005940": "NH투자증권",
    "000150": "두산",
    "034220": "LG디스플레이",
    "071050": "한국금융지주",
    "032640": "LG유플러스",
    "454910": "SK바이오사이언스",
    "298040": "효성첨단소재",
    "016360": "삼성증권",
    "271560": "오리온",
    "307950": "현대오토에버",
    "138930": "BNK금융지주",
    "175330": "JB금융지주",
    "005385": "현대차우",
    "302440": "SK바이오사이언스",
    "006260": "LS",
    "251270": "넷마블",
    "036570": "엔씨소프트",
    "097950": "CJ제일제당",
    "377300": "카카오게임즈",
    "035250": "강원랜드",
    "078930": "GS",
    "028050": "삼성엔지니어링",
    "011070": "LG이노텍",
    "000720": "현대건설",
    "462870": "LX세미콘",
    "009830": "한화솔루션",
    "066970": "엘앤에프",
    "039490": "키움증권",
    "036460": "한국가스공사",
    "128940": "한미약품",
    "004020": "현대제철",
    "018880": "한온시스템",
    "011780": "금호석유",
    "022100": "포스코 ICT",
    "001040": "CJ",
    "052690": "한전기술",
    "383220": "F&F",
    "007660": "이수페타시스",
    "001440": "대한전선",
    "011170": "롯데케미칼",
    "081660": "휠라홀딩스",
    "026960": "동서",
    "000880": "한화",
    "012750": "에스원",
    "001450": "현대해상",
    "002380": "KCC"
}

def get_stock_data(code):
    """현재가 및 상세 주식 정보 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/inquire-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "FHKST01010100"
    }
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": code,
    }
    
    res = requests.get(URL, headers=headers, params=params)
    response_json = res.json()
    
    if 'output' in response_json:
        return response_json["output"]
    else:
        print(f"Error: 종목 코드 {code}의 'output' 데이터 없음")
        return None

# API 토큰 발급
ACCESS_TOKEN = get_access_token()

# 데이터 컬럼 매핑
columns_map = {
    '순위': 'index',
    '종가': 'stck_prpr',
    '전일가': 'prdy_vrss',
    '등락률': 'prdy_ctrt',
    '거래대금': 'acml_tr_pbmn',
    '현재가': 'stck_oprc',
    '종목코드': 'code',
    '종목명': 'name'
}

def format_number(value, format_type='number'):
    """숫자 포맷팅 함수"""
    try:
        if format_type == 'price':
            return f"{int(value):,}"
        elif format_type == 'percentage':
            return f"{float(value):.2f}%"
        else:
            return f"{int(value):,}"
    except:
        return value

while True:
    print(f"\n🔄 주식 데이터 조회 시작... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print("+" + "-"*80 + "+")
    
    all_stock_data = []
    
    for idx, (code, name) in enumerate(itm_no_dict.items()):
        stock_data = get_stock_data(code=code)
        if stock_data:
            data = {
                'index': idx,
                'code': code,
                'name': name,
                'stck_prpr': format_number(stock_data['stck_prpr'], 'price'),
                'prdy_vrss': format_number(stock_data['prdy_vrss'], 'price'),
                'prdy_ctrt': format_number(stock_data['prdy_ctrt'], 'percentage'),
                'acml_tr_pbmn': format_number(stock_data['acml_tr_pbmn']),
                'stck_oprc': format_number(stock_data['stck_oprc'], 'price')
            }
            all_stock_data.append(data)
    
    if all_stock_data:
        df = pd.DataFrame(all_stock_data)
        # 컬럼 순서 지정
        df = df[['index', 'stck_prpr', 'prdy_vrss', 'prdy_ctrt', 'acml_tr_pbmn', 
                 'stck_oprc', 'code', 'name']]
        
        # 컬럼명 한글로 변경
        df.columns = ['순위', '종가', '전일가', '등락률', '거래대금', '현재가', '종목코드', '종목명']
        
        # 인덱스 재설정
        df.set_index('순위', inplace=True)
        
        # 테이블 출력
        print(df.to_string(justify='right'))
        print("+" + "-"*80 + "+")
    
    print(f"\n⏳ 10초 대기 중...")
    time.sleep(10)
