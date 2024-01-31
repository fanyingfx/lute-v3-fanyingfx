import requests
import random
import json
import yaml
from hashlib import md5


def load_api_keys(conf_path):
    with open(conf_path, "r") as f:
        d = yaml.safe_load(f)
    return d


class BaiDuFanyi:
    def __init__(self, appKey, appSecret):
        self.url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
        self.appid = appKey
        self.secretKey = appSecret
        self.fromLang = "auto"
        self.toLang = "zh"
        self.salt = random.randint(32768, 65536)
        self.header = {"Content-Type": "application/x-www-form-urlencoded"}

    def BdTrans(self, text):
        sign = self.appid + text + str(self.salt) + self.secretKey
        md = md5()
        md.update(sign.encode(encoding="utf-8"))
        sign = md.hexdigest()
        data = {
            "appid": self.appid,
            "q": text,
            "from": self.fromLang,
            "to": self.toLang,
            "salt": self.salt,
            "sign": sign,
        }
        response = requests.post(self.url, params=data, headers=self.header)  # 发送post请求
        text = response.json()  # 返回的为json格式用json接收数据
        # print(text)
        results = text["trans_result"][0]["dst"]
        return results


if __name__ == "__main__":
    d = load_api_keys("fanyikey.yaml")
    if "baidu" in d:
        baidu = d["baidu"]

        appKey = baidu["appid"]  # 你在第一步申请的APP ID
        appSecret = baidu["appkey"]  # 公钥
        BaiduTranslate_test = BaiDuFanyi(appKey, appSecret)
        Results = BaiduTranslate_test.BdTrans("Hello, World!")  # 要翻译的词组
        print(Results)
