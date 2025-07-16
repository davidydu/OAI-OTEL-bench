# GAIA Agent Self-Hosting Technical Plan

## Overview
This document outlines the technical plan to adapt the GAIA Agent codebase to use self-hosted models via SGLang on RunPod, replacing the dependency on OpenAI’s models. The plan includes understanding the existing codebase, setting up SGLang, deploying on RunPod, modifying the GAIA code, enhancing logging and telemetry, extracting sparsity patterns, and testing the integration.

## 1. Understand the Current GAIA Agent Codebase
- **Codebase Structure**: The `GAIA_agent_design` folder uses the `openai-agents-python` SDK, relying on OpenAI models (e.g., o4-mini, o3, gpt-4.1) for tasks like planning, searching, writing, evaluating, and judging. These are implemented in `research_bot/agents`.
- **Media Processing**: Logic for media processing resides in `agents_lib` (e.g., `processors/*`, `tools/*`).
- **Orchestration**: The `GAIAResearchManager` in `research_bot/manager.py` orchestrates agent calls.

## 2. Set Up SGLang for Self-Hosted Models
- **Installation**:
  - Install `sglang[all]>=0.4.9.post2` using `pip` or `uv`, along with dependencies like `FlashInfer` and `torch 2.7.1` (refer to SGLang documentation).
  - Alternatively, use Docker for installation as per SGLang’s instructions.
- **Backend**:
  - SGLang provides OpenAI-compatible REST endpoints (e.g., `chat/completions`, `completions`). See SGLang’s OpenAI API – Completions tutorial for setup details.

## 3. Use RunPod for Hosting
- **RunPod Setup**:
  - Build a RunPod Docker image with SGLang installed and the chosen model (e.g., Qwen). Follow RunPod documentation for building custom images.
  - In the serverless entrypoint (similar to RunPod’s sentiment analysis example), start the SGLang backend server and expose endpoints.
  - Optionally, run `sglang-api-server` inside the RunPod container for API compatibility.
- **Configuration**:
  - Use the `runpod` Python package to package and deploy serverless workers.
  - Example: Start the worker with `runpod.serverless.start({"handler": handler})`.

## 4. Modify GAIA Code for Self-Hosting
- **Codebase Adaptation**:
  - Duplicate the `GAIA_agent_design` folder (already done as `GAIA_self_hosted_agent`).
  - Update agent configurations in `research_bot/agents/*.py` to point to RunPod-hosted SGLang endpoints instead of OpenAI’s API.
  - If using SGLang’s OpenAI-compatible API, specify `base_url=<runpod_endpoint>` when creating `Agent` instances, keeping model names intact.
- **Model Parameters**:
  - Add SGLang-specific parameters (e.g., expert parallelism, quantization) via `ModelSettings` or request payloads, as outlined in SGLang documentation.
- **Environment Configuration**:
  - Update `config.yaml` or other config structures to include RunPod credentials (API keys or tokens) and SGLang endpoint URLs.

## 5. Logging and Telemetry
- **Existing Instrumentation**:
  - Retain `Logfire` and `OpenTelemetry` instrumentation as implemented in `src/telemetry.py`.
  - Ensure SGLang client requests use `httpx` or similar to capture spans.
- **Enhanced Metrics**:
  - Optionally extend instrumentation to log additional metrics, such as activation sparsity (see below).

## 6. Extract Sparsity Patterns
- **Implementation**:
  - If SGLang provides hooks for activation tensors, use its Python API to intercept them.
  - For models like Qwen, modify the model’s forward pass or implement a wrapper to compute per-layer sparsity (`(tensor==0).float().mean()`).
- **Storage**:
  - Store sparsity metrics in a CSV file or as custom attributes on `Logfire` spans for later analysis.

## 7. Testing and Iteration
- **Deployment**:
  - Build and deploy the RunPod container.
  - Verify that the SGLang server responds correctly to `chat/completions` requests.
- **Unit Tests**:
  - Update GAIA agent unit tests to ensure compatibility with the self-hosted endpoint.
- **Workflow Testing**:
  - Run GAIA workflows locally against the RunPod endpoint.
  - Collect traces to verify the integration and ensure no disruptions in functionality.

## Summary
This plan reuses the existing GAIA agent codebase while redirecting model inference to a self-hosted SGLang backend on RunPod. Key changes include updating agent configurations, integrating SGLang endpoints, enhancing telemetry for sparsity metrics, and thorough testing to ensure a seamless transition.