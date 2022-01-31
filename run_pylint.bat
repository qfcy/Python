@echo off
pylint "%1" --disable=C0326 --disable=C0103 --disable=C0321 --disable=C0410 -E
pause