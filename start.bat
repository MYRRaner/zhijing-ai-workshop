@echo off
chcp 65001 >nul
echo ========================================
echo   智境·AI创意工坊 - 启动脚本
echo ========================================
echo.

echo [1/3] 启动 Flask AI 微服务...
start "Flask AI Service" cmd /k "cd /d %~dp0 && python run_ai_service.py"
timeout /t 3 >nul

echo [2/3] 启动 Django 主应用...
start "Django Main App" cmd /k "cd /d %~dp0 && python manage.py runserver 0.0.0.0:8000"
timeout /t 3 >nul

echo [3/3] 启动完成！
echo.
echo   Flask AI服务: http://127.0.0.1:5001
echo   Django主应用: http://127.0.0.1:8000
echo.
echo   如需配置智谱AI API密钥，请设置环境变量:
echo   set ZHIPU_API_KEY=your_api_key_here
echo.
pause
