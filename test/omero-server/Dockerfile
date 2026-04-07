FROM ghcr.io/manics/omero-server-docker:ubuntu
LABEL authors="Julio Mateos Langerak"

RUN mkdir $OMERODIR/lib/scripts/omero/microscope_metrics
COPY scripts/* $OMERODIR/lib/scripts/omero/microscope_metrics/

USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

USER omero-server
