FROM python:2.7.12

RUN pip install boto3 pyyaml
COPY py /scripts/hesburgh

COPY scripts /scripts
ENV PATH="$PATH:/scripts"
