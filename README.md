
# 如何安装

1. 安装python推荐python3.10
2. 打开终端(命令行/cmd/powershell)
  1. 确认安装的python 版本 `python -V`
  2. 运行以下命令
```sh
pip install https://github.com/fanyingfx/lute-v3-fanyingfx/releases/download/3.1.1b7/lute3_fy-3.1.1b7-py3-none-any.whl --upgrade
pip install edge-tts
python -m spacy download en_core_web_sm
```
3. 运行
```
python -m lute.main 
```
如过端口被占用，可以运行
```
python -m lute.main --port 9876
```
4.  会发现报错
![image](https://github.com/fanyingfx/lute-v3-fanyingfx/assets/57335844/1770244e-f321-438f-a366-7591fc56b944)

5.  进入报错目录，如果没有就新建目录
Windows中的目录是(C:\Users\用户名\AppData\Local\Lute3\Lute3)需要在Lute3目录中再建一个目录
将分享的词典文件以及`dict_conf.yaml`,`fanyikey.yaml`复制到Lute3目录
7. 重新运行
```
python -m lute.main --port 9876
```

