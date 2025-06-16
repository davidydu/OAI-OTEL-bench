import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# Ensure Protobuf over HTTP
os.environ.setdefault("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")

OTLP_ENDPOINT = "https://logfire-us.pydantic.dev/otlp/v1/traces"
OTLP_HEADERS = {"Authorization": f"Bearer {os.getenv('LOGFIRE_TOKEN', '')}"}

exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT, headers=OTLP_HEADERS)
processor = BatchSpanProcessor(exporter)

provider = trace.get_tracer_provider()
if hasattr(provider, "add_span_processor"):
    provider.add_span_processor(processor)
else:
    resource = Resource.create({"service.name": "openai-agent-benchmark"})
    sdk_provider = TracerProvider(resource=resource)
    sdk_provider.add_span_processor(processor)
    trace.set_tracer_provider(sdk_provider)

tracer = trace.get_tracer(__name__)
