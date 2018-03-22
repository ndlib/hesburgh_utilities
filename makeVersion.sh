
pushd py
# set version first
  python setup.py bdist_wheel
  twine upload dist/*
popd

pushd js
# set version first
  npm publish
popd