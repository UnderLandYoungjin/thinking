#예외처리를 위해 에러 이후에 +2한후 부터 진행 시킬수 있는 last어쩌구 하는 코드를 추가 시켜 놓았었는데, 왠지 필요 없는것 같아 지우고 실행 시켜도 되어서, 지움!
#5월 5일 새벽 0시 58분 시간에 따른 구매 전략 변화를 업로드
#5월4일 8시17분 finally에 time.sl\sleep(1)되었던거 pass로 변경하면서 속도를 빠르게 업그레이드 함
#2024년 5월 4일 오후 7시 37분 기준으로 내 계좌의 종목을 가지고 오는 부분에서 에러가 날수 있는 부분을 try , except문으로 처리하는 코드를 추가 하였음

import requests
import json
import datetime
import time
import yaml



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
    headers = {"content-type":"application/json"}
    body = {"grant_type":"client_credentials",
    "appkey":APP_KEY, 
    "appsecret":APP_SECRET}
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    ACCESS_TOKEN = res.json()["access_token"]
    return ACCESS_TOKEN
    
def hashkey(datas):
    """암호화"""
    PATH = "uapi/hashkey"
    URL = f"{URL_BASE}/{PATH}"
    headers = {
    'content-Type' : 'application/json',
    'appKey' : APP_KEY,
    'appSecret' : APP_SECRET,
    }
    res = requests.post(URL, headers=headers, data=json.dumps(datas))
    hashkey = res.json()["HASH"]
    return hashkey

def get_current_price(code="005930"):
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
        "output_table_cols": "stck_prpr,stck_oprc" 
    }
    res = requests.get(URL, headers=headers, params=params)
    json_data = res.json()
    return {
        '현재가': int(json_data['output']['stck_prpr']),
        '시초가': json_data['output']['stck_oprc'],
        '최고가': json_data['output']['stck_hgpr'],
        '전일대비': json_data['output']['prdy_vrss']
    }

def get_daily_price(code="005930"):
    PATH = "/uapi/domestic-stock/v1/quotations/inquire-daily-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "CTPF1002R"
    }
    params = {
        "PRDT_TYPE_CD": "300",
        "PDNO": code,
    }
    res = requests.get(URL, headers=headers, params=params)
    st_name = str(res.json()['output']['prdt_name'])
    return st_name

def buy(code="005930", qty="1"):
    """주식 시장가 매수"""  
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "01",
        "ORD_QTY": str(int(qty)),
        "ORD_UNPR": "0",
    }
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC0802U",
        "custtype":"P",
        "hashkey" : hashkey(data)
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    if res.json()['rt_cd'] == '0':
        print(f"[해당 조건으로 매수 성공 하였습니다.]{str(res.json())}")
        return True
    else:
        print(f"[매수 실패]{str(res.json())}")
        return False

def sell(code="005930", qty="1"):
    """"""
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "01",
        "ORD_QTY": qty,
        "ORD_UNPR": "0",
    }
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC0801U",
        "custtype":"P",
        "hashkey" : hashkey(data)
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    if res.json()['rt_cd'] == '0':
        print(f"[해당 조건으로 매도에 성공 하였습니다.]{str(res.json())}")
        return True
    else:
        print(f"[매도 실패]{str(res.json())}")
        return False

def get_balance_inquire(code="005930"):
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
    #json_data = res.json()
    #2024년5월2일 목요일 오후 1시5분 기준으로 아래 부분이 잘 풀리지 않는다...list indices must be integers of slices, not str이라고 하는데....

    stock_list = res.json()['output1']
    stock_dict = {}

    for stock in stock_list:
        if int(stock['hldg_qty']) > 0:#수량이 0개 초과 하였을 경우에(1개 이상 무조건 보유하고 있는 종목)
            stock_dict[stock['pdno']] = [stock['prdt_name'], stock['hldg_qty'], stock['pchs_avg_pric'], stock['prpr']] #pdno를 key로 하여 hldg_qty, pchs_avg_pric 값을 추가 하였음
            #print(f"{stock['prdt_name']}({stock['pdno']}): {stock['hldg_qty']}주{stock['pchs_avg_pric']}")
    return stock_dict


ACCESS_TOKEN = get_access_token()
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
    '070300', '078860', '062970', '096870'
]
    print(f"\n{'='*50}\n종목 탐색을 시작합니다.\n{'='*50}\n")
    now = datetime.datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    
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
            current_price = get_current_price(symbol)
            st_name = get_daily_price(symbol)
            my_poket = get_balance_inquire(symbol)
            
            now_y = int(current_price['전일대비'])  # 전일대비가 str로 넘어와서 int로 변환
            y_end_price = current_price['현재가'] - now_y  # 현재가에서 전일대비를 빼어서 어제 종가 확인
            diff_a = ((current_price['현재가'] / y_end_price) - 1) * 100  # 전일 종가 대비 현재 등락률

            print(f"코드: {symbol}, 종목명: {st_name}, 현재가 정보: {current_price}, 현재가-전일대비=전일종가: {y_end_price}, 등락율={diff_a:.3f}%")
            if t_09_00 < now < t_11_00:   #오전 9시에서 11시 사이에는 종가대비 3~4% 상승한 종목을 구매
                print(f"{'='*50}\n오전장{'='*50}")
                if 7 <= diff_a <= 9:
                    print(f"{'='*50}\n{st_name}이(가) 조건에 부합하여 매수를 시도합니다.\n{'='*50}")
                    count_condition = count_condition+1
                    print(f"조건에 부합하는 종목을 {count_condition} 개 찾았습니다.")
                    buy(symbol, 1)  # 종목 코드와 매수량을 매수 함수에 전달
                else:
                    print("조건에 부합하지 않으므로 넘어갑니다.")
            elif t_11_00 < now < t_13_30:  #오전 11시와 오후 13시 30분 사이에는 5프로 이상 9프로 이하는 구매
                #print(f"{'='*50}\n시간 테스트11111{'='*50}")
                if 6 <= diff_a <= 9:
                    print(f"{'='*50}\n{st_name}이(가) 조건에 부합하여 매수를 시도합니다.\n{'='*50}")
                    count_condition = count_condition+1
                    print(f"조건에 부합하는 종목을 {count_condition} 개 찾았습니다.")
                    buy(symbol, 1)  # 종목 코드와 매수량을 매수 함수에 전달
                else:
                    print("조건에 부합하지 않으므로 넘어갑니다.")
                       
            elif t_13_30 < now < t_15_30 :  #오후 13시 30분 부터 오후 15시 30분까지는 종가 대비 9~15프로 상승 종목을 구매
                #print(f"{'='*50}\n시간 테스트222222{'='*50}") 
                if  0.5 <=  diff_a <= 0.9:
                    print(f"{'='*50}\n{st_name}이(가) 조건에 부합하여 매수를 시도합니다.\n{'='*50}")
                    count_condition = count_condition+1
                    print(f"조건에 부합하는 종목을 {count_condition} 개 찾았습니다.")
                    buy(symbol, 1)  # 종목 코드와 매수량을 매수 함수에 전달
                else:
                    print("조건에 부합하지 않으므로 넘어갑니다.")
            else:
                print(f"{'='*50}\n장이 열린 시간이 아니어서 구매는 따로 하지 않고 종목 모니터링만 진행 합니다\n{'='*50}")        


        except KeyError as e:
            print(f"키 에러 발생: {e}")
        except ValueError as e:
            print(f"값 에러 발생: {e}")
        except Exception as e:
            print(f"에러 발생: {e}")
        finally:
            pass

    print(f"\n{'='*50}\n종목을 전체적으로 탐색 완료 하였습니다.\n{'='*50}\n")
    
    time.sleep(1)

    keys = list(my_poket.keys())
    for key in keys:
        try:
            if key in my_poket:
                values = my_poket[key] 
                name = str(values[0])  # 종목명
                qty = int(values[1])  # 보유수량
                num1 = float(values[2])  # 매수가
                num2 = float(values[3])  # 현재가
                diff = (num2 * qty) - (num1 * qty)
                margin_rate = ((num2 / num1) - 1) * 100  # 수익률

                print(f"({key}): ({name})의 수익률은 {margin_rate:.3f}% 입니다.")
                if margin_rate >= 2.1:
                    print(f"{name}이(가) 이익이 발생하여 매도를 시도합니다.")
                    sell(key, qty)
                elif margin_rate <= -0.7:
                    print(f"{name}이(가) 손실이 발생하여 손절을 시도합니다.")
                else:
                    print("조건에 부합하지 않으므로 넘깁니다.")
        except KeyError as e:
            print(f"키 에러 발생: {e}")
        except ValueError as e:
            print(f"값 에러 발생: {e}")
        except Exception as e:
            print(f"에러 발생: {e}")
        finally:
            pass
    print(f"\n{'='*50}\n 보유 종목 조건 확인을 완료하였습니다. \n{'='*50}\n")