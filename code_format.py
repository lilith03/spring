#! /usr/bin/python
# coding: utf-8

from yapf.yapflib.yapf_api import FormatFile


def process(file_name):
    FormatFile(file_name, in_place=True)


if __name__ == '__main__':
    process('/Users/apple/spring/code_format.py')
