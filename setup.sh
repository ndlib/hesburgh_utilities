pip install boto3 pyyaml setuptools

cd py
pip install -e .
cd ..

cd scripts
pip install -e .
cd ..

cd js
yarn link
cd ..
