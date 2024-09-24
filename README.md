## MAIXCAM上运行：
* 将launcher和launcher_deamon都kill掉或者重命名，top命令看一下确保没有在运行
* 运行python文件

## PC端（Windows）
* pc安装ASCOM （测试用的 6.6版本
* 安装驱动（exe文件）
* 安装NINA

* NINA驱动选择Sony NEX （还没来得及改名字，比较麻烦
* 点击驱动选择旁边的齿轮，进入设置
* 将IP地址设置为板子的IP
* 保存后打开相机

### 注意事项
* 设置到cam.gain的增益为NINA中增益的32倍
* （ASCOM中增益为16bit，因此必须缩小一下，到python里面乘上32）
