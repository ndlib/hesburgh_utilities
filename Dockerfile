FROM python:2.7.12

RUN pip install boto3 pyyaml

COPY scripts /scripts
COPY py /scripts/hesburgh_utilities
COPY py hesburgh_utilities/py
COPY js hesburgh_utilities/js

ENV PATH="$PATH:/scripts"
