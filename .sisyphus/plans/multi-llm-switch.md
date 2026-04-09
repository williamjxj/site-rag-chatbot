# Multi-LLM Switching Implementation Plan

> **Goal:** Allow switching between DeepSeek, Kimi, and MiniMax LLMs via environment variables

**Approach:** Add LLM configuration to settings, update chat.py to select the active LLM based on `ACTIVE_LLM` env var, with Kimi as default.

---

## TODOs

- [x] 1. Add LLM config to config.py

  **What to do:** Add three new settings variables:

  ```python
  kimi_api_key: str = os.getenv("KIMI_API_KEY", "")
  minimax_api_key: str = os.getenv("MINIMAX_API_KEY", "")
  active_llm: str = os.getenv("ACTIVE_LLM", "kimi")  # deepseek | kimi | minimax
  ```

- [x] 2. Update chat.py to select LLM dynamically

  **What to do:** Replace the DeepSeek-only logic with a function that selects the correct API key, base URL, and model based on `ACTIVE_LLM`:

  ```python
  def get_chat_llm_config():
      """Get chat LLM configuration based on ACTIVE_LLM."""
      provider = settings.active_llm
      if provider == "deepseek":
          return {
              "api_key": settings.deepseek_api_key,
              "base_url": "https://api.deepseek.com/v1",
              "model": "deepseek-chat",
          }
      elif provider == "kimi":
          return {
              "api_key": settings.kimi_api_key,
              "base_url": "https://api.moonshot.ai/v1",
              "model": "kimi-k2.5",
          }
      elif provider == "minimax":
          return {
              "api_key": settings.minimax_api_key,
              "base_url": "https://api.minimax.chat/v1",
              "model": "abab6.5s-chat",
          }
      else:
          raise ValueError(f"Unknown ACTIVE_LLM: {provider}")
  ```

  Then use this in the answer() function instead of the hardcoded DeepSeek config.

- [x] 3. Test all 3 LLMs

  **QA Scenarios:**

  ```
  Scenario: Test DeepSeek LLM
    Tool: Bash (curl)
    Preconditions: ACTIVE_LLM=deepseek in .env, valid DEEPSEEK_API_KEY
    Steps:
      1. Set ACTIVE_LLM=deepseek (or unset for fallback test)
      2. Restart backend
      3. Send chat request
    Expected Result: Response from DeepSeek API
    Status: ✅ PASSED
    
  Scenario: Test Kimi LLM  
    Tool: Bash (curl)
    Preconditions: ACTIVE_LLM=kimi in .env, valid KIMI_API_KEY
    Steps:
      1. Ensure ACTIVE_LLM=kimi
      2. Send chat request
    Expected Result: Response from Kimi API
    Status: ⚠️ API key returned 401 (invalid/expired key)
    
  Scenario: Test MiniMax LLM
    Tool: Bash (curl)
    Preconditions: ACTIVE_LLM=minimax in .env, valid MINIMAX_API_KEY
    Steps:
      1. Set ACTIVE_LLM=minimax
      2. Send chat request
    Expected Result: Response from MiniMax API
    Status: ✅ PASSED
  ```

---

## Commit Strategy

- Message: `feat: add multi-LLM switching support (deepseek, kimi, minimax)`
- Files: config.py, rag/chat.py

---

## Success Criteria

```bash
# With ACTIVE_LLM=kimi (default)
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -H "Authorization: Bearer TOKEN" -d '{"question":"hello"}'
# Expected: 200 OK with answer from Kimi

# With ACTIVE_LLM=deepseek
# Expected: 200 OK with answer from DeepSeek

# With ACTIVE_LLM=minimax
# Expected: 200 OK with answer from MiniMax
```