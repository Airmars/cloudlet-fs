#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

import logging

from xmlrpclib import Binary
import xmlrpclib

from errno import EACCES
from os.path import realpath
from sys import argv, exit
from threading import Lock

import os

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

class Loopback(LoggingMixIn, Operations):
    def __init__(self, serverip="127.0.0.1", serverport="42014"):
        self.serverip = serverip
        self.serverport = serverport
        serveraddress = 'http://{}:{}'.format(serverip, serverport)
        print("Connecting to " + serveraddress)
        self.server = xmlrpclib.ServerProxy(serveraddress)

    def open(self, filename, flags, mode=0777):
      return self.server.open(filename, flags, mode)

    #def access(self, path, mode):
    #    if not os.access(path, mode):
    #        raise FuseOSError(EACCES)

    def chmod(self, path, mode):
      return self.server.chmod(path, mode)

    #def create(self, path, mode):
    #    return os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)

    #def flush(self, path, fh):
    #    return os.fsync(fh)

    #def fsync(self, path, datasync, fh):
    #    if datasync != 0:
    #      return os.fdatasync(fh)
    #    else:
    #      return os.fsync(fh)

    def getattr(self, path, fd=None):
      (success, rval) = self.server.lstat(path)
      if success: return rval
      else: raise FuseOSError(rval)

    #getxattr = None

    #def link(self, target, source):
    #    return os.link(source, target)

    #listxattr = None
    #mkdir = os.mkdir
    #mknod = os.mknod
    #open = os.open

    def read(self, path, size, offset, fd):
        self.server.lseek(fd, offset, 0)
        return self.server.read(fd, size).data

    def readdir(self, path, fh):
      return self.server.readdir(path, fh)

    #readlink = os.readlink

    #def release(self, path, fh):
    #    return os.close(fh)

    def rename(self, old, new):
        return self.server.rename(old, new)

    def rmdir(self, path):
      return self.server.rmdir(path)

    #def statfs(self, path):
    #    stv = os.statvfs(path)
    #    return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
    #        'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
    #        'f_frsize', 'f_namemax'))

    #def symlink(self, target, source):
    #    return os.symlink(source, target)

    #def truncate(self, path, length, fh=None):
    #    with open(path, 'r+') as f:
    #        f.truncate(length)

    def unlink(self, path):
      return self.server.unlink(path)

    #utimens = os.utime

    def write(self, path, data, offset, fd):
      self.server.lseek(fd, offset, 0)
      return self.server.write(fd, Binary(data))

if __name__ == '__main__':
    if len(argv) < 2:
        print('Usage: %s MOUNTPOINT [SERVERIP] [SERVERPORT]' % argv[0])
        exit(1)

    logging.basicConfig(level=logging.WARN)
    fuse = FUSE(Loopback(*argv[2:]), argv[1], foreground=True)
