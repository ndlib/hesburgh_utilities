pip install boto3 pyyaml

wd="$(pwd)"

pythonFolder="/usr/local/lib/python2.7/site-packages/hesburgh"
if [[ ! -d "$pythonFolder" ]]; then
  ln -s "$wd/py" $pythonFolder
fi

cd js
yarn link
cd ..
