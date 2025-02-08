import sys,os
from setuptools import setup,Extension

try:os.chdir(os.path.split(__file__)[0])
except:pass

# 操作说明：
# 在命令提示符中转到solar_system_accelerate_util.c所在目录，
# 运行命令python setup.py bdist，即可编译该Python扩展模块。
# 再将生成的build\lib.winxx-cpythonxx目录中的.pyd文件
# 移动至"引力模拟.py"所在目录，即可使用。
setup(
    name='solar-system-accelerate-util',
    version='1.3.3',
    ext_modules=[Extension(
        "solar_system_accelerate_util",["solar_system_accelerate_util.c"]
    )],
)