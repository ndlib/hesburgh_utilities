import zipfile
import os
import imp

from hesburgh import heslog


def NOOP():
  pass

########### WALK
def walk(filefolder):
  toSearch = filefolder if type(filefolder) is str else filefolder.get("")

  if os.path.isfile(filefolder):
    realPath = filefolder
    yield realPath, os.path.basename(realPath)
  elif os.path.isdir(filefolder):
    for root, dirs, files in os.walk(filefolder, followlinks=True):
      for file in files:
        realPath = os.path.join(root, file)
        yield realPath, file
  else:
    heslog.error("Trying to walk %s that is neither file nor folder" % filefolder)


########### ZIP
def zipDir(zipf, toZip):
  for realPath, filename in walk(toZip):
    archivePath = os.path.relpath(realPath, '..')
    heslog.verbose("%s => %s" % (realPath, archivePath))
    zipf.write(realPath, archivePath)


def makeZip(zipName, paths):
  zipf = zipfile.ZipFile(zipName, 'w', zipfile.ZIP_DEFLATED)
  heslog.verbose("Make zip %s" % zipName)
  for path in paths:
    zipDir(zipf, path)
  zipf.close()


# pre/post scripts - imports source file and runs the "run" function within
def runScript(scriptFile, **kwargs):
  mod = imp.load_source('tmp', scriptFile)
  return mod.run(**kwargs)
