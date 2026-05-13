import random
import datetime

MARKETS = ["EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", "AUDUSD-OTC"]

def get_signal():
    market = random.choice(MARKETS)
    action = random.choice(["CALL", "PUT"])
    confidence = random.randint(70, 95)
    time_now = datetime.datetime.now().strftime("%H:%M")

    return {
        "market": market,
        "action": action,
        "confidence": confidence,
        "time": time_now
    }
