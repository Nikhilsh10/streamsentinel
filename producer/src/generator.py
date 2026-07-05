import uuid
import random
from datetime import datetime, timezone
import numpy as np
from faker import Faker

fake = Faker()

SENSOR_DEVICES = ["device_001", "device_002", "device_003", "device_004", "device_005"]
MERCHANT_CATEGORIES = ["grocery","fuel","restaurant","electronics",
                       "pharmacy","clothing","travel","entertainment",
                       "utilities","retail"]
COUNTRY_CODES = ["IN","US","GB","SG","AE","DE","AU"]

def get_iso_timestamp():
    return datetime.now(timezone.utc).isoformat()

def generate_sensor_event(anomaly_type=None):
    """
    Generates a sensor event.
    anomaly_type can be: None, 'point', 'contextual'
    """
    is_anomaly = anomaly_type is not None
    
    # Normal distributions
    temp = np.clip(np.random.normal(70, 5), 40, 100)
    vib = np.clip(np.random.normal(0.1, 0.03), 0, 1)
    press = np.clip(np.random.normal(101, 2), 95, 110)
    curr = np.clip(np.random.normal(4.0, 0.5), 0, 10)

    if anomaly_type == 'point':
        # One feature at 4 sigma +
        feature = random.choice(['temp', 'vib', 'press', 'curr'])
        if feature == 'temp':
            temp = np.clip(np.random.normal(95, 2), 40, 100)
        elif feature == 'vib':
            vib = np.clip(np.random.normal(0.4, 0.1), 0, 1)
        elif feature == 'press':
            press = np.clip(np.random.normal(115, 2), 95, 120)
        elif feature == 'curr':
            curr = np.clip(np.random.normal(8.0, 1.0), 0, 10)
            
    elif anomaly_type == 'contextual':
        temp = np.clip(np.random.normal(90, 2), 40, 100)
        curr = np.clip(np.random.normal(0.5, 0.1), 0, 10)
        
    return {
        "event_id": str(uuid.uuid4()),
        "stream": "sensor",
        "timestamp": get_iso_timestamp(),
        "device_id": random.choice(SENSOR_DEVICES),
        "temperature": round(float(temp), 2),
        "vibration": round(float(vib), 3),
        "pressure": round(float(press), 2),
        "current_draw": round(float(curr), 2),
        "is_injected_anomaly": is_anomaly
    }

def generate_financial_event(anomaly_type=None):
    """
    Generates a financial event.
    anomaly_type can be: None, 'point', 'collective'
    """
    is_anomaly = anomaly_type is not None
    
    # Normal distribution
    amount = round(np.random.lognormal(mean=3.5, sigma=1.0), 2)
    merchant = random.choice(MERCHANT_CATEGORIES)
    hour = random.randint(0, 23)
    velocity = random.choices([0, 1, 2, 3], weights=[70, 20, 8, 2])[0]
    
    if anomaly_type == 'point':
        amount = round(np.random.lognormal(mean=7.0, sigma=0.5), 2)
    elif anomaly_type == 'collective':
        velocity = random.randint(10, 20)

    return {
        "event_id": str(uuid.uuid4()),
        "stream": "financial",
        "timestamp": get_iso_timestamp(),
        "user_id": fake.sha256()[:12],
        "amount": float(amount),
        "merchant_category": merchant,
        "hour_of_day": int(hour),
        "velocity_30s": int(velocity),
        "country_code": random.choice(COUNTRY_CODES),
        "is_injected_anomaly": is_anomaly
    }

def generate_random_event(anomaly_rate=0.05):
    """
    Generates either a sensor or financial event, with a chance of being an anomaly.
    """
    stream = random.choice(["sensor", "financial"])
    
    is_anomaly = random.random() < anomaly_rate
    anomaly_type = None
    
    if stream == "sensor":
        if is_anomaly:
            anomaly_type = random.choice(['point', 'contextual'])
        return generate_sensor_event(anomaly_type)
    else:
        if is_anomaly:
            anomaly_type = random.choice(['point', 'collective'])
        return generate_financial_event(anomaly_type)
