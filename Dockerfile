FROM python:2.7.12

RUN pip install boto3 pyyaml

COPY scripts /scripts
COPY py /scripts/hesburgh
COPY py hesburgh/py
COPY js hesburgh/js

ENV PATH="$PATH:/scripts"
