#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import socket
import struct
import progressbar
from cia_info import ciaTitleSerial

class Express(object):
    def __init__(self, host, filepath):
        super(Express, self).__init__()
        self.host = host
        self.filepath = filepath

    def FileInfo(self, filepath):
        filename = os.path.splitext(filepath)[0]
        filesize = os.path.getsize(filepath)
        print('Filename: ' + filename + '\tFilesize: ' + self.ReadableSize(filesize))
        return filename, filesize

    def ReadableSize(self, size, precision = 2):
        suffixes=[' B', ' KB', ' MB', ' GB']
        suffixIndex = 0
        while size > 1024 and suffixIndex < 4:
            suffixIndex += 1
            size = size/1024.0
        return "%.*f%s"%(precision, size, suffixes[suffixIndex])

    def SendFile(self):
        filename, filesize = self.FileInfo(self.filepath)
        trunksize = 1024 * 128
        filesizebyte = struct.pack('>Q', filesize)

        titleid, serial = ciaTitleSerial(self.filepath)
        print('Title ID: ' + titleid + '\tSerial: ' + serial)

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect((self.host, 5000))
        except Exception as e:
            raise e

        try:
            f = open(self.filepath, 'rb')
            l = f.read(trunksize)
            progress = progressbar.AnimatedProgressBar(end = os.path.getsize(self.filepath) + len(filesizebyte), width = 70)
            s.send(filesizebyte)
            while l:
                s.send(l)
                l = f.read(trunksize)
                progress + trunksize
                progress.show_progress()
            f.close()
            s.close()
            print('\n\nFile transfer success.')
        except Exception as e:
            f.close()
            s.close()
            print('\n\nFile transfer failed.')
            raise e

def main():
    if len(sys.argv) != 3 or sys.argv[1] == '-h':
        print('Usage: ' + sys.argv[0] + ' <ip> <file>\n(E.g: ./sockfilepy.py 192.168.1.51 mario.cia)')
        return
    if not (os.path.isfile(sys.argv[2]) and (os.path.splitext(sys.argv[2])[1] == '.cia')):
        print('Sorry, cia file not found.')
        return
    host = sys.argv[1]
    filepath = sys.argv[2]
    Express(host, filepath).SendFile()

if __name__ == '__main__':
    main()