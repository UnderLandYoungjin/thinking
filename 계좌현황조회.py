import requests
import json
import yaml

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

def get_balance_inquire():
    """내 계좌 정보 조회"""
    PATH = "/uapi/domestic-stock/v1/trading/inquire-balance"
    URL = f"{URL_BASE}/{PATH}"
    
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "TTTC8434R"
    }
    
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "01",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    
    res = requests.get(URL, headers=headers, params=params)
    
    if res.status_code != 200:
        print("계좌 정보를 가져오는 중 오류 발생:", res.text)
        return {}, {}

    json_data = res.json()
    
    output1 = json_data.get('output1', [])
    output2 = json_data.get('output2', [])
    
    return output1, output2

# 🔹 API를 호출하여 내 계좌 정보 가져오기
ACCESS_TOKEN = get_access_token()
stocks, account_info = get_balance_inquire()

# 🔹 보유 주식 목록 출력
if not stocks:
    print("\n===== 보유한 종목이 없습니다. =====\n")
else:
    print("\n===== 내 계좌 보유 종목 =====\n")
    for stock in stocks:
        name = stock["prdt_name"]  # 종목명
        code = stock["pdno"]  # 종목 코드
        qty = int(stock["hldg_qty"])  # 보유 수량
        avg_price = float(stock["pchs_avg_pric"])  # 평균 매수가
        market_price = float(stock["prpr"])  # 현재가
        trade_type = stock["trad_dvsn_name"]  # 거래 방식 (현금/융자 등)
        profit_rate = float(stock["evlu_erng_rt"])  # 수익률

        print(f"종목명: {name} ({code})")
        print(f"보유 수량: {qty}주, 매수가: {avg_price:.2f}원, 현재가: {market_price:.2f}원")
        print(f"거래 방식: {trade_type}, 수익률: {profit_rate:.2f}%\n")

# 🔹 계좌 정보 출력
if not account_info:
    print("\n===== 계좌 정보를 가져올 수 없습니다. =====\n")
else:
    print("\n===== 내 계좌 현황 =====\n")
    for acc in account_info:
        total_assets = int(acc["tot_evlu_amt"])  # 총 자산 평가금액
        total_stock_value = int(acc["scts_evlu_amt"])  # 보유 주식 평가금액
        total_profit = int(acc["evlu_pfls_smtl_amt"])  # 총 손익
        cash_balance = int(acc["dnca_tot_amt"])  # 예수금
        prev_assets = int(acc["bfdy_tot_asst_evlu_amt"])  # 전일 총 자산 평가금액
        assets_diff = int(acc["asst_icdc_amt"])  # 자산 변화량

        print(f"총 자산 평가금액: {total_assets:,} 원")
        print(f"보유 주식 평가금액: {total_stock_value:,} 원")
        print(f"총 손익: {total_profit:,} 원")
        print(f"예수금: {cash_balance:,} 원")
        print(f"전일 대비 자산 변화: {assets_diff:,} 원\n")
