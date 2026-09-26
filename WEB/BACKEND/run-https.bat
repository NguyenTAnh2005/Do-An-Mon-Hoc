@echo off
uvicorn main:app --reload --host localhost --port 8000 --ssl-keyfile "cert\localhost+2-key.pem" --ssl-certfile "cert\localhost+2.pem"