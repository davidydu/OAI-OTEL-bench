from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import os

# 1. Initialize TracerProvider with service name
resource = Resource.create({"service.name": "openai-agent-benchmark"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

# 2. Configure OTLP exporter (HTTP) to Logfire
# Parse headers safely
headers_str = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")
headers = {}
if headers_str:
    for header in headers_str.split(","):
        if "=" in header:
            key, value = header.split("=", 1)
            headers[key.strip()] = value.strip()

exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
    headers=headers
)
processor = BatchSpanProcessor(exporter)
provider.add_span_processor(processor)

# 3. Obtain tracer
tracer = trace.get_tracer(__name__)
