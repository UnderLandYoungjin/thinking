import requests
import json
import datetime
import time
import yaml

# 설정 파일(config.yaml)에서 API 사용에 필요한 설정 값을 불러온다.
with open('config.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)
APP_KEY = _cfg['APP_KEY']
APP_SECRET = _cfg['APP_SECRET']
ACCESS_TOKEN = ""  # 초기에는 빈 문자열로 설정한다.
CANO = _cfg['CANO']  # 계좌번호
ACNT_PRDT_CD = _cfg['ACNT_PRDT_CD']  # 계좌 상품 코드
URL_BASE = _cfg['URL_BASE']  # API 기본 URL

def get_access_token():
    """
    액세스 토큰을 발급받는 함수.
    API 엔드포인트에 POST 요청을 보내어 액세스 토큰을 받아온다.
    """
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    PATH = "oauth2/tokenP"  # 토큰 발급을 위한 경로
    URL = f"{URL_BASE}/{PATH}"  # 전체 URL 생성
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    ACCESS_TOKEN = res.json()["access_token"]  # JSON 응답에서 액세스 토큰 추출
    return ACCESS_TOKEN

def hashkey(datas):
    """
    주문 데이터에 대한 해시키(암호화)를 생성하는 함수.
    API에서 요구하는 해시키를 받아오기 위해 POST 요청을 보낸다.
    """
    PATH = "uapi/hashkey"
    URL = f"{URL_BASE}/{PATH}"
    headers = {
        'content-Type': 'application/json',
        'appKey': APP_KEY,
        'appSecret': APP_SECRET,
    }
    res = requests.post(URL, headers=headers, data=json.dumps(datas))
    hashkey = res.json()["HASH"]  # JSON 응답에서 HASH 값을 추출
    return hashkey

def get_current_price(code="005930"):
    """
    주어진 종목코드에 대해 현재가, 시초가, 최고가, 전일 대비 가격 정보를 조회하는 함수.
    API 엔드포인트에 GET 요청을 보내고, 결과를 딕셔너리 형태로 반환한다.
    """
    PATH = "uapi/domestic-stock/v1/quotations/inquire-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "FHKST01010100"  # 거래 요청 ID
    }
    params = {
        "fid_cond_mrkt_div_code": "J",  # 시장 구분 코드
        "fid_input_iscd": code,  # 종목 코드
        "output_table_cols": "stck_prpr,stck_oprc"  # 반환할 데이터 컬럼 지정
    }
    res = requests.get(URL, headers=headers, params=params)
    json_data = res.json()
    # API 응답의 output 부분에서 데이터를 추출하여 딕셔너리로 반환한다.
    return {
        '현재가': int(json_data['output']['stck_prpr']),
        '시초가': json_data['output']['stck_oprc'],
        '최고가': json_data['output']['stck_hgpr'],
        '전일대비': json_data['output']['prdy_vrss']
    }

def get_daily_price(code="005930"):
    """
    주어진 종목코드에 대해 일일 가격 정보를 조회하는 함수.
    주로 종목명을 반환한다.
    """
    PATH = "/uapi/domestic-stock/v1/quotations/inquire-daily-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "CTPF1002R"  # 거래 요청 ID
    }
    params = {
        "PRDT_TYPE_CD": "300",  # 상품 타입 코드
        "PDNO": code,  # 종목 코드
    }
    res = requests.get(URL, headers=headers, params=params)
    st_name = str(res.json()['output']['prdt_name'])  # 종목명 추출
    return st_name

def buy(code="005930", qty="1"):
    """
    주식 시장가 매수를 실행하는 함수.
    주문 데이터를 구성한 후 API에 POST 요청을 보내 매수 주문을 실행한다.
    """
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    data = {
        "CANO": CANO,  # 계좌 번호
        "ACNT_PRDT_CD": ACNT_PRDT_CD,  # 계좌 상품 코드
        "PDNO": code,  # 종목 코드
        "ORD_DVSN": "01",  # 주문 구분 (시장가)
        "ORD_QTY": str(int(qty)),  # 주문 수량
        "ORD_UNPR": "0",  # 주문 가격 (시장가이므로 0)
    }
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "TTTC0802U",  # 매수 거래 요청 ID
        "custtype": "P",  # 고객 타입
        "hashkey": hashkey(data)  # 데이터 암호화 해시키
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    # API 응답의 rt_cd가 '0'이면 주문 성공, 아니면 주문 실패
    if res.json()['rt_cd'] == '0':
        print(f"[해당 조건으로 매수 성공 하였다.]{str(res.json())}")
        return True
    else:
        print(f"[매수 실패]{str(res.json())}")
        return False

def sell(code="005930", qty="1"):
    """
    주식 시장가 매도를 실행하는 함수.
    매수와 유사한 방식으로 주문 데이터를 구성하고 API에 POST 요청을 보낸다.
    """
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    data = {
        "CANO": CANO,  # 계좌 번호
        "ACNT_PRDT_CD": ACNT_PRDT_CD,  # 계좌 상품 코드
        "PDNO": code,  # 종목 코드
        "ORD_DVSN": "01",  # 주문 구분 (시장가)
        "ORD_QTY": qty,  # 주문 수량
        "ORD_UNPR": "0",  # 주문 가격 (시장가이므로 0)
    }
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "TTTC0801U",  # 매도 거래 요청 ID
        "custtype": "P",  # 고객 타입
        "hashkey": hashkey(data)  # 데이터 암호화 해시키
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    # API 응답의 rt_cd가 '0'이면 주문 성공, 아니면 주문 실패
    if res.json()['rt_cd'] == '0':
        print(f"[해당 조건으로 매도에 성공 하였다.]{str(res.json())}")
        return True
    else:
        print(f"[매도 실패]{str(res.json())}")
        return False

def get_balance_inquire(code="005930"):
    """
    계좌의 보유 종목 정보를 조회하는 함수.
    API를 통해 조회한 보유 종목 리스트에서 보유 수량이 0보다 큰 종목들을
    종목 코드(key)와 종목명, 보유수량, 매수가, 현재가 정보를 값으로 하는 딕셔너리로 반환한다.
    """
    PATH = "/uapi/domestic-stock/v1/trading/inquire-balance"
    URL = f"{URL_BASE}/{PATH}"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "TTTC8434R"  # 잔고 조회 거래 요청 ID
    }
    params = {
        "CANO": CANO,  # 계좌 번호
        "ACNT_PRDT_CD": ACNT_PRDT_CD,  # 계좌 상품 코드
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",  # 조회 구분
        "UNPR_DVSN": "01",  # 평가 방식
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "01",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    res = requests.get(URL, headers=headers, params=params)
    # API 응답에서 보유 종목 리스트를 추출한다.
    stock_list = res.json()['output1']
    stock_dict = {}

    # 보유 수량이 0보다 큰 종목만을 선택하여 딕셔너리에 저장한다.
    for stock in stock_list:
        if int(stock['hldg_qty']) > 0:
            # 종목코드를 key로 하여 종목명, 보유수량, 매수가, 현재가 정보를 저장한다.
            stock_dict[stock['pdno']] = [
                stock['prdt_name'],
                stock['hldg_qty'],
                stock['pchs_avg_pric'],
                stock['prpr']
            ]
    return stock_dict

# ACCESS_TOKEN을 발급받아 전역 변수에 저장한다.
ACCESS_TOKEN = get_access_token()
# ACCESS_TOKEN 발급 이후

# 보유 종목은 한 번만 조회하여 변수에 저장한다.
my_poket_all = get_balance_inquire()

while True:

    symbol_list = ['036540', '115450', '287410', '025320', '015750', '003380', '041190', '007390', '046890', '335890',
    '025980', '006730', '215600', '091700', '297890', '151860', '092040', '256840', '252990', '005160',
    '051980', '243840', '299900', '099430', '031330', '101730', '148150', '050890', '029960', '059090',
    '027360', '319400', '077360', '298830', '025770', '036200', '041020', '136480', '061970', '095700',
    '441270', '064800', '038500', '108230', '235980', '060150', '024850', '278650', '056080', '078150',
    '036620', '100790', '041960', '058820', '217270', '060370', '094480', '047310', '078020', '211050',
    '307750', '030530', '023410', '214680', '270520', '064260', '314930', '204620', '083650', '101670',
    '122990', '334970', '179290', '036030', '086890', '144960', '093640', '032620', '034810', '217820',
    '013120', '078160', '200470', '048530', '048870', '043370', '086980', '109610', '017890', '083790',
    '297090', '126600', '042370', '036890', '060570', '207760', '371950', '045390', '084990', '122450',
    '472850', '035810', '123040', '084650', '289220', '264850', '063570', '054210', '046440', '067080',
    '048550', '321550', '123410', '053300', '131370', '066790', '045970', '068930', '005860', '085670',
    '110790', '225530', '194700', '011040', '060590', '039980', '019210', '090710', '006620', '073570',
    '037070', '038110', '038540', '205100', '234690', '168360', '156100', '206560', '220260', '043610',
    '290550', '246710', '382800', '377450', '033290', '064820', '183490', '067000', '419050', '203650',
    '418420', '125210', '013990', '388050', '100130', '023600', '408900', '203400', '121440', '040300',
    '119830', '067990', '376190', '030960', '357230', '044340', '417500', '046210', '099440', '315640',
    '040910', '396470', '356680', '063170', '109740', '006910', '362320', '049720', '029480', '149980',
    '090470', '013310', '068790', '131400', '226330', '073010', '014940', '277880', '037460', '039560',
    '089850', '072770', '337930', '348150', '452190', '305090', '261200', '054620', '088800', '228850',
    '340360', '180400', '217730', '393210', '353810', '263600', '012700', '007330', '082800', '293780',
    '021080', '140070', '137950', '065450', '039340', '338840', '090850', '251630', '306620', '162300',
    '082850', '391710', '368770', '042510', '300120', '164060', '294090', '310200', '261780', '067900',
    '005710', '256940', '332570', '259630', '066700', '048910', '054050', '124560', '060310', '206400',
    '066980', '147830', '366030', '035610', '071200', '053580', '119850', '267320', '026150', '061040',
    '080580', '027050', '036710', '347890', '052330', '105550', '291230', '082210', '208370', '105330',
    '159580', '128660', '014470', '100700', '294630', '216050', '104540', '053700', '041440', '095190',
    '115180', '065130', '038460', '104620', '042500', '102370', '226340', '051160', '054780', '236810',
    '317770', '066590', '186230', '357580', '417790', '443250', '052710', '199550', '054670', '053280',
    '123420', '041920', '027830', '078140', '038680', '049520', '041910', '053450', '041930', '007820',
    '446540', '382480', '250060', '234300', '142210', '067370', '033230', '092460', '260930', '452280',
    '141000', '170030', '033310', '407400', '289080', '115160', '330350', '232680', '040420', '086710',
    '093920', '067570', '052790', '054800', '058630', '203690', '088130', '307930', '208140', '140430',
    '403490', '094970', '072020', '361570', '173130', '323280', '321370', '093190', '054040', '064240',
    '389140', '314130', '241770', '069540', '263800', '352090', '059210', '234920', '131030', '024910',
    '094850', '271830', '053050', '241520', '071670', '383930', '036120', '078890', '032850', '347000',
    '317830', '142760', '001540', '126880', '011560', '396300', '309960', '368600', '043650', '153710',
    '089790', '284620', '155650', '237820', '087260', '333430', '008830', '053260', '189980', '226400',
    '187420', '241690', '238090', '066910', '218150', '277070', '006140', '024880', '377030', '122310',
    '318020', '158430', '253840', '054920', '160550', '127980', '265560', '222040', '010470', '352910',
    '066670', '086040', '223250', '009780', '347770', '036640', '048430', '308080', '217500', '037440',
    '064480', '215100', '039860', '011320', '347740', '288980', '352700', '376930', '080000', '066310',
    '098120', '039240', '060230', '389470', '053980', '059270', '041520', '333620', '105740', '351330',
    '142280', '020710', '302550', '219420', '123570', '168330', '171010', '330730', '246720', '025550',
    '115500', '095270', '012790', '024840', '004650', '136410', '039290', '185490', '201490', '002800',
    '064090', '017480', '032540', '303530', '263050', '388790', '220180', '270870', '163730', '322180',
    '365330', '314140', '301300', '033320', '033540', '212560', '049480', '068050', '274400', '101330',
    '100590', '038070', '321260', '065950', '290740', '101170', '327260', '263700', '064520', '225220',
    '440290', '041460', '150900', '053290', '037370', '189690', '038870', '242040', '015710', '239340',
    '290720', '115440', '039830', '053270', '094840', '214270', '046120', '434480', '072990', '307180',
    '092300', '101390', '317850', '147760', '129920', '024740', '265740', '051490', '348030', '122690',
    '052220', '187660', '276040', '306040', '072470', '060850', '419120', '294140', '137080', '438700',
    '238490', '053350', '103840', '067920', '081150', '376180', '032940', '134580', '024950', '017510',
    '254120', '222110', '320000', '317690', '050960', '223310', '139670', '014570', '057030', '016100',
    '088910', '376980', '087600', '355150', '094940', '044960', '004780', '033200', '318000', '148930',
    '353590', '413640', '258610', '128540', '405920', '452300', '038010', '238120', '053160', '066130',
    '106080', '104200', '039420', '004590', '037350', '097870', '377220', '019540', '033560', '088280',
    '138070', '099390', '075970', '068100', '056700', '367000', '340810', '285800', '204020', '056360',
    '440320', '198080', '019990', '298060', '417180', '309930', '051380', '033790', '073110', '377330',
    '014970', '039010', '263810', '304840', '060540', '110020', '100660', '197140', '101000', '079000',
    '052860', '037030', '133750', '013810', '024120', '080010', '091590', '048770', '127120', '054540',
    '001840', '039610', '083550', '354200', '290520', '023770', '069920', '288330', '080520', '065370',
    '405000', '052600', '031310', '318010', '299660', '199730', '317120', '222980', '008370', '189860',
    '045060', '195500', '069410', '115610', '177830', '267790', '419540', '076080', '187270', '052460',
    '378800', '058450', '101240', '005670', '291650', '080720', '228340', '289010', '340930', '362990',
    '002290', '085910', '357880', '046310', '198940', '045340', '290270', '187220', '203450', '351320',
    '130500', '229000', '072950', '237750', '286750', '032750', '238200', '131220', '221800', '263020',
    '021650', '058110', '019770', '051390', '065570', '114450', '363250', '025880', '067010', '040160',
    '247660', '089140', '119500', '036480', '089230', '312610', '024940', '331380', '006920', '318160',
    '079170', '099410', '368970', '014100', '296640', '290560', '081580', '075130', '059100', '048470',
    '208350', '045300', '012620', '093380', '035460', '192390', '291810', '071850', '017000', '086060',
    '025870', '035200', '262840', '232830', '215480', '317530', '073190', '103230', '067730', '060480',
    '154030', '063760', '344860', '130740', '224060', '020400', '275630', '039740', '361670', '191410',
    '070300', '078860', '062970', '096870']
    print(f"\n{'='*50}\n종목 탐색을 시작한다.\n{'='*50}\n")
    now = datetime.datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
     
    # 거래 시간대를 설정한다.
    t_09_00 = now.replace(hour=9, minute=0, second=0, microsecond=0)
    t_09_30 = now.replace(hour=9, minute=30, second=0, microsecond=0)
    t_10_00 = now.replace(hour=10, minute=0, second=0, microsecond=0)
    t_10_30 = now.replace(hour=10, minute=30, second=0, microsecond=0)
    t_11_00 = now.replace(hour=11, minute=0, second=0, microsecond=0)
    t_11_30 = now.replace(hour=11, minute=30, second=0, microsecond=0)
    t_12_00 = now.replace(hour=12, minute=0, second=0, microsecond=0)
    t_12_30 = now.replace(hour=12, minute=30, second=0, microsecond=0)
    t_13_00 = now.replace(hour=13, minute=0, second=0, microsecond=0)
    t_13_30 = now.replace(hour=13, minute=30, second=0, microsecond=0)
    t_14_00 = now.replace(hour=14, minute=0, second=0, microsecond=0)
    t_14_30 = now.replace(hour=14, minute=30, second=0, microsecond=0)
    t_15_00 = now.replace(hour=15, minute=0, second=0, microsecond=0)
    t_15_30 = now.replace(hour=15, minute=30, second=0, microsecond=0)
 
    print(f"\n{'='*50}\n현재시간 = ({formatted_time})\n{'='*50}\n")
    time.sleep(1)
     
    count_condition = 0
 
    for symbol in symbol_list:
        try:
            # 각 종목에 대해 현재가와 일일 가격 정보를 조회한다.
            current_price = get_current_price(symbol)
            st_name = get_daily_price(symbol)
            
            now_y = int(current_price['전일대비'])
            y_end_price = current_price['현재가'] - now_y
            diff_a = ((current_price['현재가'] / y_end_price) - 1) * 100
 
            print(f"코드: {symbol}, 종목명: {st_name}, 현재가 정보: {current_price}, "
                  f"현재가-전일대비=전일종가: {y_end_price}, 등락율={diff_a:.3f}%")
 
            # 보유 여부 확인: 이미 보유중이면 해당 종목만 건너뛴다.
            if symbol in my_poket_all:
                print(f"{'='*50}\n{st_name}은(는) 이미 보유 중이므로 매수를 건너뛴다.\n{'='*50}")
                continue  # 이 symbol에 대해서는 매수 로직 실행하지 않고 다음 symbol로 넘어간다.
 
            # 매수 조건 검사: 장중(오후 13시 30분~15시 30분)이며, 등락률 조건에 부합하면 매수 시도
            if now:
                if 0.5 <= diff_a <= 0.9:
                    print(f"{'='*50}\n{st_name}이(가) 조건에 부합하여 매수를 시도한다.\n{'='*50}")
                    count_condition += 1
                    print(f"조건에 부합하는 종목을 {count_condition}개 찾았다.")
                    buy(symbol, 1)
                else:
                    print("조건에 부합하지 않으므로 넘어간다.")
            else:
                print(f"{'='*50}\n장이 열리지 않아 구매는 진행하지 않고 모니터링만 수행한다.\n{'='*50}")
 
        except KeyError as e:
            print(f"키 에러 발생: {e}")
        except ValueError as e:
            print(f"값 에러 발생: {e}")
        except Exception as e:
            print(f"에러 발생: {e}")
 
    print(f"\n{'='*50}\n종목 전체 탐색을 완료하였다.\n{'='*50}\n")
     
    time.sleep(1)
 
    # 매도 조건 검사 시 보유 종목 정보는 my_poket_all를 사용한다.
    for key in list(my_poket_all.keys()):
        try:
            values = my_poket_all[key]
            name = str(values[0])      # 종목명
            qty = int(values[1])       # 보유 수량
            num1 = float(values[2])    # 매수가
            num2 = float(values[3])    # 현재가
            margin_rate = ((num2 / num1) - 1) * 100  # 수익률
 
            print(f"({key}): ({name})의 수익률은 {margin_rate:.3f}%이다.")
            if margin_rate >= 2.1:
                print(f"{name}이(가) 이익이 발생하여 매도를 시도한다.")
                sell(key, qty)
            elif margin_rate <= -0.7:
                print(f"{name}이(가) 손실이 발생하여 손절 매도를 시도한다.")
                sell(key, qty)
            else:
                print("매도 조건에 부합하지 않으므로 넘어간다.")
 
        except KeyError as e:
            print(f"키 에러 발생: {e}")
        except ValueError as e:
            print(f"값 에러 발생: {e}")
        except Exception as e:
            print(f"에러 발생: {e}")
 
    print(f"\n{'='*50}\n보유 종목에 대한 조건 확인을 완료하였다.\n{'='*50}\n")
