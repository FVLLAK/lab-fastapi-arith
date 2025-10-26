# LAB API FastAPI + Docker + Git + Watchers

API FastAPI: `/health`, `/add`, `/sub`, `/mul`, `/div` (division par zéro => HTTP 400).
Scripts de watch (code & git). Docker (image légère, user non-root, port 8000).

## Quickstart
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.app.main:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/health

## Tests
pytest -q

## Docker
export IMAGE_NAME=fallak/lab1
docker build -t $IMAGE_NAME:latest .
docker run -d --rm --name lab1 -p 8000:8000 $IMAGE_NAME:latest

## Watchers
./scripts/watch_build_deploy.sh
./scripts/watch_git_build_deploy.sh

## Git (init & push)
git init && git add . && git commit -m "init"
git branch -M main
git remote add origin https://github.com/FVLLAK/lab-fastapi-arith.git
git push -u origin main
# redeploy check 26 أكتوبر, 2025 +01 21:37:58
