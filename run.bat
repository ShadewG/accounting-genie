@echo off
REM Launch Accounting Genie FastAPI server
python -m uvicorn main:app --reload
pause
