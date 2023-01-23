import asyncio
import aiohttp
from time import sleep
from waves_config import *

async def send_request(method, url, headers=None, json=None, data=None, cookies=None):
    async with aiohttp.ClientSession() as session:
        if method == "get":
            async with session.get(url, headers=headers, cookies=cookies, json=json, data=data) as response:
                if response.content_type == "application/json":
                    return await response.json()
                else:
                    return await response.text()
        elif method == "post":
            async with session.post(url, headers=headers, cookies=cookies, json=json, data=data) as response:
                if response.content_type == "application/json":
                    return await response.json()
                else:
                    return await response.text()
        else:
            raise TypeError

def check_balances():

    low_eth = False
    low_bsc = False
    low_polygon = False

    eth_balance = W3_ETH.eth.get_balance(GATEWAY)
    eth_balance = Web3.fromWei(eth_balance, "ether")

    bsc_balance = W3_BSC.eth.get_balance(GATEWAY)
    bsc_balance = Web3.fromWei(bsc_balance, "ether")

    polygon_balance = W3_POLYGON.eth.get_balance(GATEWAY)
    polygon_balance = Web3.fromWei(polygon_balance, "ether")

    if eth_balance < 0.2:
        low_eth = True

    if bsc_balance < 0.2:
        low_bsc = True

    if polygon_balance < 0.2:
        low_polygon = True
    
    return low_eth, low_bsc, low_polygon

def get_token_balances():

    try:
        eth_busd_balance = ETH_BUSD_CONTRACT.functions.balanceOf(GATEWAY).call()
        eth_busd_balance = int(Web3.fromWei(eth_busd_balance, "ether"))
    except:
        eth_busd_balance = "FAIL"

    try:
        eth_usdt_balance = ETH_USDT_CONTRACT.functions.balanceOf(GATEWAY).call()
        eth_usdt_balance = int(Web3.fromWei(eth_usdt_balance, "mwei"))
    except:
        eth_usdt_balance = "FAIL"

    try:
        eth_usdc_balance = ETH_USDC_CONTRACT.functions.balanceOf(GATEWAY).call()
        eth_usdc_balance = int(Web3.fromWei(eth_usdc_balance, "mwei"))
    except:
        eth_usdc_balance = "FAIL"

    try:
        bsc_busd_balance = BSC_BUSD_CONTRACT.functions.balanceOf(GATEWAY).call()
        bsc_busd_balance = int(Web3.fromWei(bsc_busd_balance, "ether"))
    except:
        bsc_busd_balance = "FAIL"

    try:
        bsc_usdt_balance = BSC_USDT_CONTRACT.functions.balanceOf(GATEWAY).call()
        bsc_usdt_balance = int(Web3.fromWei(bsc_usdt_balance, "ether"))
    except:
        bsc_usdt_balance = "FAIL"

    try:
        bsc_usdc_balance = BSC_USDC_CONTRACT.functions.balanceOf(GATEWAY).call()
        bsc_usdc_balance = int(Web3.fromWei(bsc_usdc_balance, "ether"))
    except:
        bsc_usdc_balance = "FAIL"

    try:
        polygon_usdt_balance = POLYGON_USDT_CONTRACT.functions.balanceOf(GATEWAY).call()
        polygon_usdt_balance = int(Web3.fromWei(polygon_usdt_balance, "mwei"))
    except:
        polygon_usdt_balance = "FAIL"

    try:
        polygon_usdc_balance = POLYGON_USDC_CONTRACT.functions.balanceOf(GATEWAY).call()
        polygon_usdc_balance = int(Web3.fromWei(polygon_usdc_balance, "mwei"))
    except:
        polygon_usdc_balance = "FAIL"

    return eth_busd_balance, eth_usdt_balance, eth_usdc_balance, bsc_busd_balance, bsc_usdt_balance, bsc_usdc_balance, polygon_usdt_balance, polygon_usdc_balance

def check_withdrawal_availability():

    url = "https://api.wx.network/v1/withdraw/currencies?limit=10&offset=0"
    
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.95 Safari/537.36"
    }

    tokens = asyncio.run(send_request("get", url, headers))
    
    if isinstance(tokens, str):
        tokens = asyncio.run(send_request("get", url, headers))
        
    eth_busd_available = False
    eth_usdt_available = False
    eth_usdc_available = False
    bsc_busd_available = False
    bsc_usdt_available = False
    bsc_usdc_available = False
    polygon_usdt_available = False
    polygon_usdc_available = False
    
    if isinstance(tokens, str):
        return eth_busd_available, eth_usdt_available, eth_usdc_available, bsc_busd_available, bsc_usdt_available, bsc_usdc_available, polygon_usdt_available, polygon_usdc_available
    if tokens.get("errors"):
        return eth_busd_available, eth_usdt_available, eth_usdc_available, bsc_busd_available, bsc_usdt_available, bsc_usdc_available, polygon_usdt_available, polygon_usdc_available
    
    tokens = tokens["items"]

    for token in tokens:
        if token["id"] == "BUSD" and token["status"] == "active" and token["platform_id"] == "ETH":
            eth_busd_available = True
            continue
        if token["id"] == "BUSD" and token["status"] == "active" and token["platform_id"] == "BSC":
            bsc_busd_available = True
            continue
        if token["id"] == "USDT" and token["status"] == "active" and token["platform_id"] == "ETH":
            eth_usdt_available = True
            continue
        if token["id"] == "USDT" and token["status"] == "active" and token["platform_id"] == "BSC":
            bsc_usdt_available = True
            continue
        if token["id"] == "USDT" and token["status"] == "active" and token["platform_id"] == "POLYGON":
            polygon_usdt_available = True
            continue
        if token["id"] == "USDC" and token["status"] == "active" and token["platform_id"] == "ETH":
            eth_usdc_available = True
            continue
        if token["id"] == "USDC" and token["status"] == "active" and token["platform_id"] == "BSC":
            bsc_usdc_available = True
            continue
        if token["id"] == "USDC" and token["status"] == "active" and token["platform_id"] == "POLYGON":
            polygon_usdc_available = True
        
    return eth_busd_available, eth_usdt_available, eth_usdc_available, bsc_busd_available, bsc_usdt_available, bsc_usdc_available, polygon_usdt_available, polygon_usdc_available

def get_price(pair):

    if pair == "USDC_USDT":
        url = PriceUrl.USDC_USDT
    elif pair == "BUSD_USDT":
        url = PriceUrl.BUSD_USDT
    elif pair == "BUSD_USDC":
        url = PriceUrl.BUSD_USDC
    else:
        raise TypeError

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "cookie": "intercom-id-ibdxiwmt=9fbc1be5-c19f-411a-ae89-f77bfe8490e7; sp=66fcb826-880d-4542-98f7-304200f6c608; intercom-device-id-ibdxiwmt=19fcbdbf-8077-46bd-87db-1b471d5dcb9b; amplitude_id_e3b3df0d53b4cae5b75350d898132934waves.exchange=eyJkZXZpY2VJZCI6IjJiMDUyYWEzLWQ3MDAtNDJkZS1iMGRjLTc1ODA1ODIyMzFlMVIiLCJ1c2VySWQiOm51bGwsIm9wdE91dCI6ZmFsc2UsInNlc3Npb25JZCI6MTY3MDkxODcyMzg2NCwibGFzdEV2ZW50VGltZSI6MTY3MDkxOTA5MzQ3MCwiZXZlbnRJZCI6MiwiaWRlbnRpZnlJZCI6MSwic2VxdWVuY2VOdW1iZXIiOjN9; _ga=GA1.1.364205357.1657555371; INGRESSCOOKIE=1672137586.446.42.318078; _sp_ses.a15c=*; amplitude_id_1b7892a92d0e56a667df25583600fff3waves.exchange=eyJkZXZpY2VJZCI6IjllOWY0MmVhLTJkZWUtNDljZS1iMTRlLTI0OWI3OWU2YjMyNlIiLCJ1c2VySWQiOiIwNTY4NmRmZi1hZjZkLTQ2MGYtYjZjYS02Mzg1MjdkNzcyYzMiLCJvcHRPdXQiOmZhbHNlLCJzZXNzaW9uSWQiOjE2NzIxMzc1ODYzOTIsImxhc3RFdmVudFRpbWUiOjE2NzIxMzc1OTYxNzYsImV2ZW50SWQiOjc3NSwiaWRlbnRpZnlJZCI6MCwic2VxdWVuY2VOdW1iZXIiOjc3NX0=; _sp_id.a15c=dac0a226-69c1-4226-85fb-fb1a7067eba9.1657555379.174.1672137852.1672079517.e1651981-fdaa-403b-b1e3-246ca2c71160; intercom-session-ibdxiwmt=STliMytCcEpENXVoOXdrcXZlRkRkMUZqU3Jla24wY1hwNlh1NjQ1VUtCQ250cTM1YjNDMWJNdlR2eHlxTGhNZy0tdkx3TXIzSzhHQ0R3NEJsOU5jTTFkdz09--675322e2e7fb25878f585966b10253af4f9e659a; _ga_P2ZYBNY1N0=GS1.1.1672137579.173.1.1672137853.0.0.0",
        "referer": "https://waves.exchange/",
        "ucd": "wx.web",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.95 Safari/537.36"
    }

    price = asyncio.run(send_request("get", url, headers))
    if isinstance(price, dict):
        price = price["data"][0]["data"]["lastPrice"]
        price = int(price * 10000) / 10000
    else:
        price = "FAIL"

    return price

msg = ""

def run_parser():

    global msg

    while True:

        try:

            low_eth, low_bsc, low_polygon = check_balances()

            eth_busd_balance, eth_usdt_balance, eth_usdc_balance, bsc_busd_balance, bsc_usdt_balance, bsc_usdc_balance, polygon_usdt_balance, polygon_usdc_balance = get_token_balances()

            eth_busd_available, eth_usdt_available, eth_usdc_available, bsc_busd_available, bsc_usdt_available, bsc_usdc_available, polygon_usdt_available, polygon_usdc_available = check_withdrawal_availability()

            usdc_usdt = get_price("USDC_USDT")
            busd_usdt = get_price("BUSD_USDT")
            busd_usdc = get_price("BUSD_USDC")
            
            e1 = "(√)" if eth_busd_available else "(X)"
            e2 = "(√)" if eth_usdt_available else "(X)"
            e3 = "(√)" if eth_usdc_available else "(X)"
            
            b1 = "(√)" if bsc_busd_available else "(X)"
            b2 = "(√)" if bsc_usdt_available else "(X)"
            b3 = "(√)" if bsc_usdc_available else "(X)"

            p1 = "(√)" if polygon_usdt_available else "(X)"
            p2 = "(√)" if polygon_usdc_available else "(X)"

            _msg = ""

            _msg += "Gateway (0x6871EaCd33fbcfE585009Ab64F0795d7152dc5a0)\n\n"

            if low_eth or low_bsc or low_polygon:
                if low_eth:
                    _msg += "Low ETH balance\n"
                if low_bsc:
                    _msg += "Low BNB balance\n"
                if low_polygon:
                    _msg += "Low MATIC balance\n"
                _msg += "\n"

            balance_data = [
                [f"{eth_usdt_balance} USDT {e2}", f"{eth_usdc_balance} USDC {e3}", f"{eth_busd_balance} BUSD {e1}"],
                [f"{bsc_usdt_balance} USDT {b2}", f"{bsc_usdc_balance} USDC {b3}", f"{bsc_busd_balance} BUSD {b1}"],
                [f"{polygon_usdt_balance} USDT {p1}", f"{polygon_usdc_balance} USDC {p2}"]
            ]

            balance_data_new = []
            
            for row in balance_data:
                if len(row) > 2:
                    balance_data_new.append("{: >16} {: >16} {: >16}".format(*row))
                else:
                    balance_data_new.append("{: >16} {: >16}".format(*row))

            _msg += "Ethereum  |"+balance_data_new[0]+"\n"
            _msg += "BSC       |"+balance_data_new[1]+"\n"
            _msg += "Polygon   |"+balance_data_new[2]+"\n"

            _msg += "\n"
            
            _msg += f"USDC/USDT |  {usdc_usdt}\n"
            _msg += f"BUSD/USDT |  {busd_usdt}\n"
            _msg += f"BUSD/USDC |  {busd_usdc}\n"

            _msg += "\n"

            if usdc_usdt != "FAIL" and usdc_usdt < 0.975 and (eth_usdc_available or bsc_usdc_available or polygon_usdc_available):
                _msg += "USDT -> USDC arb 2%+\n"
            elif usdc_usdt != "FAIL" and usdc_usdt > 1.025 and (eth_usdt_available or bsc_usdt_available or polygon_usdt_available):
                _msg += "USDC -> USDT arb 2%+\n"
            if busd_usdt != "FAIL" and busd_usdt < 0.975 and (eth_busd_available or bsc_busd_available):
                _msg += "USDT -> BUSD arb 2%+\n"
            elif busd_usdt != "FAIL" and busd_usdt > 1.025 and (eth_usdt_available or bsc_usdt_available or polygon_usdt_available):
                _msg += "BUSD -> USDT arb 2%+\n"
            if busd_usdc != "FAIL" and busd_usdc < 0.975 and (eth_busd_available or bsc_busd_available):
                _msg += "USDC -> BUSD arb 2%+\n"
            elif busd_usdc != "FAIL" and busd_usdc > 1.025 and (eth_usdc_available or bsc_usdc_available or polygon_usdc_available):
                _msg += "BUSD -> USDC arb 2%+"
            
            msg = _msg

        except:
            continue
        
        sleep(5)

def get_access_token():

    url = f"https://api.wx.network/v1/oauth2/token"

    headers = HEADERS
    headers["content-type"] = "application/x-www-form-urlencoded"

    data = {
        "grant_type": "refresh_token",
        "scope": "general",
        "client_id": "waves.exchange",
        "refresh_token": REFRESH_TOKEN
    }

    token = asyncio.run(send_request("post", url, headers, data=data))
    token = token["access_token"]

    return token

def check_withdraw_availability(token, evm_address, network):

    url = f"https://api.wx.network/v1/withdraw/addresses/{token}/{evm_address}/{network}"

    response = asyncio.run(send_request("get", url, HEADERS))
    
    try:

        if response.get("errors"):
            if response["errors"][0]["message"] == "Invalid access token.":
                access_token = get_access_token()
                HEADERS["authorization"] = f"Bearer {access_token}"
                response = asyncio.run(send_request("get", url, HEADERS))
        
        if response.get("errors"):
            return
        
        withdrawal_token = response["currency"]
        send_address = response["proxy_addresses"][0]

        if withdrawal_token["id"] == token and withdrawal_token["platform_id"] == network:
            return send_address
    
    except AttributeError:
        print("error getting response")
        return

def try_withdraw(token, amount):

    eth = check_withdraw_availability(token, RECEIVER_ADDRESS, "ETH")
    bsc = check_withdraw_availability(token, RECEIVER_ADDRESS, "BSC")
    polygon = check_withdraw_availability(token, RECEIVER_ADDRESS, "POLYGON")
    
    if bsc:

        bsc_proxy = pw.Address(bsc)

        if token == "BUSD":
            ACCOUNT.sendAsset(bsc_proxy, BUSD, int(amount * 10**6))
        elif token == "USDT":
            ACCOUNT.sendAsset(bsc_proxy, USDT, int(amount * 10**6))
        elif token == "USDC":
            ACCOUNT.sendAsset(bsc_proxy, USDC, int(amount * 10**6))

    elif polygon:
        
        polygon_proxy = pw.Address(polygon)

        if token == "USDT":
            ACCOUNT.sendAsset(polygon_proxy, USDT, int(amount * 10**6))
        elif token == "USDC":
            ACCOUNT.sendAsset(polygon_proxy, USDC, int(amount * 10**6))

    elif eth:
        
        eth_proxy = pw.Address(eth)

        if token == "BUSD":
            ACCOUNT.sendAsset(eth_proxy, BUSD, int(amount * 10**6))
        elif token == "USDT":
            ACCOUNT.sendAsset(eth_proxy, USDT, int(amount * 10**6))
        elif token == "USDC":
            ACCOUNT.sendAsset(eth_proxy, USDC, int(amount * 10**6))

    else:
        return

try_withdraw_running = False

def try_withdraw_loop(token, amount):
    
    while try_withdraw_running:
        try_withdraw(token, amount)
        sleep(2)
