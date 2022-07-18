from libs.sms.ronglian_sms_sdk import SmsSDK
from celery_handler.main import app

accId = '8a216da881ad97540181b82e906f01c7'
accToken = '58f47ba00f274ea69fab320261daf929'
appId = '8a216da881ad97540181b82e919a01ce'


@app.task
def celery_send_sms(mobile, code):
    sdk = SmsSDK(accId, accToken, appId)
    tid = '1'

    datas = (code, '3')
    sdk.sendMessage(tid, mobile, datas)
