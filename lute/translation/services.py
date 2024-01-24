from lute.translation.baidufanyi import load_api_keys, BaiDuFanyi

from lute.config.app_config import AppConfig
from lute.translation.youdaofanyi import YouDaoTranslator

app_conf_path = AppConfig.default_config_filename(dev=True)
fanyikey_path = AppConfig(app_conf_path).fanyikeypath
d = load_api_keys(fanyikey_path)
if 'baidu' in d:
    baidu = d['baidu']

    appKey = baidu['appid']  # 你在第一步申请的APP ID
    appSecret = baidu['appkey']  # 公钥
    BaiduTranslate = BaiDuFanyi(appKey, appSecret)
if 'youdao' in d:
    youdao = d['youdao']
    appKey = youdao['appid']  # 你在第一步申请的APP ID
    appSecret =youdao['appkey']  # 公钥
    youdao_translator = YouDaoTranslator(appKey, appSecret)
    # Results = BaiduTranslate_test.BdTrans("Hello, World!")  # 要翻译的词组

def baidu_translate(text):
    return BaiduTranslate.BdTrans(text)

def youdao_translate(text):
    return youdao_translator.translate(text, 'ja2zh')

if __name__ == '__main__':
    res=baidu_translate('Hello word')
    print(res)