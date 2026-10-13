import pytest
import os
from src.template_renderer import TemplateRenderer

def test_simple_placeholder():
    renderer = TemplateRenderer()
    context = {"name": "Alice", "city": "Bangkok"}
    tmpl = "Hello {name}, welcome to {city}!"
    assert renderer.render(tmpl, context) == "Hello Alice, welcome to Bangkok!"

def test_numeric_formatting():
    renderer = TemplateRenderer()
    context = {"sales": 12345.6789, "count": 42}
    tmpl = "Sales: ${sales:.2f}, Count: {count}"
    assert renderer.render(tmpl, context) == "Sales: $12345.68, Count: 42"

def test_environment_placeholder(monkeypatch):
    monkeypatch.setenv("TEST_RECIPIENT_EMAIL", "test@example.com")
    renderer = TemplateRenderer()
    tmpl = "Recipient is ${TEST_RECIPIENT_EMAIL}"
    assert renderer.render(tmpl, {}) == "Recipient is test@example.com"

def test_disallowed_environment_placeholder():
    renderer = TemplateRenderer()
    tmpl = "Secret: ${SUPER_SECRET_KEY}"
    with pytest.raises(ValueError, match="not permitted or restricted"):
        renderer.render(tmpl, {})

def test_missing_context_key():
    renderer = TemplateRenderer()
    tmpl = "Hello {unknown_key}!"
    with pytest.raises(ValueError, match="Missing context key"):
        renderer.render(tmpl, {})

def test_nested_data_access():
    renderer = TemplateRenderer()
    context = {
        "attachments_meta": [
            {"filename": "report.pdf", "filepath": "/path/to/report.pdf"},
            {"filename": "data.xlsx", "filepath": "/path/to/data.xlsx"}
        ]
    }
    tmpl = "Attachment at {attachments_meta.0.filepath} and name {attachments_meta.1.filename}"
    res = renderer.render(tmpl, context)
    assert res == "Attachment at /path/to/report.pdf and name data.xlsx"

def test_nested_key_error():
    renderer = TemplateRenderer()
    context = {"user": {"profile": {}}}
    tmpl = "{user.profile.nonexistent}"
    with pytest.raises(ValueError, match="Missing context key"):
        renderer.render(tmpl, context)
