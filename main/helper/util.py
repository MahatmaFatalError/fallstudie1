#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import zlib


def string_to_base64(string):
    return base64.b64encode(string.encode('utf-8'))


def base64_to_string(base64_string):
    return base64.b64decode(base64_string).decode('utf-8')


def compress(string):
    return zlib.compress(string)


def decompress(compressed_string):
    return zlib.decompress(compressed_string)


