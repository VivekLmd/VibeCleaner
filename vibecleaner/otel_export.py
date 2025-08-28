from pathlib import Path
from typing import Optional
import json

from .telemetry import runs_base_dir


def export_run_to_otel(run_id: str) -> str:
    """Export a run as a single OTEL trace with spans for provider calls.

    Requires opentelemetry-sdk and otlp exporter installed. If unavailable, returns a hint.
    """
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    except Exception:
        return (
            "OpenTelemetry packages not found. Install extras:\n"
            "  pip install opentelemetry-sdk opentelemetry-exporter-otlp\n"
            "Then re-run the export."
        )

    base = runs_base_dir() / run_id
    run_meta = json.loads((base / "run.json").read_text(encoding="utf-8"))
    events = [json.loads(l) for l in (base / "events.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

    provider = TracerProvider(resource=Resource.create({"service.name": "vibecleaner"}))
    span_exporter = OTLPSpanExporter()  # honors OTEL_EXPORTER_OTLP_* env vars
    provider.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer("vibecleaner")

    with tracer.start_as_current_span("vibecleaner.run", attributes={
        "run.id": run_id,
        "vibecleaner.cmd": run_meta.get("cmd", ""),
        "vibecleaner.mode": run_meta.get("mode", ""),
        "vibecleaner.provider": run_meta.get("provider", ""),
        "vibecleaner.model": run_meta.get("model", ""),
    }):
        for e in events:
            ev = e.get("event")
            attrs = {k: v for k, v in e.items() if k not in ("event", "ts")}
            if ev in ("provider_call_start", "provider_call_end"):
                name = f"{ev}:{attrs.get('provider','')}"
            else:
                name = ev
            with tracer.start_as_current_span(name, attributes=attrs):
                pass

    # Force flush
    provider.force_flush()
    return "Exported run to OTLP (check your collector)."

