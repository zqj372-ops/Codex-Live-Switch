#!/usr/bin/env python3
"""Regression tests for Codex Live Switch config editing helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from common import parse_toml_safely, upsert_provider, upsert_top_level  # noqa: E402


class ConfigEditingTests(unittest.TestCase):
    def test_upsert_preserves_unrelated_provider(self) -> None:
        original = '''approval_policy = "never"

[model_providers.openai]
name = "OpenAI"
base_url = "https://api.openai.com/v1"
wire_api = "responses"
env_key = "OPENAI_API_KEY"
'''
        preset = {
            "provider_id": "minimax",
            "provider_name": "MiniMax",
            "base_url": "https://api.minimax.io/v1",
            "wire_api": "chat_completions",
            "env_key": "MINIMAX_API_KEY",
        }
        updated = upsert_top_level(original, "model", "MiniMax-M3")
        updated = upsert_top_level(updated, "model_provider", "minimax")
        updated = upsert_provider(updated, preset)
        parsed = parse_toml_safely(updated, Path("config.toml"))

        self.assertEqual(parsed["model"], "MiniMax-M3")
        self.assertEqual(parsed["model_provider"], "minimax")
        self.assertIn("openai", parsed["model_providers"])
        self.assertEqual(parsed["model_providers"]["minimax"]["env_key"], "MINIMAX_API_KEY")

    def test_upsert_provider_replaces_existing_provider_without_duplicate_table(self) -> None:
        original = '''model = "old"
model_provider = "minimax"

[model_providers.minimax]
name = "Old"
base_url = "https://old.example/v1"
wire_api = "chat_completions"
env_key = "OLD_KEY"
'''
        preset = {
            "provider_id": "minimax",
            "provider_name": "MiniMax",
            "base_url": "https://api.minimax.io/v1",
            "wire_api": "chat_completions",
            "env_key": "MINIMAX_API_KEY",
        }
        updated = upsert_provider(original, preset)
        parsed = parse_toml_safely(updated, Path("config.toml"))

        self.assertEqual(updated.count("[model_providers.minimax]"), 1)
        self.assertEqual(parsed["model_providers"]["minimax"]["base_url"], "https://api.minimax.io/v1")
        self.assertEqual(parsed["model_providers"]["minimax"]["env_key"], "MINIMAX_API_KEY")


if __name__ == "__main__":
    unittest.main()
