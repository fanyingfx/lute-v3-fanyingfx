[原版Lute链接](https://github.com/LuteOrg/lute-v3)
## 如何安装
### 前提
- 首先需要系统上安装python
- 可能需要科学上网
- 需要下载词典文件：https://pan.baidu.com/s/15Xd5NheDYePiaPvkvuQEbQ?pwd=v1hj 提取码: v1hj
### 安装过程
1. 打开终端执行以下命令
` pip install https://github.com/fanyingfx/lute-v3-fanyingfx/releases/download/3.3.3a1/lute3-3.3.3a1-py3-none-any.whl --upgrade`
2. 执行
`python -m lute.main` 如果出现端口冲突可将命令换为
`python -m lute.main --port 5151` 其中5151可以是其它大于5000的数字

3. 启动会应该会报错，此时讲从下载文件中复制 dicts, unidic-cwj复制到提示的Lute数据目录

### 词典设置
#### 英语
![English Dict](https://github.com/user-attachments/assets/408c0750-2c70-48d7-b2b9-87aecd0c5bab)
#### 日语
![Japanese](https://github.com/user-attachments/assets/12e5b790-23dc-4983-8050-ad7ee483b03d)
