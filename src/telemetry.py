import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# Ensure Protobuf over HTTP
os.environ.setdefault("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")

# Logfire OTLP ingest URL & auth header
OTLP_ENDPOINT = "https://logfire-us.pydantic.dev/otlp/v1/traces"
OTLP_HEADERS = {
    "Authorization": "Bearer pylf_v1_us_9bZ57RDYs2P0LbbxcjK95kxZKL0jqFDhKqjYtTR7Wwy7"
}

# Build exporter & processor
exporter = OTLPSpanExporter(
    endpoint=OTLP_ENDPOINT,
    headers=OTLP_HEADERS
)
processor = BatchSpanProcessor(exporter)

# Attach to existing provider or install a new one if proxy
provider = trace.get_tracer_provider()
if hasattr(provider, "add_span_processor"):
    provider.add_span_processor(processor)
else:
    resource = Resource.create({"service.name": "openai-agent-benchmark"})
    sdk_provider = TracerProvider(resource=resource)
    sdk_provider.add_span_processor(processor)
    trace.set_tracer_provider(sdk_provider)

# Export tracer
tracer = trace.get_tracer(__name__)