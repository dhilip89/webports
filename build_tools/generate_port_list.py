#!/usr/bin/env python
# Copyright (c) 2013 The Native Client Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tool for re-generating port list in markdown format
"""

from __future__ import print_function

import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NACLPORTS_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_FILE = os.path.join(NACLPORTS_ROOT, 'docs', 'port_list.md')

sys.path.append(os.path.join(NACLPORTS_ROOT, 'lib'))

import webports
import webports.source_package

SRC_URL = 'https://chromium.googlesource.com/webports/+/master'

header = '''\
# List of available ports

Port are listed in alphabetical order, with links to the upstream
source archive and the patch used when building for NaCl.
This listing is auto-generated by
[generate\_port\_list](%s/bin/generate_port_list).

| **Name** | **Version** | **Upstream Archive** | **NaCl Patch** \
| **Disabled Libc** | **Disabled Arch** |
| :--- | :--- | :--- | :--- | :--- | :--- |
''' % SRC_URL


def make_table_row(pkg):
  patch = os.path.join(pkg.root, 'nacl.patch')
  if os.path.exists(patch):
    size = os.path.getsize(patch)
    if size < 1024:
      patch = '[%d B][%s]' % (size, pkg.NAME + '_patch')
    else:
      patch = '[%d KiB][%s]' % (size / 1024, pkg.NAME + '_patch')
  else:
    patch = ''
  url = '[%s][%s]' % (pkg.get_archive_filename(), pkg.NAME + '_upstream')
  package_url = '[%s]' % pkg.NAME

  disabled_libc = getattr(pkg, 'DISABLED_LIBC')
  if disabled_libc:
    disabled_libc = ', '.join(disabled_libc)

  disabled_arch = getattr(pkg, 'DISABLED_ARCH')
  if disabled_arch:
    disabled_arch = ', '.join(disabled_arch)

  host = pkg.BUILD_OS
  if host:
    host = host + '-only'
  else:
    host = ''
  cols = (package_url, pkg.VERSION, url, patch, disabled_libc, disabled_arch)
  return '| %-25s | %-15s | %-45s | %-20s | %s | %s |\n' % cols


def make_page():
  page = header

  total = 0
  for package in sorted(webports.source_package.source_package_iterator()):
    if package.URL:
      page += make_table_row(package)
    total += 1

  page += '\n_Total = %d_\n\n' % total

  page += '# Local Ports (not based on upstream sources) =\n\n'
  total = 0
  for package in webports.source_package.source_package_iterator():
    if package.URL:
      continue
    page += '- [%s][%s]\n' % (package.NAME, package.NAME)
    total += 1
  page += '\n_Total = %d_\n\n' % total

  # Generate up to tree links for each package at the base of the page
  for package in webports.source_package.source_package_iterator():
    relative_path = os.path.relpath(package.root, NACLPORTS_ROOT)
    page += '[%s]: %s/%s\n' % (package.NAME, SRC_URL, relative_path)

    patch = os.path.join(package.root, 'nacl.patch')
    if os.path.exists(patch):
      relative_path = os.path.relpath(patch, NACLPORTS_ROOT)
      page += '[%s_patch]: %s/%s\n' % (package.NAME, SRC_URL, relative_path)

    if package.URL:
      page += '[%s_upstream]: %s\n' % (package.NAME, package.URL)

  return page


def main(argv):
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('-v', '--verbose', action='store_true',
                      help='Output extra information.')
  parser.add_argument('-o', '--output', default=OUTPUT_FILE,
                      help='Output file.')
  args = parser.parse_args(argv)
  with open(args.output, 'w') as f:
    f.write(make_page())
  return 0


if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
