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

    LM Studio API Reference:
    - REST API v0: /api/v0/models, /api/v0/chat/completions
    - OpenAI compat: /v1/models, /v1/chat/completions (supports JIT model loading)

    See: https://lmstudio.ai/docs/developer/rest/endpoints
    """

    def __init__(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        self._repo_root = repo_root
        self._python_cmd = self._resolve_python()
        self._default_ollama = "http://127.0.0.1:11434"
        self._default_lmstudio = "http://127.0.0.1:1234"

    def _prompt_path(self, filename: str) -> Path:
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
        """Extract model list from various API response formats."""
        if isinstance(data, list):
            entries = data
        else:
            entries = data.get("data") or data.get("models") or data.get("items") or []
        models = []
        for item in entries:
            if isinstance(item, str):
                models.append({"id": item, "state": None})
                continue
            model_id = (
                item.get("key")
                or item.get("id")
                or item.get("model")
                or item.get("name")
                or item.get("identifier")
                or item.get("path")
            )
            if not model_id:
                continue
            state = item.get("state") or item.get("status")
            instance_id = None
            loaded_instances = item.get("loaded_instances") or []
            if loaded_instances:
                state = "loaded"
                if isinstance(loaded_instances, list) and loaded_instances:
                    instance_id = loaded_instances[0].get("id")
            if isinstance(item.get("loaded"), bool):
                state = "loaded" if item.get("loaded") else "unloaded"
            models.append({"id": model_id, "state": state, "instance_id": instance_id})
        return models

    async def _list_lmstudio_models(self, base_url: str) -> list[dict]:
        """
        List available models from LM Studio.

        Tries multiple endpoints in order:
        1. /api/v0/models (REST API v0 - current)
        2. /v1/models (OpenAI compat)
        """
        headers = self._auth_headers()
        last_error = None

        # Try endpoints in order of preference
        endpoints = [
            "/api/v0/models",  # LM Studio REST API v0
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

    async def list_models(self, provider: str, base_url: Optional[str] = None) -> List[str]:
        """List available models for a given provider."""
        if provider == "local":
            return ["bundled"]
        if provider == "ollama":
            url = (base_url or self._default_ollama).rstrip("/") + "/api/tags"
            data = await self._fetch_json(url)
            return [m.get("name") for m in data.get("models", []) if m.get("name")]
        if provider == "lmstudio":
            models = await self._list_lmstudio_models(
                self._normalize_lmstudio_base(base_url or self._default_lmstudio)
            )
            return [m["id"] for m in models if m.get("id")]
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

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={
                    **os.environ,
                    "PYTHONUNBUFFERED": "1",
                    "PYTHONPATH": os.pathsep.join(
                        [
                            str(self._repo_root / "mlx-video"),
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
            headers = self._auth_headers()

            payload = {
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
                lm_base + "/v1/chat/completions", payload, headers=headers
            )

            if status in (200, 201):
                choices = data.get("choices") or []
                if choices and choices[0].get("message"):
                    return (choices[0]["message"].get("content") or "").strip()
                return ""

            error_msg = "LM Studio request failed"
            if data and isinstance(data, dict):
                error_obj = data.get("error", {})
                if isinstance(error_obj, dict):
                    error_msg = error_obj.get("message", error_msg)
                elif isinstance(error_obj, str):
                    error_msg = error_obj

            if "not defined" in error_msg.lower() or "utility process" in error_msg.lower():
                error_msg = (
                    "LM Studio internal error. Please try:\n"
                    "1. Restart LM Studio\n"
                    "2. Load the model manually in LM Studio first\n"
                    "3. If the issue persists, restart your computer"
                )
            elif "not found" in error_msg.lower() or "not loaded" in error_msg.lower():
                error_msg = f"Model '{model}' not found. Please load it in LM Studio first."
            elif status == 0:
                error_msg = "Cannot connect to LM Studio. Make sure LM Studio is running and the server is started."

            raise RuntimeError(error_msg)

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


prompt_enhancer = PromptEnhancerService()
