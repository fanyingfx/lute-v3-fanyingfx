from lute.translation.baidufanyi import load_api_keys, BaiDuFanyi

from lute.config.app_config import AppConfig
from lute.translation.youdaofanyi import YouDaoTranslator

app_conf_path = AppConfig.default_config_filename()
fanyikey_path = AppConfig(app_conf_path).fanyikeypath
print(fanyikey_path)

baidu_status = False
youdao_status = False

d = load_api_keys(fanyikey_path)
if "baidu" in d:
    baidu = d["baidu"]
    appKey = str(baidu["appid"]).strip()  # 你在第一步申请的APP ID
    appSecret = str(baidu["appkey"]).strip()  # 公钥
    BaiduTranslate = BaiDuFanyi(appKey, appSecret)
    try:
        BaiduTranslate.BdTrans("test")
        baidu_status = True
    except Exception:
        pass

if "youdao" in d:
    youdao = d["youdao"]
    appKey = str(youdao["appid"]).strip()  # 你在第一步申请的APP ID
    appSecret = str(youdao["appkey"]).strip()  # 公钥
    youdao_translator = YouDaoTranslator(appKey, appSecret)
    # Results = BaiduTranslate_test.BdTrans("Hello, World!")  # 要翻译的词组
    try:
        r = youdao_translator.translate("こにちは", "ja2zh")
        if r != "E":
            youdao_status = True
    except Exception:
        pass


def baidu_translate(text):
    if not baidu_status:
        return "百度翻译失败"
    return BaiduTranslate.BdTrans(text)


def youdao_translate(text):
    if not youdao_status:
        return "有道翻译失败"
    return youdao_translator.translate(text, "ja2zh")


if __name__ == "__main__":
    res = baidu_translate("Hello word")
    print(res)
