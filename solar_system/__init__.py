try:
    from solar_system.solar_system import __doc__,__author__,__email__
    from solar_system.solar_system import *
except ImportError:
    from solar_system import __doc__,__author__,__email__
    from solar_system import *
from types import FunctionType

__version__ = "1.3.3"
__all__ = ["GravSys","Star","RoundStar","Sun","SpaceCraft","main",
"PLANET_SIZE","SUN_MASS","MERCURY_MASS","VENUS_MASS","EARTH_MASS",
"MOON_MASS","MARS_MASS","PHOBOS_MASS","AST_MASS","JUPITER_MASS",
"SATURN_MASS","URANUS_MASS","NEPTUNE_MASS","SPACECRAFT_MASS"]

def _copy_func(function,to_globals):
    # 修改函数的全局命名空间，返回更新后的函数
    return FunctionType(function.__code__,
                        to_globals,
                        function.__name__,
                        function.__defaults__,
                        function.__closure__)

if __name__=='__main__':main()
