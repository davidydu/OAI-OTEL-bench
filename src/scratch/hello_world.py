import os
import logfire

# Configure Logfire using token from environment
logfire.configure(token=os.environ.get("LOGFIRE_TOKEN"))
logfire.info("Hello, {place}!", place="World")
