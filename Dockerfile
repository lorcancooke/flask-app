# syntax=docker/dockerfile:1

ARG CLOUDSMITH_WORKSPACE
ARG CLOUDSMITH_REPOSITORY

# ---------- Stage 1: Build with dev base image ----------

FROM docker.cloudsmith.io/${CLOUDSMITH_WORKSPACE}/${CLOUDSMITH_REPOSITORY}/docker/library/python:3.13-slim AS dev


# for chainguard FROM docker.cloudsmith.io/${CLOUDSMITH_WORKSPACE}/${CLOUDSMITH_REPOSITORY}/chainguard/python:latest-dev AS dev

ARG CLOUDSMITH_SERVICE
ARG CLOUDSMITH_WORKSPACE
ARG CLOUDSMITH_REPOSITORY
ARG CLOUDSMITH_API_KEY

WORKDIR /flask-app

RUN python -m venv venv
ENV PATH="/flask-app/venv/bin":$PATH
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --index-url https://$CLOUDSMITH_SERVICE:$CLOUDSMITH_API_KEY@dl.cloudsmith.io/basic/$CLOUDSMITH_WORKSPACE/$CLOUDSMITH_REPOSITORY/python/simple/

# ---------- Stage 2: Final runtime image ----------

FROM docker.cloudsmith.io/${CLOUDSMITH_WORKSPACE}/${CLOUDSMITH_REPOSITORY}/docker/library/python:3.13-slim

# for chainguard FROM docker.cloudsmith.io/${CLOUDSMITH_WORKSPACE}/${CLOUDSMITH_REPOSITORY}/chainguard/python:latest

ARG CLOUDSMITH_WORKSPACE
ARG CLOUDSMITH_REPOSITORY
ARG BUILD_NUMBER=dev
ARG BUILD_DATE=unknown
ARG GIT_SHA=unknown

WORKDIR /flask-app

COPY app.py app.py
COPY --from=dev /flask-app/venv /flask-app/venv
ENV PATH="/flask-app/venv/bin:$PATH"

ENV BUILD_NUMBER=${BUILD_NUMBER}
ENV BUILD_DATE=${BUILD_DATE}
ENV GIT_SHA=${GIT_SHA}
ENV CLOUDSMITH_WORKSPACE=${CLOUDSMITH_WORKSPACE}
ENV CLOUDSMITH_REPOSITORY=${CLOUDSMITH_REPOSITORY}

EXPOSE 5000

ENTRYPOINT ["python", "-m", "gunicorn", "-b", "0.0.0.0:5000", "app:app"]


