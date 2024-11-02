if exist .venv\ () else (
  python -m venv .venv
  .venv\scripts\pip install -r requirements.txt
)

.venv\scripts\python main.py