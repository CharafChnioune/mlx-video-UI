import asyncio
import json
import os
import urllib.request
import urllib.error
from urllib.parse import urlparse
from pathlib import Path
from typing import Optional, List


class PromptEnhancerService:
    """
    Prompt enhancement service supporting local MLX, Ollama, and LM Studio backends.

    LM Studio API Reference (0.4.0+):
    - REST API v1: /api/v1/models, /api/v1/chat
    - REST API v0: /api/v0/models (legacy)
    - OpenAI compat: /v1/models, /v1/chat/completions

    See: https://lmstudio.ai/docs/api/rest-api
    """

    def __init__(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        ui_root = Path(__file__).resolve().parents[2]
        self._repo_root = repo_root
        self._ui_root = ui_root
        self._python_cmd = self._resolve_python()
        self._default_ollama = "http://127.0.0.1:11434"
        self._default_lmstudio = "http://127.0.0.1:1234"

    def _prompt_path(self, filename: str) -> Path:
        override = self._ui_root / "backend" / "prompts" / filename
        if override.exists():
            return override
        return (
            self._repo_root
            / "mlx-video"
            / "mlx_video"
            / "models"
            / "ltx"
            / "prompts"
            / filename
        )

    def _load_prompt_text(self, filename: str, fallback: str) -> str:
        prompt_path = self._prompt_path(filename)
        if prompt_path.exists():
            return prompt_path.read_text()
        return fallback

    def _load_system_prompt(self) -> str:
        return self._load_prompt_text(
            "gemma_t2v_system_prompt.txt",
            "You are a creative assistant. Expand the user's prompt into a detailed video prompt with audio.",
        )

    def _load_negative_system_prompt(self) -> str:
        return self._load_prompt_text(
            "gemma_t2v_negative_system_prompt.txt",
            "You are a creative assistant. Generate a concise negative prompt to avoid artifacts and unwanted elements.",
        )

    def _filename_system_prompt(self) -> str:
        return (
            "Return a short, filesystem-safe filename (3-8 words) describing the scene. "
            "Use only lowercase letters and spaces; no punctuation, no quotes. "
            "Return only the filename text, nothing else."
        )

    def _resolve_python(self) -> str:
        mlx_root = self._repo_root / "mlx-video"
        venv_bin = mlx_root / ".venv" / "bin"
        for candidate in ("python", "python3"):
            path = venv_bin / candidate
            if path.exists():
                return str(path)
        return "python"

    def _auth_headers(self) -> dict:
        """Get authorization headers for LM Studio if token is set."""
        token = os.environ.get("LMSTUDIO_API_TOKEN") or os.environ.get("LMSTUDIO_TOKEN")
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

    def _normalize_lmstudio_base(self, base_url: str) -> str:
        """Normalize LM Studio base URL."""
        base = (base_url or "").strip()
        if not base:
            return self._default_lmstudio.rstrip("/")

        parsed = urlparse(base)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"

        trimmed = base.split("/")[0]
        if "://" not in trimmed:
            trimmed = f"http://{trimmed}"
        parsed = urlparse(trimmed)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
        return self._default_lmstudio.rstrip("/")

    def _build_user_prompt(self, prompt: str, negative_prompt: Optional[str] = None) -> str:
        if negative_prompt:
            return f"user prompt: {prompt}\nexisting negative prompt: {negative_prompt}"
        return f"user prompt: {prompt}"

    def _build_local_prompt(self, prompt: str, negative_prompt: Optional[str] = None) -> str:
        if negative_prompt:
            return f"{prompt}\nexisting negative prompt: {negative_prompt}"
        return prompt

    async def _fetch_json(self, url: str, payload: Optional[dict] = None, headers: Optional[dict] = None) -> dict:
        def _do_request() -> dict:
            data = None
            req_headers = {"Content-Type": "application/json", **(headers or {})}
            if payload is not None:
                data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=req_headers)
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8"))

        return await asyncio.to_thread(_do_request)

    async def _fetch_json_with_status(
        self, url: str, payload: Optional[dict] = None, headers: Optional[dict] = None
    ) -> tuple[int, Optional[dict], str]:
        def _do_request() -> tuple[int, Optional[dict], str]:
            data = None
            req_headers = {"Content-Type": "application/json", **(headers or {})}
            if payload is not None:
                data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=req_headers)
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    body = resp.read().decode("utf-8")
                    return resp.status, json.loads(body) if body else None, body
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
                try:
                    parsed = json.loads(body) if body else None
                except Exception:
                    parsed = None
                return exc.code, parsed, body
            except urllib.error.URLError as exc:
                return 0, None, str(exc.reason)

        return await asyncio.to_thread(_do_request)

    def _extract_models(self, data: dict) -> list[dict]:
        """Extract model list from LM Studio v1 API response.

        v1 API response format:
        {
            "models": [
                {
                    "type": "llm",
                    "key": "lmstudio-community/qwen2.5-7b-instruct",
                    "display_name": "Qwen 2.5 7B Instruct",
                    "loaded_instances": [{"id": "...", "config": {...}}],
                    ...
                }
            ]
        }
        """
        # v1 API uses "models" array directly
        if isinstance(data, list):
            entries = data
        else:
            entries = data.get("models") or data.get("data") or data.get("items") or []

        models = []
        for item in entries:
            if isinstance(item, str):
                models.append({
                    "id": item,
                    "display_name": item,
                    "state": None,
                    "type": "llm"
                })
                continue

            # v1 API uses "key" as primary identifier
            model_id = (
                item.get("key")  # v1 API primary
                or item.get("id")
                or item.get("model")
                or item.get("name")
                or item.get("identifier")
                or item.get("path")
            )
            if not model_id:
                continue

            # Skip embedding models (only return LLMs)
            model_type = item.get("type", "llm")
            if model_type == "embedding":
                continue

            # Get display name (v1 API provides human-readable names)
            display_name = item.get("display_name") or model_id

            # Determine loaded state from loaded_instances
            loaded_instances = item.get("loaded_instances") or []
            state = "loaded" if loaded_instances else "not-loaded"

            # Fallback to explicit state/status fields
            if not loaded_instances:
                explicit_state = item.get("state") or item.get("status")
                if explicit_state:
                    state = explicit_state
                elif isinstance(item.get("loaded"), bool):
                    state = "loaded" if item.get("loaded") else "not-loaded"

            instance_id = None
            if isinstance(loaded_instances, list) and loaded_instances:
                instance_id = loaded_instances[0].get("id")

            models.append({
                "id": model_id,
                "display_name": display_name,
                "state": state,
                "type": model_type,
                "instance_id": instance_id
            })
        return models

    async def _list_lmstudio_models(self, base_url: str) -> list[dict]:
        """
        List available models from LM Studio.

        Tries multiple endpoints in order:
        1. /api/v1/models (REST API v1 - LM Studio 0.4.0+)
        2. /api/v0/models (REST API v0 - legacy)
        3. /v1/models (OpenAI compat)
        """
        headers = self._auth_headers()
        last_error = None

        # Try endpoints in order of preference (v1 first for LM Studio 0.4.0+)
        endpoints = [
            "/api/v1/models",  # LM Studio REST API v1 (0.4.0+)
            "/api/v0/models",  # LM Studio REST API v0 (legacy)
            "/v1/models",      # OpenAI compatibility
        ]

        for endpoint in endpoints:
            status, data, body = await self._fetch_json_with_status(
                base_url.rstrip("/") + endpoint, headers=headers
            )
            if status in (200, 201):
                return self._extract_models(data or {})
            last_error = f"LM Studio {endpoint} HTTP {status}: {body}".strip()

        raise RuntimeError(last_error or "LM Studio not responding. Make sure LM Studio is running and the server is started (lms server start).")

    def _parse_lmstudio_error(self, status: int, data: Optional[dict], body: str, model: str) -> str:
        """Parse LM Studio error response into a user-friendly message."""
        error_msg = "LM Studio request failed"

        if data and isinstance(data, dict):
            error_obj = data.get("error", {})
            if isinstance(error_obj, dict):
                error_msg = error_obj.get("message", error_msg)
            elif isinstance(error_obj, str):
                error_msg = error_obj

        if "not defined" in error_msg.lower() or "utility process" in error_msg.lower():
            return (
                "LM Studio internal error. Please try:\n"
                "1. Restart LM Studio\n"
                "2. Load the model manually in LM Studio first\n"
                "3. If the issue persists, restart your computer"
            )
        elif "not found" in error_msg.lower() or "not loaded" in error_msg.lower():
            return f"Model '{model}' not found. Please load it in LM Studio first."
        elif status == 0:
            return "Cannot connect to LM Studio. Make sure LM Studio is running and the server is started."

        return error_msg

    async def _is_model_loaded(self, base_url: str, model: str) -> bool:
        """Check if a model is currently loaded in LM Studio."""
        try:
            models = await self._list_lmstudio_models(base_url)
            for m in models:
                if m.get("id") == model and m.get("state") == "loaded":
                    return True
            return False
        except Exception:
            return False

    async def _unload_lmstudio_model(self, base_url: str, instance_id: str, timeout: int = 30) -> tuple[bool, Optional[str]]:
        """
        Unload a model in LM Studio using the v1 API.

        POST /api/v1/models/unload
        Request: {"identifier": "instance-id"}
        Response: {"success": true}

        Args:
            base_url: LM Studio base URL
            instance_id: The instance_id of the loaded model to unload
            timeout: Timeout in seconds

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        headers = self._auth_headers()
        # LM Studio expects "instance_id" as the key (not "identifier")
        payload = {"instance_id": instance_id}

        def _do_unload() -> tuple[int, Optional[dict], str]:
            data = json.dumps(payload).encode("utf-8")
            req_headers = {"Content-Type": "application/json", **headers}
            req = urllib.request.Request(
                base_url.rstrip("/") + "/api/v1/models/unload",
                data=data,
                headers=req_headers
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    body = resp.read().decode("utf-8")
                    return resp.status, json.loads(body) if body else None, body
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
                try:
                    parsed = json.loads(body) if body else None
                except Exception:
                    parsed = None
                return exc.code, parsed, body
            except urllib.error.URLError as exc:
                return 0, None, f"Connection error: {exc.reason}"

        status, data, body = await asyncio.to_thread(_do_unload)

        if status in (200, 201):
            print(f"[LM Studio] Model instance '{instance_id}' unloaded successfully")
            return True, None

        # Extract error message
        error_msg = "Unknown error"
        if data and isinstance(data, dict):
            error_obj = data.get("error", {})
            if isinstance(error_obj, dict):
                error_msg = error_obj.get("message", error_msg)
            elif isinstance(error_obj, str):
                error_msg = error_obj
        elif body:
            error_msg = body[:200]

        return False, error_msg

    async def _get_loaded_models(self, base_url: str) -> list[dict]:
        """Get all currently loaded models with their instance IDs."""
        try:
            models = await self._list_lmstudio_models(base_url)
            return [m for m in models if m.get("state") == "loaded" and m.get("instance_id")]
        except Exception:
            return []

    async def _load_lmstudio_model(self, base_url: str, model: str, timeout: int = 300) -> tuple[bool, Optional[str]]:
        """
        Load a model in LM Studio using the v1 API.

        POST /api/v1/models/load
        Request: {"model": "model-key"}
        Response: {"type": "llm", "instance_id": "...", "status": "loaded"}

        Args:
            base_url: LM Studio base URL
            model: Model key/identifier to load
            timeout: Timeout in seconds for loading (default 5 minutes)

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        headers = self._auth_headers()
        payload = {"model": model}

        # Use longer timeout for model loading (can take a while for large models)
        def _do_load() -> tuple[int, Optional[dict], str]:
            data = json.dumps(payload).encode("utf-8")
            req_headers = {"Content-Type": "application/json", **headers}
            req = urllib.request.Request(
                base_url.rstrip("/") + "/api/v1/models/load",
                data=data,
                headers=req_headers
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    body = resp.read().decode("utf-8")
                    return resp.status, json.loads(body) if body else None, body
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
                try:
                    parsed = json.loads(body) if body else None
                except Exception:
                    parsed = None
                return exc.code, parsed, body
            except urllib.error.URLError as exc:
                return 0, None, f"Connection error: {exc.reason}"

        status, data, body = await asyncio.to_thread(_do_load)

        if status in (200, 201):
            load_status = data.get("status") if data else None
            if load_status == "loaded":
                print(f"[LM Studio] Model '{model}' loaded successfully")
                return True, None
            else:
                return False, f"Unexpected status: {load_status}"

        # Extract error message from response
        error_msg = "Unknown error"
        if data and isinstance(data, dict):
            error_obj = data.get("error", {})
            if isinstance(error_obj, dict):
                error_msg = error_obj.get("message", error_msg)
            elif isinstance(error_obj, str):
                error_msg = error_obj
        elif body:
            error_msg = body[:200]

        return False, error_msg

    async def _ensure_model_loaded(self, base_url: str, model: str) -> None:
        """
        Ensure a model is loaded in LM Studio, loading it if necessary.

        LM Studio typically only allows one model loaded at a time.
        If another model is loaded, we unload it first before loading the requested model.

        Raises RuntimeError if the model cannot be loaded.
        """
        # First check if already loaded
        if await self._is_model_loaded(base_url, model):
            return

        # Check if other models are loaded and unload them first
        loaded_models = await self._get_loaded_models(base_url)
        for loaded in loaded_models:
            instance_id = loaded.get("instance_id")
            loaded_name = loaded.get("display_name") or loaded.get("id")
            if instance_id:
                print(f"[LM Studio] Unloading currently loaded model '{loaded_name}' to make room for '{model}'...")
                success, error = await self._unload_lmstudio_model(base_url, instance_id)
                if not success:
                    print(f"[LM Studio] Warning: Failed to unload '{loaded_name}': {error}")
                    # Continue anyway, maybe loading will still work

        # Try to load the model
        print(f"[LM Studio] Loading model '{model}'...")
        success, error = await self._load_lmstudio_model(base_url, model)

        if not success:
            raise RuntimeError(
                f"Failed to load model \"{model}\". Error: {error}"
            )

        print(f"[LM Studio] Model '{model}' is now ready")

    async def _chat_lmstudio_v1(
        self,
        base_url: str,
        model: str,
        user_prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Chat using LM Studio native v1 API with fallback to OpenAI compat.

        LM Studio v1 API (/api/v1/chat):
        - Request: {model, input, system_prompt, temperature, max_output_tokens, stream}
        - Response: {output: [{type: "message", content: "..."}], stats: {...}}

        Falls back to OpenAI compat (/v1/chat/completions) if v1 fails.
        Auto-loads the model if not already loaded.
        """
        # Ensure model is loaded before making chat request
        await self._ensure_model_loaded(base_url, model)

        headers = self._auth_headers()

        # Try native v1 API first (LM Studio 0.4.0+)
        v1_payload = {
            "model": model,
            "input": user_prompt,
            "system_prompt": system_prompt,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "stream": False,
        }

        status, data, body = await self._fetch_json_with_status(
            base_url.rstrip("/") + "/api/v1/chat", v1_payload, headers=headers
        )

        if status in (200, 201):
            # v1 API returns output array
            output = data.get("output") or []
            for item in output:
                if item.get("type") == "message":
                    return (item.get("content") or "").strip()
            return ""

        # Fallback to OpenAI compat endpoint
        openai_payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        status, data, body = await self._fetch_json_with_status(
            base_url.rstrip("/") + "/v1/chat/completions", openai_payload, headers=headers
        )

        if status in (200, 201):
            choices = data.get("choices") or []
            if choices and choices[0].get("message"):
                return (choices[0]["message"].get("content") or "").strip()
            return ""

        # Handle errors
        raise RuntimeError(self._parse_lmstudio_error(status, data, body, model))

    async def list_models(self, provider: str, base_url: Optional[str] = None) -> List[dict]:
        """List available models for a given provider.

        Returns a list of model dictionaries with:
        - id: Model identifier to use in API calls
        - display_name: Human-readable name for UI display
        - state: 'loaded' | 'not-loaded' | None
        - type: 'llm' | 'embedding' (LM Studio v1 only)
        """
        if provider == "local":
            return [{"id": "bundled", "display_name": "Bundled MLX Model", "state": None, "type": "llm"}]
        if provider == "ollama":
            url = (base_url or self._default_ollama).rstrip("/") + "/api/tags"
            data = await self._fetch_json(url)
            models = []
            for m in data.get("models", []):
                name = m.get("name")
                if name:
                    models.append({
                        "id": name,
                        "display_name": name,
                        "state": None,
                        "type": "llm"
                    })
            return models
        if provider == "lmstudio":
            return await self._list_lmstudio_models(
                self._normalize_lmstudio_base(base_url or self._default_lmstudio)
            )
        return []

    async def _enhance_with_prompts(
        self,
        prompt: str,
        provider: str,
        model: Optional[str],
        base_url: Optional[str],
        max_tokens: int,
        temperature: float,
        seed: int,
        enhancer_repo: Optional[str],
        system_prompt: str,
        system_prompt_file: Optional[str],
        negative_prompt: Optional[str] = None,
        use_system_prompt_for_local: bool = True,
    ) -> str:
        if provider == "local":
            local_prompt = self._build_local_prompt(prompt, negative_prompt)
            cmd = [
                self._python_cmd,
                "-m",
                "mlx_video.enhance",
                "--prompt",
                local_prompt,
                "--max-tokens",
                str(max_tokens),
                "--temperature",
                str(temperature),
                "--seed",
                str(seed),
                "--json",
            ]
            if enhancer_repo:
                cmd.extend(["--enhancer-repo", enhancer_repo])
            if use_system_prompt_for_local:
                if system_prompt_file:
                    cmd.extend(["--system-prompt-file", system_prompt_file])
                elif system_prompt:
                    cmd.extend(["--system-prompt", system_prompt])

            repo_override = os.environ.get("MLX_VIDEO_REPO_PATH")
            repo_path = Path(repo_override).expanduser() if repo_override else (self._repo_root / "mlx-video")
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={
                    **os.environ,
                    "PYTHONUNBUFFERED": "1",
                    "PYTHONPATH": os.pathsep.join(
                        [
                            str(repo_path),
                            os.environ.get("PYTHONPATH", ""),
                        ]
                    ).strip(os.pathsep),
                },
            )

            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                err = stderr.decode("utf-8", errors="ignore").strip()
                raise RuntimeError(err or "Prompt enhancement failed")

            out_text = stdout.decode("utf-8", errors="ignore").strip().splitlines()
            if not out_text:
                raise RuntimeError("Prompt enhancement returned no output")

            for line in reversed(out_text):
                if line.strip().startswith("{"):
                    data = json.loads(line)
                    return data.get("enhanced", "").strip()

            raise RuntimeError("Prompt enhancement output was not JSON")

        user_prompt = self._build_user_prompt(prompt, negative_prompt)

        if provider == "ollama":
            if not model:
                raise RuntimeError("Select an Ollama model")
            url = (base_url or self._default_ollama).rstrip("/") + "/api/generate"
            payload = {
                "model": model,
                "prompt": user_prompt,
                "system": system_prompt,
                "stream": False,
                "options": {"temperature": temperature},
            }
            status, data, body = await self._fetch_json_with_status(url, payload)
            if status not in (200, 201):
                raise RuntimeError(body or "Ollama request failed")
            return (data.get("response") or "").strip()

        if provider == "lmstudio":
            if not model:
                raise RuntimeError("Select an LM Studio model")

            lm_base = self._normalize_lmstudio_base(base_url or self._default_lmstudio)
            result = await self._chat_lmstudio_v1(
                base_url=lm_base,
                model=model,
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return result

        raise RuntimeError("Unknown provider")

    async def enhance(
        self,
        prompt: str,
        provider: str = "local",
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
        seed: int = 42,
        enhancer_repo: Optional[str] = None,
    ) -> str:
        """
        Enhance a prompt using the specified provider.

        For LM Studio, uses OpenAI-compatible /v1/chat/completions endpoint
        which supports Just-In-Time (JIT) model loading - the model will be
        loaded automatically when the request is made.
        """
        system_prompt = self._load_system_prompt()
        return await self._enhance_with_prompts(
            prompt=prompt,
            provider=provider,
            model=model,
            base_url=base_url,
            max_tokens=max_tokens,
            temperature=temperature,
            seed=seed,
            enhancer_repo=enhancer_repo,
            system_prompt=system_prompt,
            system_prompt_file=None,
            negative_prompt=None,
            use_system_prompt_for_local=False,
        )

    async def enhance_with_negative(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        provider: str = "local",
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
        seed: int = 42,
        enhancer_repo: Optional[str] = None,
    ) -> tuple[str, str]:
        system_prompt = self._load_system_prompt()
        negative_system_prompt = self._load_negative_system_prompt()
        negative_prompt_file = self._prompt_path("gemma_t2v_negative_system_prompt.txt")
        negative_prompt_file_str = str(negative_prompt_file) if negative_prompt_file.exists() else None

        enhanced = await self._enhance_with_prompts(
            prompt=prompt,
            provider=provider,
            model=model,
            base_url=base_url,
            max_tokens=max_tokens,
            temperature=temperature,
            seed=seed,
            enhancer_repo=enhancer_repo,
            system_prompt=system_prompt,
            system_prompt_file=None,
            negative_prompt=None,
            use_system_prompt_for_local=False,
        )

        negative = await self._enhance_with_prompts(
            prompt=prompt,
            provider=provider,
            model=model,
            base_url=base_url,
            max_tokens=max_tokens,
            temperature=temperature,
            seed=seed,
            enhancer_repo=enhancer_repo,
            system_prompt=negative_system_prompt,
            system_prompt_file=negative_prompt_file_str,
            negative_prompt=negative_prompt,
            use_system_prompt_for_local=True,
        )
        negative = " ".join(negative.splitlines()).strip()

        return enhanced, negative

    async def enhance_filename(
        self,
        prompt: str,
        provider: str = "local",
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        max_tokens: int = 64,
        temperature: float = 0.3,
        seed: int = 42,
    ) -> Optional[str]:
        if provider == "local":
            return None

        filename = await self._enhance_with_prompts(
            prompt=prompt,
            provider=provider,
            model=model,
            base_url=base_url,
            max_tokens=max_tokens,
            temperature=temperature,
            seed=seed,
            enhancer_repo=None,
            system_prompt=self._filename_system_prompt(),
            system_prompt_file=None,
            negative_prompt=None,
            use_system_prompt_for_local=False,
        )
        cleaned = " ".join((filename or "").strip().split())
        return cleaned or None


prompt_enhancer = PromptEnhancerService()
