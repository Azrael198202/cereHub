# cerehub
Phase 2 runnable implementation for `cerehub/core`.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn core.main:app --reload --port 8000
```

Open:
- http://127.0.0.1:8000/ui/box/
- http://127.0.0.1:8000/ui/app/
