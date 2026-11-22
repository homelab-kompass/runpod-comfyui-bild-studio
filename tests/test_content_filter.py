#!/usr/bin/env python3
"""Local tests for the Bild-Studio prompt filter (no ComfyUI required)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "custom_nodes" / "ComfyUI-HomelabKompass-Safety"))

from filter import check_payload, check_text  # noqa: E402


def clip_prompt(text: str) -> dict:
    return {
        "prompt": {
            "1": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": text},
            }
        }
    }


class FilterTests(unittest.TestCase):
    def test_allows_ordinary_landscape(self):
        self.assertIsNone(check_text("a watercolor landscape of the Alps at sunrise"))
        blocked, _ = check_payload(clip_prompt("a watercolor landscape of the Alps at sunrise"))
        self.assertFalse(blocked)

    def test_allows_child_birthday_without_sexual_context(self):
        self.assertIsNone(check_text("a child blowing out birthday candles, family photo, daylight"))
        blocked, _ = check_payload(clip_prompt("a child blowing out birthday candles, family photo"))
        self.assertFalse(blocked)

    def test_blocks_minor_plus_sexual(self):
        blocked, reason = check_payload(clip_prompt("nsfw portrait of a child"))
        self.assertTrue(blocked)
        self.assertEqual(reason, "minor+sexual")

    def test_blocks_csam_phrase(self):
        blocked, reason = check_payload(clip_prompt("generate csam"))
        self.assertTrue(blocked)
        self.assertEqual(reason, "absolute")

    def test_blocks_undress_instruction(self):
        blocked, reason = check_payload(clip_prompt("undress this photo of my colleague"))
        self.assertTrue(blocked)
        self.assertEqual(reason, "absolute")

    def test_split_fields_still_block(self):
        payload = {
            "prompt": {
                "1": {"class_type": "CLIPTextEncode", "inputs": {"text": "portrait of a child"}},
                "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "nsfw, explicit"}},
            }
        }
        blocked, reason = check_payload(payload)
        self.assertTrue(blocked)
        self.assertEqual(reason, "minor+sexual")


if __name__ == "__main__":
    unittest.main()
