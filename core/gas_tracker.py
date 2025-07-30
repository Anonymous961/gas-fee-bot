import requests
from config.api_keys import config

ETHERSCAN_API_KEY=config["ETHERSCAN_API_KEY"]

def eth_gas_tracker(gas_price=2_000_000_000):
    url= "https://api.etherscan.io/api"

    # params = {
    #     "module": "gastracker",
    #     "action": "gasestimate",
    #     "gasprice": gas_price,
    #     "apikey": ETHERSCAN_API_KEY,
    # }
    params = {
        "module": "gastracker",
        "action": "gasoracle",
        "apikey": ETHERSCAN_API_KEY,
    }


    try:
        response= requests.get(url,params=params,timeout=5)
        response.raise_for_status()

        data= response.json()

        if data.get("status")=="1":
            return {
                "low": data["result"]["SafeGasPrice"],
                "medium": data["result"]["ProposeGasPrice"],
                "high": data["result"]["FastGasPrice"]
            }
        else:
            # Optional: Return entire error object or some default/error value
            return {"error": data.get("message", "Unknown error"), "response": data}
        
    except requests.exceptions.RequestException as e:
        return {"error":str(e)}