from dotenv import dotenv_values
import os

# Load configuration with priority:
# 1. Existing environment variables (works in Render)
# 2. .env file (works locally)
config = {
    **dotenv_values(".env"),  # will be empty if .env doesn't exist
    **os.environ             # will contain Render's environment variables
}

# Alternative simpler version if you don't need .env support:
# config = os.environ  # Just use this if you only use environment variables