# taken from https://github.com/opencobra/cobrapy/blob/devel/appveyor/build_glpk.py

import os
import sys
# import hashlib
import tarfile
import struct
import shutil
import setuptools.msvc
try:
    import urllib2
except ImportError:  # python 3
    import urllib.request as urllib2


# these need to be set to the latest glpk version
glpk_version = os.getenv('NEW_GLPK_VERSION')
# glpk_md5 = "eda7965907f6919ffc69801646f13c3e"

glpk_build_dir = "glpk_build/glpk-%s" % glpk_version
url = "http://ftp.gnu.org/gnu/glpk/glpk-%s.tar.gz" % glpk_version
bitness = struct.calcsize("P") * 8


# def md5(fname):
#     hash = hashlib.md5()
#     with open(fname, "rb") as f:
#         for chunk in iter(lambda: f.read(4096), b""):
#             hash.update(chunk)
#     return hash.hexdigest()


def get_vcvarsall_cmd():
    py_ver = sys.version_info
    if py_ver.major == 3 and py_ver.minor >= 5:
        vc_ver = 14
    elif py_ver.major == 3 and py_ver.minor >= 3:
        vc_ver = 10
    else:
        vc_ver = 9
    vc_path = setuptools.msvc.msvc9_find_vcvarsall(vc_ver)
    assert vc_path is not None
    command = '"%s"' % vc_path

    if py_ver.major == 2:
        from distutils.msvc9compiler import Reg, WINSDK_BASE
        WIN_SDK_71_PATH = Reg.get_value(os.path.join(WINSDK_BASE, 'v7.1'),
                                        'installationfolder')
        WIN_SDK_71_BAT_PATH = os.path.join(
            WIN_SDK_71_PATH, 'Bin', 'SetEnv.cmd')
        if bitness == 64:
            command = (
                'call "%s" /Release /x64 ' % WIN_SDK_71_BAT_PATH +
                command + ' amd64'
            )

    return command


if not os.path.isdir("glpk_build/"):
    os.mkdir("glpk_build")
if not os.path.isdir(glpk_build_dir):
    response = urllib2.urlopen(url)
    with open("glpk-download.tar.gz", "wb") as outfile:
        outfile.write(response.read())
    # assert md5("glpk-download.tar.gz") == glpk_md5
    with tarfile.open("glpk-download.tar.gz") as infile:
        infile.extractall("glpk_build")

os.chdir("%s/w%d" % (glpk_build_dir, bitness))
if not os.path.isfile("glpk.lib"):
    shutil.copy2("config_VC", "config.h")
    os.system(get_vcvarsall_cmd() + "& nmake /f Makefile_VC")
shutil.copy2("glpk.lib", "../../..")
os.chdir("../../..")
shutil.copy2(glpk_build_dir + "/src/glpk.h", ".")
