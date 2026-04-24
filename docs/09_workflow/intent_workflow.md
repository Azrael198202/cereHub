# environment capability workflow

Intent:
  install_runtime_capability

Workflow:
  1. detect missing software
  2. analyze installation requirements
  3. generate install plan
  4. request permission if needed
  5. execute installation
  6. verify installation
  7. register capability
  8. continue blocked task

## Capability Layer 

Responsible for determining what's missing.

For example:
- No ollama
- No python package
- No ffmpeg
- No playwright browser
- No specific local model

## Environment Layer

Responsible for installation and repair.

For example:
- Install ollama
- pip install xxx
- playwright install
- ollama pull qwen3:4b

## Runtime Layer

Responsible for executing installation commands.

For example:
- shell
- python
- sandbox
- subprocess

## Trace / Validation

Responsible for recording and confirming successful installation.

For example:
- Installation log
- Version check
- Command return code
- Health check