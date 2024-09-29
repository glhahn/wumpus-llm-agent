#!/usr/bin/env bash

export OPENAI_API_BASE="http://localhost:8080/v1"
export OPENAI_API_KEY="sk-no-key-required"

# model name from the llamafile with OpenAI compatible endpoint
export LITELLM_MODEL="openai/mistral-7b-instruct-v0.2.Q4_0.gguf"

python src/main.py
