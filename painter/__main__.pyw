try:
    from __init__ import __import_mod
    fmt_str="%s"
except ImportError:
    from .__init__ import __import_mod
    fmt_str="painter.%s"
mod=__import_mod(fmt_str)
mod.main()
