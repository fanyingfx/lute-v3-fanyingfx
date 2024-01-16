from lute.translation.baidufanyi import load_api_keys, BaiDuFanyi

from lute.config.app_config import AppConfig

app_conf_path = AppConfig.default_config_filename()
fanyikey_path = AppConfig(app_conf_path).fanyikeypath
d = load_api_keys(fanyikey_path)
if 'baidu' in d:
    baidu = d['baidu']

    appKey = baidu['appid']  # 你在第一步申请的APP ID
    appSecret = baidu['appkey']  # 公钥
    BaiduTranslate = BaiDuFanyi(appKey, appSecret)
    # Results = BaiduTranslate_test.BdTrans("Hello, World!")  # 要翻译的词组

def baidu_translate(text):
    return BaiduTranslate.BdTrans(text)

if __name__ == '__main__':
    res=baidu_translate('Hello word')
    print(res)