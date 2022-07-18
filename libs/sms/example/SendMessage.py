from libs.sms.ronglian_sms_sdk import SmsSDK

accId = '8a216da881ad97540181b82e906f01c7'
accToken = '58f47ba00f274ea69fab320261daf929'
appId = '8a216da881ad97540181b82e919a01ce'


def send_message(phone_num, template_num):
    sdk = SmsSDK(accId, accToken, appId)
    tid = '容联云通讯创建的模板'
    mobile = '手机号1,手机号2'
    datas = ('变量1', '变量2')
    resp = sdk.sendMessage(tid, mobile, datas)
    print(resp)


send_message()
