# Updated Technical Plan for Self-Hosting GAIA Agent with SGLang on a RunPod Pod

## Overview
This updated technical plan adapts the GAIA Agent codebase to use self-hosted models via SGLang on a persistent RunPod pod, replacing the dependency on OpenAI’s models and the previously planned serverless RunPod deployment. The plan covers understanding the existing codebase, setting up SGLang, deploying on a RunPod pod, modifying the GAIA code, enhancing logging and telemetry, extracting sparsity patterns, and testing the integration.

## 1. Understand the Current GAIA Agent Codebase
- **Codebase Structure**: The `GAIA_agent_design` folder uses the `openai-agents-python` SDK for tasks like planning, searching, writing, evaluating, and judging, implemented in `research_bot/agents`.
- **Media Processing**: Tools for media processing reside in `agents_lib` (e.g., `processors/*`, `tools/*`).
- **Orchestration**: The `GAIAResearchManager` in `research_bot/manager.py` orchestrates agent calls.
- **Self-Hosted Copy**: The `GAIA_self_hosted_agent` folder is a direct copy of `GAIA_agent_design`, preserving the structure for minimal changes to core logic.

## 2. Set Up SGLang for Self-Hosted Models
- **Installation**:
  - Install `sglang[all]>=0.4.9.post2` using `pip` or `uv`, ensuring dependencies like `FlashInfer` and `PyTorch≈2.7.1` are included (refer to SGLang documentation).
  - Optionally, build a Docker image with SGLang and the chosen model (e.g., Qwen).
- **API Compatibility**:
  - SGLang exposes OpenAI-compatible REST endpoints (e.g., `/v1/chat/completions`, `/v1/completions`), enabling GAIA to treat it like the OpenAI API.

## 3. RunPod Pod Deployment
- **Pod Creation**:
  - Use RunPod’s dashboard to create a pod with sufficient GPU/CPU resources for the chosen model.
- **Docker Image**:
  - Build and push a Docker image containing SGLang and the model (e.g., Qwen) to a registry (Docker Hub or RunPod’s built-in registry).
- **Pod Startup**:
  - Launch the pod with the Docker image, running the SGLang API server (e.g., `sglang-api-server --model qwen-... --port 8000`).
  - This exposes an OpenAI-compatible endpoint at `http://<pod_ip>:8000/v1/chat/completions`.
- **Networking**:
  - Configure port forwarding or public routing per RunPod’s documentation to make the endpoint accessible externally.
  - Secure the endpoint with credentials (e.g., API key or Bearer token) if SGLang authentication is enabled.

## 4. Modify GAIA Code for Self-Hosted Endpoint
- **Agent Configuration**:
  - Update agent creation calls in `research_bot/agents/*.py` (and other relevant modules) to use `base_url=<pod_endpoint>` and `api_key=<sglang_key>` (if required).
  - Retain model names if supported by SGLang for compatibility.
- **Configuration Management**:
  - Store pod endpoint URL, model name, and SGLang parameters in environment variables or update `config.yaml` for use by `GAIAResearchManager`.
- **Remove Serverless Logic**:
  - Eliminate references to `runpod.serverless.start`, as the persistent pod replaces the serverless worker model.

## 5. Logging and Telemetry
- **Existing Instrumentation**:
  - Retain `Logfire` and `OpenTelemetry` setup in `src/telemetry.py`.
  - Ensure HTTP calls to the SGLang pod use `httpx` or `requests` to capture telemetry spans (e.g., latency, status).
- **Enhanced Telemetry**:
  - Add custom spans or attributes to log SGLang endpoint and model details for better traceability.

## 6. Extract Sparsity Patterns
- **Implementation**:
  - If controlling the model code in the pod, modify the model wrapper or forward pass to compute per-layer sparsity metrics (e.g., `mean((activation == 0))`).
- **Metric Exposure**:
  - Expose sparsity metrics via a custom SGLang API endpoint or log them to disk/telemetry (e.g., CSV or Logfire spans) for analysis.

## 7. Testing and Iteration
- **Endpoint Verification**:
  - Send test requests to the pod’s endpoint using the OpenAI API schema (e.g., via `curl` or GAIA code) to confirm responsiveness.
- **Unit Tests**:
  - Update or add GAIA unit tests to use the new pod endpoint, verifying functionality of planner, search, writer, and evaluator agents.
- **Workflow Testing**:
  - Run a small GAIA workflow using `GAIAResearchManager` to ensure pipeline compatibility.
  - Capture telemetry traces to validate integration and confirm sparsity logging.

## Summary
This updated plan shifts from a serverless RunPod worker to a persistent RunPod pod, simplifying stateful operations and debugging. The GAIA agent codebase requires minimal changes, primarily updating endpoint configurations and optionally adding sparsity instrumentation. The approach ensures compatibility with existing logic while leveraging SGLang’s efficient inference and RunPod’s robust hosting.