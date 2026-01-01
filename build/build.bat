@echo off

echo build.bat（ワンクリック exe 化）
echo. 
echo ===============================
echo QRPicker build start
echo ===============================

pyinstaller --onefile --clean --noconsole --name QRPicker ^
--icon icon.ico ^
--add-data "icon.png;." ^
--add-binary "%LOCALAPPDATA%\Programs\Python\Python311\Lib\site-packages\pyzbar\libzbar-64.dll;pyzbar" ^
--add-binary "%LOCALAPPDATA%\Programs\Python\Python311\Lib\site-packages\pyzbar\libiconv.dll;pyzbar" ^
QRPicker.py

echo ===============================
echo Build finished
echo ===============================
pause

