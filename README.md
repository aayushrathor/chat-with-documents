## Steps to Setup Application

> Make sure you have python>=3.8 installted in your system
> Install lm-studio in-order to use LLMs. `https://lmstudio.ai/`

1. Install uv (better than pip) python package manager

```bash
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows.
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. Create Virtual Environment

```bash
uv venv venv --python python3.8 -v
```

3. Activate Virtual Environment

```bash
# On macOS and Linux.
source .venv/bin/activate

# On Windows.
.venv\Scripts\activate
```

4. Install Dependencies

```bash
uv pip install -r requirements.txt
```

5. run application

```bash
chainlit run src/main.py --watch --headless --no-cache --host 0.0.0.0 --port 8000
```

6. use application on browser at `http://localhost:8000`
