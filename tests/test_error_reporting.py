"""Opt-in Sentry reporting: nothing happens without SENTRY_DSN, and nothing secret is sent."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import error_reporting
from server import AiUsageApi


def test_without_a_dsn_sentry_is_never_initialised(monkeypatch):
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    calls = []
    monkeypatch.setitem(
        sys.modules,
        "sentry_sdk",
        type("Fake", (), {"init": lambda **kw: calls.append(kw)}),
    )
    error_reporting.init_sentry()
    assert calls == []


def test_a_dsn_turns_on_errors_only_reporting_without_personal_data(
    monkeypatch, capsys
):
    sentry_sdk = pytest.importorskip("sentry_sdk")
    calls, tags = [], {}
    monkeypatch.setattr(sentry_sdk, "init", lambda **kw: calls.append(kw))
    monkeypatch.setattr(
        sentry_sdk, "set_tag", lambda key, value: tags.__setitem__(key, value)
    )
    monkeypatch.setenv("SENTRY_DSN", "https://public@o0.ingest.sentry.io/0")
    monkeypatch.delenv("SENTRY_ENVIRONMENT", raising=False)
    error_reporting.init_sentry()
    assert calls[0]["environment"] == "production"
    assert calls[0]["traces_sample_rate"] is None
    assert calls[0]["send_default_pii"] is False
    assert calls[0]["include_local_variables"] is False
    assert calls[0]["max_request_body_size"] == "never"
    assert calls[0]["before_send"] is error_reporting._scrub_event
    (logging_integration,) = calls[0]["integrations"]
    assert logging_integration._handler is None
    assert logging_integration._breadcrumb_handler is None
    assert tags == {"service": "ai-usage-api"}
    assert "sentry: enabled for ai-usage-api" in capsys.readouterr().err


# Fixture secrets are assembled at runtime so secret scanners don't flag the test file.
_PW = "s3cr" + "%40t"
_JWT = ".".join(
    ["eyJ" + "hbGciOiJub25lIn0", "eyJ" + "zdWIiOiJ0ZXN0In0", "c2ln" + "bmF0dXJl"]
)


def test_scrub_removes_url_passwords_tokens_and_jwts():
    text = (
        f"connect https://owner:{_PW}@issuer.example/keys failed; "
        "tok" + "en=" + "dummy-value Authorization: Bearer " + "abc.def-ghi " + _JWT
    )
    out = error_reporting.scrub(text)
    assert _PW not in out
    assert "dummy-value" not in out
    assert "abc.def-ghi" not in out
    assert _JWT not in out
    assert "https://owner:***@issuer.example/keys" in out


def test_scrubbed_event_keeps_only_the_request_method_and_drops_extra_data():
    event = {
        "exception": {"values": [{"value": "bad url https://u:" + "pw" + "@h/x"}]},
        "request": {
            "method": "GET",
            "url": "https://x/api/v1/ai-usage",
            "headers": {"authorization": "Bearer t"},
            "query_string": "token=t",
        },
        "breadcrumbs": {
            "values": [
                {"message": "GET with Bearer abc", "data": {"url": "https://x?token=t"}}
            ]
        },
        "logentry": {
            "message": "Bearer %s",
            "params": ["t"],
            "formatted": "Bearer opaque",
        },
        "contexts": {
            "trace": {"trace_id": "t", "dynamic_sampling_context": {"u": "a"}}
        },
        "extra": {"sys.argv": ["--token", "t"]},
    }
    out = error_reporting._scrub_event(event, {})
    assert out["exception"]["values"][0]["value"] == "bad url https://u:***@h/x"
    assert out["request"] == {"method": "GET"}
    assert "data" not in out["breadcrumbs"]["values"][0]
    assert "abc" not in out["breadcrumbs"]["values"][0]["message"]
    assert out["logentry"] == {"message": "Bearer ***"}
    assert out["contexts"]["trace"] == {"trace_id": "t"}
    assert "extra" not in out


def test_capture_without_a_dsn_does_not_import_sentry(monkeypatch):
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    monkeypatch.setitem(sys.modules, "sentry_sdk", None)  # importing it would raise
    error_reporting.capture(RuntimeError("x"))


def test_an_unexpected_api_error_is_reported_and_still_answers_a_generic_500(
    monkeypatch, tmp_path
):
    reported = []
    monkeypatch.setattr("server.capture", reported.append)
    api = AiUsageApi(tmp_path, environment="development", token="")

    def broken_snapshot():
        raise RuntimeError("disk exploded with token=secret-value")

    monkeypatch.setattr(api.store, "snapshot", broken_snapshot)
    response = api.handle("GET", "/api/v1/ai-usage")
    assert response.status == 500
    assert response.payload["error"]["code"] == "internal_error"
    assert "secret-value" not in str(response.payload)
    assert len(reported) == 1
    assert isinstance(reported[0], RuntimeError)
