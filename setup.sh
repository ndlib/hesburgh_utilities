wd="$(pwd)"
ln -s $wd/py "/usr/local/lib/python2.7/site-packages/hesburgh"

cd js
yarn link
cd ..
