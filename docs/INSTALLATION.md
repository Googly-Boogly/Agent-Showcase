# Installation

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/), **or** Python 3.11+ with FFmpeg

## Configuration

Create `config.yaml` in the project root before running:

```yaml
ANTHROPIC_API_KEY: your_anthropic_key_here
OPENAI_API_KEY: your_openai_key_here
OPENAI_MODEL_NAME: gpt-5-mini
```

This file is git-ignored and must be created manually. The simulation will fail at import time if it is missing — `singleton.py` loads it eagerly, not lazily.

## Docker (recommended)

```bash
# Run the simulation
docker-compose up --build

# Run tests
docker-compose -f docker-compose.tests.yml up --build
```

The Docker image installs FFmpeg and all Python dependencies automatically. Output (`files/animation.mp4`) is written to the host via the mounted `files/` directory.

## Manual (Python 3.11+)

1. Install FFmpeg (required for MP4 output):
   - Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - macOS: `brew install ffmpeg`

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the simulation:
   ```bash
   python src/idk_some_code/main.py
   ```

5. Run tests:
   ```bash
   pytest src/tests/
   ```

## Switching the LLM

The drone LLM is set in `src/idk_some_code/drone.py` in `agent_main()`:

```python
drone_agent = Agent(
    ...
    llm="gpt-5-mini",  # Change this
)
```

Any model string supported by CrewAI's LiteLLM backend works here, e.g.:
- `"gpt-4o"` — OpenAI GPT-4o
- `"anthropic/claude-3-haiku-20240307"` — Claude Haiku
- `"ollama/llama3.2"` — local Ollama model
