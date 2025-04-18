FROM python:3.11-slim

# Upgrade pip, setuptools, wheel
RUN pip install --upgrade pip setuptools wheel

# Create app user
RUN groupadd -g 1000 appuser && \
    useradd --create-home --uid 1000 --gid 1000 appuser


# Set working directory and switch to appuser
WORKDIR /home/appuser
COPY --chown=appuser:appuser . /tmp

USER appuser

# Install Python package (your local module in /tmp)
RUN pip install --no-cache-dir /tmp \
    && rm -rf /tmp/*

# Run your module
CMD ["python3", "-u", "-m", "tl_model_server"]
