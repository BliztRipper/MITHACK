# Hugging Face Space image (live-demo-deployment D1, D6-D9): IRIS for Health and the demo API in one container.
# Only the API's port 7860 is exposed; IRIS (1972, 52773) is reachable from inside the container only.
# Build from the repo root: docker build --platform linux/amd64 -f deploy/space/Dockerfile .
# The assembled Space repo (deploy/space/assemble.sh) has the same layout, with this file at its root.

# Pinned to the linux/amd64 image of IRIS for Health 2026.2 (Spaces run amd64). app/fhir/docker-compose.yml pins the
# multi-arch index for laptops. To bump: docker buildx imagetools inspect intersystems/irishealth-community:<tag>,
# paste the linux/amd64 manifest digest here and re-run the deploy/space checks.
FROM intersystems/irishealth-community:2026.2@sha256:788c8626895ab43951aa3c4356681c0c87b03562b6bd1965b4e67c89d8a7cde9 AS build
USER root
# Spaces run the container as uid 1000: drop the base's unused ubuntu user (1000), renumber irisowner (51773) to 1000
# and re-own its files.
RUN userdel -r ubuntu && groupmod -g 1000 irisowner && usermod -u 1000 -g 1000 irisowner \
 && find / -xdev \( -uid 51773 -o -gid 51773 \) -exec chown -h 1000:1000 {} +
# Python 3.11 for the API (the image ships 3.12 for embedded Python; the API is tested on 3.11).
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /usr/local/bin/uv
COPY app/api/requirements-demo.txt /tmp/requirements-demo.txt
RUN UV_PYTHON_INSTALL_DIR=/opt/python uv venv --python 3.11 /opt/venv \
 && uv pip install --python /opt/venv/bin/python --no-cache -r /tmp/requirements-demo.txt \
 && rm -rf /root/.cache /tmp/requirements-demo.txt /usr/local/bin/uv
COPY --chown=1000:1000 app/api /app/api
COPY app/fhir/setup.script deploy/space/entrypoint.sh /app/

# Flatten: re-owning /usr/irissys in a layer would store its 3.3 GB twice.
FROM scratch
COPY --from=build / /
# The base image's environment, minus its PYTHONPATH (IRIS embedded Python packages, not for the API).
ENV PATH=/opt/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/irisowner/bin \
    ISC_PACKAGE_IRISGROUP=irisowner ISC_PACKAGE_IRISUSER=irisowner \
    ISC_PACKAGE_MGRGROUP=irisowner ISC_PACKAGE_MGRUSER=irisowner \
    IRISSYS=/home/irisowner/irissys ISC_PACKAGE_INSTANCENAME=IRIS ISC_PACKAGE_INSTALLDIR=/usr/irissys \
    LANG=en_US.UTF-8 LANGUAGE=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    PYTHONPATH=/app/api PYTHONDONTWRITEBYTECODE=1 \
    FHIR_BASE=http://localhost:52773/csp/healthshare/demo/fhir/r4 \
    DEMO_MODE=1 USERS_FILE=users.demo.yaml COOKIE_SECURE=1
# Secrets (SESSION_SECRET, APP_MASTER_KEY, IRIS_PASSWORD) and DEMO_PASSWORDS come from the Space settings at run time.
USER 1000
WORKDIR /app/api
EXPOSE 7860
ENTRYPOINT ["/tini", "--", "/app/entrypoint.sh"]
