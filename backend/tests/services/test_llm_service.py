"""Tests for LLMService — JSON parsing, prompt formatting (mocked Groq)."""

import json

import pytest

from app.services.llm_service import _parse_json_response


class TestParseJsonResponse:
    def test_parses_plain_json(self):
        text = '{"key": "value", "num": 42}'
        result = _parse_json_response(text)
        assert result == {"key": "value", "num": 42}

    def test_strips_markdown_fences(self):
        text = '```json\n{"key": "value"}\n```'
        result = _parse_json_response(text)
        assert result == {"key": "value"}

    def test_strips_generic_fences(self):
        text = '```\n{"key": "value"}\n```'
        result = _parse_json_response(text)
        assert result == {"key": "value"}

    def test_handles_whitespace(self):
        text = '  \n  {"key": "value"}  \n  '
        result = _parse_json_response(text)
        assert result == {"key": "value"}

    def test_raises_on_invalid_json(self):
        with pytest.raises(json.JSONDecodeError):
            _parse_json_response("not valid json")

    def test_parses_nested_json(self):
        data = {
            "bull_case": "Strong growth",
            "bull_target": 200.0,
            "key_drivers": ["Revenue growth", "Margin expansion"],
        }
        result = _parse_json_response(json.dumps(data))
        assert result["bull_target"] == 200.0
        assert len(result["key_drivers"]) == 2
