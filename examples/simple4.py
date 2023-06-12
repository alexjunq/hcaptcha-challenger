import asyncio

from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import RecaptchaV2ProxylessRequest

client_options = ClientOptions(api_key='8fea505bc0d0f0374219368fd1502b07')
cap_monster_client = CapMonsterClient(options=client_options)

async def solve_captcha():
    return await cap_monster_client.solve_captcha(recaptcha2request)

recaptcha2request = RecaptchaV2ProxylessRequest(websiteUrl="https://lessons.zennolab.com/captchas/recaptcha/v2_simple.php?level=high",
                                                websiteKey="6Lcg7CMUAAAAANphynKgn9YAgA4tQ2KI_iqRyTwd")


if __name__ == '__main__':
    responses = asyncio.run(solve_captcha())
    print(responses)
