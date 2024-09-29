# Wumpus LLM Agent

An LLM-powered agent demonstrating tool-use by playing the text game [Hunt the Wumpus](https://en.wikipedia.org/wiki/Hunt_the_Wumpus) using strategic planning and reasoning.

## Dependencies

### Requirements
- Python 3.12
- Local LLM server (Mistral 7B llamafile)
- Hunt the Wumpus game executable

### Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd wumpus-llm-agent
```

2. Create and activate Python environment using pyenv:
```bash
# install Python 3.12 version, e.g. 3.12.7
pyenv install 3.12.7

# create virtualenv
pyenv virtualenv 3.12.7 wumpus-llm-agent-3.12.7

# activate virtualenv
pyenv activate wumpus-llm-agent
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download and set up Mistral 7B llamafile:
```bash
# download the Mistral 7B llamafile
wget "https://huggingface.co/Mozilla/Mistral-7B-Instruct-v0.2-llamafile/resolve/main/mistral-7b-instruct-v0.2.Q4_0.llamafile?download=true" -O mistral-7b-instruct-v0.2.Q4_0.llamafile

# make it executable
chmod +x mistral-7b-instruct-v0.2.Q4_0.llamafile

# run the server (in a separate terminal)
./mistral-7b-instruct-v0.2.Q4_0.llamafile --nobrowser
```

See the [llamafile](https://github.com/Mozilla-Ocho/llamafile) documentation for more details.

5. Install the Hunt the Wumpus game:
```bash
# on MacOS
brew install wumpus
```

This will install ESR's clone of the original BASIC Hunt the Wumpus game: https://gitlab.com/esr/wumpus

NOTE: this agent has only been tested with this version of Hunt the Wumpus.

## Running the Agent

Use the provided wrapper script to run the agent:
```bash
./run_game.sh
```

This script handles:
- Setting up the environment variables for the LLM server
- Launching the agent

## Running Tests

Tests are written using pytest and can be run from the project root:
```bash
# run all tests
pytest tests/

# run specific test file
pytest tests/test_game_handler.py

# run with detailed output
pytest -v tests/

# run with print statements
pytest -s tests/
```

## Evaluation

Game metrics can be dumped from the database as CSV using this script:
```
./dump_metrics.sh
```

In the evals directory, run the following script to generate the evaluation Jupyter notebook using game metric CSV:
```
./generate_notebook.sh
```

## TODO

* experiment with adding more game rules/details to prompt
* enhance prompt and possibly game state for better map movement planning and tracking
* fix "exploring an adjacent room with no detected hazards" reasonings given by LLM response despite detected hazards
* add shooting into multiple rooms
