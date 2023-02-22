FROM python:3.10-slim AS base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

FROM base AS python-deps

# Install pipenv and compilation dependencies
RUN pip install poetry virtualenv
RUN apt-get update && apt-get install build-essential -y --no-install-recommends
# Install python dependencies in /.venv
COPY requirements.txt .
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt


FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=python-deps venv /venv
ENV PATH="/venv/bin:$PATH"

# Create and switch to a new user
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

# Install application into container
COPY . .
EXPOSE 8000
# Run the executable
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0"]
