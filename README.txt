编辑渠道列表：
channels.txt 添加渠道编号

打包方法1：
把ipa文件放在此目录下重命名为app.ipa, 双击 "多渠道ipa打包.bat"

打包方法2：
把ipa文件拖拽到”多渠道ipa打包.bat"图标上

高级用法：
iparepack.py inputfile [-c CONFIG]

必选参数：
inputfile: 需要处理的ipa文件路径
可选参数：
-c CONFIG: 新包的参数配置文件，以json格式存储

支持修改的参数：
CFBundleIdentifier	:BundleId
CFBundleDisplayName	:应用名称
U8SDK			:U8SDK渠道参数
sign			:签名证书

注意：
所有文本文件都要以utf-8编码格式保存
Mac打包，需要安装python3
自定义ipa处理:修改process_script.py脚本