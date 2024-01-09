本仓库用于储存作者长期制作的python源代码, 包含40多个python项目，涉及爬虫、算法、OpenGL、tkinter、面向对象编程等多个领域。 

这些是仓库中的一些亮点项目：

1.图形类
- solar_system：计算机模拟万有引力、太阳系行星运动。【Gitcode版：（已移至仓库[Python 天体引力模拟程序](https://gitcode.net/qfcy_/python-gravity-simulation)）】
【Github版：（已移至仓库[Python 天体引力模拟程序](https://github.com/qfcy/python-gravity-simulation)）】
- opengl：3d图形的渲染，应用简单的OpenGL技术。
- pygame：pygame的图形渲染，如球体碰撞等。

2.界面类
- pynotepad.pyw：使用tkinter编写的文本编辑器, 支持编辑文本文件、二进制文件、自由选择主题等。
- painter：使用tkinter的Canvas控件制作的画板程序, 支持编辑、保存文档以及文档属性等功能，并有自制的文件格式`.vec`。
- 窗口控制工具.py：调用API函数，控制电脑中其他程序的窗口，修改标题、透明度，甚至边框样式。
- 录屏.py：录制屏幕，保存为avi，gif格式或png图像序列，需要安装opencv库。

3.文件处理类
- 更新文件工具.py：自动化的数据备份工具，将源文件夹中的文件备份到目标文件夹，使两文件夹内容一致。[文章：Python os模块 设计文件夹自动备份、同步工具](https://blog.csdn.net/qfcy_/article/details/125897258)
- 小项目 \ 文件处理 \ 文件修改日期.py：调用`os.utime`函数，编辑电脑中文件的修改日期。

- search_file.py：用于搜索文件的python模块。
- 复制文件工具.py：在后台复制带有指定关键词的文件。
- 复制文件工具2.py：在后台复制指定文件夹。
- 小项目 \ 文件处理 \ 清理cef程序缓存.py：清理常用软件如WPS、钉钉、Edge缓存数据的工具，适用于大多数软件。

说明：部分文件处理项目需使用pip安装search-file库。

4.网络类
- WEB：包含自己的web服务器、爬虫等小项目。

5.命令行
- pyshell.py及pyshell_w.py：模拟“>>> ”的Python交互式提示符，适合当做第二个python解释器。
- 命令行：包含作者编写的其他命令行程序。

6.其他
- ulang：应用pyinstxtractor和uncompyle6工具提取的木兰编程语言源代码。
- event：调用API函数模拟键盘、鼠标事件，可用于游戏外挂等。
- pyobject：关于Python对象内部结构、python字节码(bytecode)的库，包含pyc文件的压缩、加壳和脱壳的工具。
- timer.py：Python计时器模块，可用于程序性能分析。
- catch_turtle：使用turtle库开发的一款游戏。
- 小项目 \ turtle：编写的turtle小程序。

更多这里没有介绍的项目，可在源代码的注释中查看说明。

7.版权

本仓库中未注明“来自他人”的源代码，由作者自己编写。