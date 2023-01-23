from waves_config import RECEIVER_ADDRESS
from waves_config import W3_ETH, W3_BSC, W3_POLYGON
from waves_config import ETH_USDT_CONTRACT, ETH_USDC_CONTRACT, ETH_BUSD_CONTRACT
from waves_config import BSC_USDT_CONTRACT, BSC_USDC_CONTRACT, BSC_BUSD_CONTRACT
from waves_config import POLYGON_USDT_CONTRACT, POLYGON_USDC_CONTRACT, POLYGON_BUSD_CONTRACT

def _decode_input(contract_address, data):
    decoded_input = contract_address.decode_function_input(data)[1]
    if decoded_input.get("to"):
        to, value = decoded_input["to"], decoded_input["value"]
    else:
        to, value = decoded_input["_to"], decoded_input["_value"]
    return to, value

def check_tx(tx_hash, amount):

    try:
        tx = W3_ETH.eth.get_transaction(tx_hash)
        if tx.to == ETH_USDT_CONTRACT.address:
            to, value = _decode_input(ETH_USDT_CONTRACT, tx.input)
            if to != RECEIVER_ADDRESS:
                return
            value = float(W3_ETH.fromWei(value, "mwei"))
            if value == amount:
                return True
        elif tx.to == ETH_USDC_CONTRACT.address:
            to, value = _decode_input(ETH_USDC_CONTRACT, tx.input)
            if to != RECEIVER_ADDRESS:
                return
            value = float(W3_ETH.fromWei(value, "mwei"))
            if value == amount:
                return True
        elif tx.to == ETH_BUSD_CONTRACT.address:
            to, value = _decode_input(ETH_BUSD_CONTRACT, tx.input)
            if to != RECEIVER_ADDRESS:
                return
            value = float(W3_ETH.fromWei(value, "ether"))
            if value == amount:
                return True
        else:
            pass
    except:
        pass

    try:
        tx = W3_BSC.eth.get_transaction(tx_hash)
        if tx.to == BSC_USDT_CONTRACT.address:
            to, value = _decode_input(BSC_USDT_CONTRACT, tx.input)
            if to != RECEIVER_ADDRESS:
                return
            value = float(W3_ETH.fromWei(value, "ether"))
            if value == amount:
                return True
        elif tx.to == BSC_USDC_CONTRACT.address:
            to, value = _decode_input(BSC_USDC_CONTRACT, tx.input)
            if to != RECEIVER_ADDRESS:
                return
            value = float(W3_ETH.fromWei(value, "ether"))
            if value == amount:
                return True
        elif tx.to == BSC_BUSD_CONTRACT.address:
            to, value = _decode_input(BSC_BUSD_CONTRACT, tx.input)
            if to != RECEIVER_ADDRESS:
                return
            value = float(W3_ETH.fromWei(value, "ether"))
            if value == amount:
                return True
        else:
            pass
    except:
        pass
    
    try:
        tx = W3_POLYGON.eth.get_transaction(tx_hash)
        if tx.to == POLYGON_USDT_CONTRACT.address:
            to, value = _decode_input(POLYGON_USDT_CONTRACT, tx.input)
            if to != RECEIVER_ADDRESS:
                return
            value = float(W3_ETH.fromWei(value, "mwei"))
            if value == amount:
                return True
        elif tx.to == POLYGON_USDC_CONTRACT.address:
            to, value = _decode_input(POLYGON_USDC_CONTRACT, tx.input)
            if to != RECEIVER_ADDRESS:
                return
            value = float(W3_ETH.fromWei(value, "mwei"))
            if value == amount:
                return True
        elif tx.to == POLYGON_BUSD_CONTRACT.address:
            to, value = _decode_input(POLYGON_BUSD_CONTRACT, tx.input)
            if to != RECEIVER_ADDRESS:
                return
            value = float(W3_ETH.fromWei(value, "ether"))
            if value == amount:
                return True
        else:
            return
    except:
        return
