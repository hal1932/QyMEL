@echo off
set PYTHONPATH=%PYTHONPATH%;%~dp0
pushd C:\Program Files\Autodesk\Maya2022\bin
	mayapy.exe -m unittest discover -s %~dp0tests
popd
pause
