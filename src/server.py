#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from xmlrpclib import Binary
from sys import argv, exit
from exceptions import OSError

import os

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class FuseServer(object):
  def __init__(self, root, serverip="", serverport=42014):
    self.server = SimpleXMLRPCServer((serverip, int(serverport)), 
                                     requestHandler=RequestHandler, logRequests=False)
    self.server.register_instance(FSInterface(root))
    print("Listening on port {}".format(str(serverport)))
    self.server.serve_forever()

class FSInterface(object):
  def __init__(self, root):
    self.root = root

  def chmod(self, path, mode):
    print("chmod", path, mode)
    try:
      os.chmod(self.root + path, mode)
      return (True, 0)
    except OSError as e:
      return (False, e.errno)

  def chown(self, path, mode):
    print("chown", path, mode)
    return os.chown(self.root + path, mode)

  def close(self, fd):
    print ("close", fd)
    return os.close(fd)

  def ftruncate(self, path, length):
    print ("ftruncate", path, length)
    try:
      fd = os.open(self.root + path, 0, 0) 
      return (True, os.ftruncate(fd, length))
    except OSError as e:
      return (False, e.errno)

  def open(self, path, flags, mode=0777):
    print("open", path, flags, mode)
    return os.open(self.root + path, flags, mode)

  def lseek(self, fd, pos, how):
    print("lseek", fd, pos, how)
    return os.lseek(fd, pos, how)

  def lstat(self, path):
    #print("lstat", path)
    try:
      st = os.lstat(self.root + path)
      return (True, dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
          'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid')))
    except OSError as e:
      return (False, e.errno) 

  def mkdir(self, path, mode):
    print("mkdir", path, mode)
    os.mkdir(self.root + path, mode)
    return 0

  def read(self, fd, n):
    print("read", fd, n)
    return Binary(os.read(fd, n))

  def readdir(self, path, fh):
    #print("readdir", path, fh)
    return ['.', '..'] + os.listdir(self.root + path)

  def readlink(self, path):
    print("readlink", path)
    return os.readlink(self.root + path)

  def rename(self, old, new):
    print("rename", old, new)
    return os.rename(self.root + old, self.root + new) 

  def rmdir(self, path):
    print("rmdir", path)
    os.rmdir(self.root + path)
    return 0

  def unlink(self, path):
    print("unlink", path)
    os.unlink(self.root + path)
    return 0

  def write(self, fd, data):
    return os.write(fd, data.data)

if __name__ == "__main__":
  if len(argv) < 2:
    print('Usage: %s ROOT [SERVERIP] [SERVERPORT]' % argv[0])
    exit(1)

  f = FuseServer(*argv[1:])
