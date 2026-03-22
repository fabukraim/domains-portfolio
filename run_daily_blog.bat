@echo off
:: Navigate to the project directory
cd /d "c:\Users\Admin\Desktop\domanid.com"

:: Run the blog generator script using the virtual environment python
"c:\Users\Admin\Desktop\domanid.com\.venv\Scripts\python.exe" blog_generator.py

:: Done
echo Daily Blog Update Complete.
timeout /t 5
