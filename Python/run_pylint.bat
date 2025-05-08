@echo off
rem 关闭部分不必要的提示和警告
python -m pylint %* --disable=C0326 --disable=C0103 --disable=C0115 --disable=C0116 --disable=C0321 --disable=C0410 --disable=W0614  --disable=W0401  --disable=W0641 --disable=W0212 --disable=R0902 --disable=W0613 --disable=C0123 --disable=W0603 --disable=R0914 --disable=R0913 --disable=W0212 --disable=R0912 --disable=R0915 --disable=R0801
pause