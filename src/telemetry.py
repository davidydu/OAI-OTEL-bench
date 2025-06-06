from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, OTLPSpanExporter
import os

# 1. Initialize TracerProvider with service name
resource = Resource.create({"service.name": "openai-agent-benchmark"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

# 2. Configure OTLP exporter (HTTP) to Logfire
exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
    headers=dict(h.split("=",1) for h in os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "").split(",")),
    protocol=os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")
)
processor = BatchSpanProcessor(exporter)
provider.add_span_processor(processor)

# 3. Obtain tracer
tracer = trace.get_tracer(__name__)
