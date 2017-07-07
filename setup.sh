pip install boto3 pyyaml

wd="$(pwd)"

pythonFolder=`python -c "from distutils.sysconfig import get_python_lib; print
get_python_lib()"`
if [[ ! -d "$pythonFolder" ]]; then
  ln -s "$wd/py" $pythonFolder
fi

cd js
yarn link
cd ..
