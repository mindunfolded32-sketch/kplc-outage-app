import os
import africastalking

AT_USERNAME = os.getenv("AT_USERNAME", "sandbox")
AT_API_KEY = os.getenv("AT_API_KEY", "")
AT_SENDER_ID = os.getenv("AT_SENDER_ID", None)

if AT_API_KEY:
    africastalking.initialize(AT_USERNAME, AT_API_KEY)
    sms_service = africastalking.SMS
else:
    sms_service = None

async def dispatch_alert(sub_type: str, target: str, outage: dict):
    if sub_type == "webhook":
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                await client.post(target, json={
                    "event": "kplc_outage_alert",
                    "data": outage
                })
        except Exception as e:
            logger.error(f"Webhook failed: {e}")

    elif sub_type == "sms":
        msg = f"KPLC ALERT: Outage on {outage['outage_date']} ({outage['region']}). Details: {outage['link']}"
        if sms_service:
            try:
                sms_service.send(msg, [target], sender_id=AT_SENDER_ID)
                logger.info(f"SMS delivered to {target}")
            except Exception as e:
                logger.error(f"Africa's Talking error: {e}")
        else:
            logger.info(f"[SMS MOCK to {target}]: {msg}")