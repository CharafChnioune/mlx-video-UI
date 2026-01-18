"""
LoRA Utilities for LTX-2 in mlx-video-UI.

This module provides functionality to:
- Convert PyTorch LoRA weights to MLX format
- Validate LoRA files for compatibility with LTX-2
- Fuse LoRA weights into base model weights
- Scan directories for LoRA files
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import mlx.core as mx


# Default paths to scan for LoRA files
DEFAULT_LORA_PATHS = [
    Path.home() / "Downloads",
    Path.home() / ".mlx-video-ui" / "loras",
    Path(__file__).parent / "loras",  # Project loras folder
]

# LoRA directory for user storage
LORA_DIR = Path.home() / ".mlx-video-ui" / "loras"
LORA_DIR.mkdir(parents=True, exist_ok=True)


def convert_pytorch_lora(lora_path: str) -> dict[str, Any]:
    """
    Convert PyTorch LoRA weights (safetensors) to MLX format.

    PyTorch LoRA key pattern (common):
        diffusion_model.transformer_blocks.{N}.attn1.to_q.lora_A.weight
        diffusion_model.transformer_blocks.{N}.attn1.to_q.lora_B.weight
        diffusion_model.transformer_blocks.{N}.attn1.to_q.lora_down.weight
        diffusion_model.transformer_blocks.{N}.attn1.to_q.lora_up.weight

    MLX model key pattern:
        model.diffusion_model.transformer_blocks.{N}.attn1.to_q.weight

    Args:
        lora_path: Path to the PyTorch LoRA safetensors file

    Returns:
        dict with keys:
            - weights: dict mapping MLX-style keys to (lora_A, lora_B) tuples
            - rank: The LoRA rank
            - target_modules: List of target module types (attn1, attn2, etc.)
            - original_keys: Number of keys in the original file
            - converted_keys: Number of successfully converted key pairs
    """
    from safetensors import safe_open

    # Load the PyTorch weights
    pytorch_weights = {}
    with safe_open(lora_path, framework="numpy") as f:
        for key in f.keys():
            pytorch_weights[key] = mx.array(f.get_tensor(key))

    # Group lora_A and lora_B pairs
    lora_pairs: dict[str, dict[str, mx.array]] = {}
    rank = None
    target_modules = set()

    for key, weight in pytorch_weights.items():
        # Parse the key to extract base path and lora type
        if ".lora_A.weight" in key:
            base_key = key.replace(".lora_A.weight", "")
            lora_type = "lora_A"
        elif ".lora_B.weight" in key:
            base_key = key.replace(".lora_B.weight", "")
            lora_type = "lora_B"
        elif ".lora_down.weight" in key:
            base_key = key.replace(".lora_down.weight", "")
            lora_type = "lora_A"
        elif ".lora_up.weight" in key:
            base_key = key.replace(".lora_up.weight", "")
            lora_type = "lora_B"
        elif ".lora_A" in key and ".weight" not in key:
            base_key = key.replace(".lora_A", "")
            lora_type = "lora_A"
        elif ".lora_B" in key and ".weight" not in key:
            base_key = key.replace(".lora_B", "")
            lora_type = "lora_B"
        elif ".lora_down" in key and ".weight" not in key:
            base_key = key.replace(".lora_down", "")
            lora_type = "lora_A"
        elif ".lora_up" in key and ".weight" not in key:
            base_key = key.replace(".lora_up", "")
            lora_type = "lora_B"
        else:
            continue

        # Convert key from PyTorch format to MLX format
        mlx_key = _convert_key_to_mlx(base_key)

        if mlx_key not in lora_pairs:
            lora_pairs[mlx_key] = {}
        lora_pairs[mlx_key][lora_type] = weight

        # Extract rank from lora_A (shape is [rank, input_dim])
        if lora_type == "lora_A" and rank is None:
            rank = weight.shape[0]

        # Track target modules (attn1, attn2, etc.)
        for module in ["attn1", "attn2", "ff", "norm"]:
            if module in base_key:
                target_modules.add(module)

    # Build final weights dict with complete pairs only
    converted_weights = {}
    for mlx_key, pair in lora_pairs.items():
        if "lora_A" in pair and "lora_B" in pair:
            converted_weights[mlx_key] = {
                "lora_A": pair["lora_A"],
                "lora_B": pair["lora_B"],
            }

    return {
        "weights": converted_weights,
        "rank": rank or 0,
        "target_modules": list(target_modules),
        "original_keys": len(pytorch_weights),
        "converted_keys": len(converted_weights),
    }


def _convert_key_to_mlx(pytorch_key: str) -> str:
    """
    Convert a PyTorch LoRA key to MLX model key format.

    Transformations:
        - Remove 'diffusion_model.' prefix (it's 'model.diffusion_model.' in MLX)
        - Convert '.to_out.0.' to '.to_out.'

    Args:
        pytorch_key: The PyTorch key (without lora_A/lora_B suffix)

    Returns:
        The MLX-compatible key
    """
    key = pytorch_key

    # The PyTorch LoRA starts with 'diffusion_model.'
    # The MLX model has 'model.diffusion_model.'
    # We store just the relative path for matching
    if key.startswith("diffusion_model."):
        key = key[len("diffusion_model."):]

    # Convert to_out.0 to to_out (MLX uses single Linear layer)
    key = key.replace(".to_out.0.", ".to_out.")
    key = key.replace(".to_out.0", ".to_out")

    return key


def validate_lora(path: str) -> dict[str, Any]:
    """
    Validate a LoRA file for compatibility with LTX-2.

    Args:
        path: Path to the LoRA safetensors file

    Returns:
        dict with keys:
            - valid: bool indicating if the LoRA is valid
            - rank: The LoRA rank (if valid)
            - target_modules: List of target modules
            - num_layers: Number of transformer blocks affected
            - error: Error message (if not valid)
    """
    if not os.path.exists(path):
        return {"valid": False, "error": f"File not found: {path}"}

    if not path.endswith(".safetensors"):
        return {"valid": False, "error": "File must be a .safetensors file"}

    try:
        result = convert_pytorch_lora(path)

        if result["converted_keys"] == 0:
            return {
                "valid": False,
                "error": "No valid LoRA weight pairs found",
            }

        # Count unique transformer blocks
        blocks = set()
        for key in result["weights"].keys():
            if "transformer_blocks." in key:
                # Extract block number
                parts = key.split("transformer_blocks.")
                if len(parts) > 1:
                    block_num = parts[1].split(".")[0]
                    if block_num.isdigit():
                        blocks.add(int(block_num))

        return {
            "valid": True,
            "rank": result["rank"],
            "target_modules": result["target_modules"],
            "num_layers": len(blocks),
            "num_weights": result["converted_keys"],
            "error": None,
        }

    except Exception as e:
        return {
            "valid": False,
            "error": f"Failed to load LoRA: {str(e)}",
        }


def fuse_lora_weights(
    base_weights: dict[str, mx.array],
    lora_configs: list[dict[str, Any]],
    return_stats: bool = False,
) -> dict[str, mx.array] | tuple[dict[str, mx.array], dict[str, int]]:
    """
    Fuse LoRA weights into base model weights.

    Formula per layer:
        W_merged = W_base + Σ(scale_i * lora_B_i @ lora_A_i)

    Args:
        base_weights: The base model weights (will be copied, not modified)
        lora_configs: List of dicts with keys:
            - weights: The converted LoRA weights from convert_pytorch_lora()
            - scale: The LoRA scale (float)
            - name: Optional name for logging

    Returns:
        New weights dict with LoRA weights fused in
    """
    # Make a copy of base weights
    fused_weights = dict(base_weights)

    # Track which keys were modified
    modified_keys = set()
    stats = {
        "total_pairs": 0,
        "matched_pairs": 0,
        "skipped_no_base": 0,
        "skipped_dims": 0,
        "skipped_shape": 0,
    }

    for lora_config in lora_configs:
        lora_weights = lora_config.get("weights", {})
        scale = lora_config.get("scale", 1.0)

        if scale == 0.0:
            continue

        for lora_key, lora_pair in lora_weights.items():
            stats["total_pairs"] += 1
            lora_A = lora_pair["lora_A"]
            lora_B = lora_pair["lora_B"]

            # Find matching base weight key
            base_key = _find_matching_base_key(lora_key, fused_weights)

            if base_key is None:
                stats["skipped_no_base"] += 1
                continue

            base_weight = fused_weights[base_key]

            if lora_A.ndim != 2 or lora_B.ndim != 2:
                stats["skipped_dims"] += 1
                continue
            if base_weight.ndim != 2:
                stats["skipped_dims"] += 1
                continue

            rank = lora_A.shape[0]
            if lora_B.shape[1] != rank:
                stats["skipped_shape"] += 1
                continue

            out_dim, in_dim = base_weight.shape
            expected = (lora_B.shape[0], lora_A.shape[1])

            if expected == (out_dim, in_dim):
                delta = scale * (lora_B @ lora_A)
                fused_weights[base_key] = base_weight + delta
                modified_keys.add(base_key)
                stats["matched_pairs"] += 1
            elif expected == (in_dim, out_dim):
                delta = scale * (lora_B @ lora_A)
                fused_weights[base_key] = base_weight + delta.T
                modified_keys.add(base_key)
                stats["matched_pairs"] += 1
            else:
                stats["skipped_shape"] += 1

    if return_stats:
        return fused_weights, stats
    return fused_weights


def _find_matching_base_key(
    lora_key: str,
    base_weights: dict[str, mx.array],
) -> str | None:
    """
    Find the matching base weight key for a LoRA key.

    The LoRA key is a relative path like:
        transformer_blocks.0.attn1.to_q

    The base weight key might be:
        model.diffusion_model.transformer_blocks.0.attn1.to_q.weight

    Args:
        lora_key: The LoRA key (relative path)
        base_weights: The base model weights dict

    Returns:
        The matching base key, or None if not found
    """
    # Try direct match with .weight suffix
    for prefix in ["model.diffusion_model.", "diffusion_model.", ""]:
        candidate = f"{prefix}{lora_key}.weight"
        if candidate in base_weights:
            return candidate

        # Try without .weight suffix
        candidate = f"{prefix}{lora_key}"
        if candidate in base_weights:
            return candidate

    # Fallback: match on suffix to avoid accidental substring matches
    suffixes = (f".{lora_key}.weight", f".{lora_key}")
    for base_key in base_weights.keys():
        if base_key.endswith(suffixes):
            return base_key

    return None


def scan_for_loras(paths: list[str | Path] | None = None) -> list[dict[str, Any]]:
    """
    Scan directories for LoRA safetensors files.

    Args:
        paths: List of paths to scan. Uses DEFAULT_LORA_PATHS if None.

    Returns:
        List of dicts with keys:
            - path: Full path to the LoRA file
            - name: Filename without extension
            - size_mb: File size in MB
            - valid: Whether the LoRA is valid (from quick validation)
    """
    if paths is None:
        paths = DEFAULT_LORA_PATHS

    found_loras = []
    seen_paths = set()

    for search_path in paths:
        search_path = Path(search_path)

        if not search_path.exists():
            continue

        # Search for .safetensors files
        for lora_file in search_path.rglob("*.safetensors"):
            # Skip duplicates
            if str(lora_file) in seen_paths:
                continue
            seen_paths.add(str(lora_file))

            # Skip non-LoRA files (heuristic: check for 'lora' in name or path)
            name_lower = lora_file.name.lower()
            path_lower = str(lora_file).lower()

            # Quick check if this might be a LoRA file
            is_likely_lora = (
                "lora" in name_lower or
                "lora" in path_lower or
                _quick_lora_check(str(lora_file))
            )

            if not is_likely_lora:
                continue

            # Get file size
            size_mb = lora_file.stat().st_size / (1024 * 1024)

            found_loras.append({
                "path": str(lora_file),
                "name": lora_file.stem,
                "size_mb": round(size_mb, 2),
                "valid": None,  # Will be validated on demand
            })

    # Sort by name
    found_loras.sort(key=lambda x: x["name"].lower())

    return found_loras


def _quick_lora_check(path: str) -> bool:
    """
    Quick check if a safetensors file is likely a LoRA file.

    Checks for presence of lora_A or lora_B keys without loading all weights.
    """
    try:
        from safetensors import safe_open

        with safe_open(path, framework="numpy") as f:
            keys = list(f.keys())[:10]  # Check first 10 keys
            for key in keys:
                if "lora_A" in key or "lora_B" in key:
                    return True
        return False
    except Exception:
        return False


def get_lora_info(path: str) -> dict[str, Any]:
    """
    Get detailed information about a LoRA file.

    Args:
        path: Path to the LoRA file

    Returns:
        dict with validation info plus additional details
    """
    validation = validate_lora(path)

    if not validation["valid"]:
        return validation

    # Add file info
    file_path = Path(path)
    validation["name"] = file_path.stem
    validation["size_mb"] = round(file_path.stat().st_size / (1024 * 1024), 2)
    validation["path"] = str(path)

    return validation


def load_lora_for_generation(
    lora_path: str,
    scale: float = 1.0,
) -> dict[str, Any] | None:
    """
    Load and prepare a LoRA for use in generation.

    Args:
        lora_path: Path to the LoRA file
        scale: LoRA scale factor

    Returns:
        LoRA config dict ready for fuse_lora_weights, or None if invalid
    """
    validation = validate_lora(lora_path)

    if not validation["valid"]:
        return None

    converted = convert_pytorch_lora(lora_path)

    return {
        "weights": converted["weights"],
        "scale": scale,
        "name": Path(lora_path).stem,
        "path": lora_path,
        "rank": converted["rank"],
    }
