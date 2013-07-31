#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# The MIT License
# 
# Copyright (c) 2009-2011 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from io import BytesIO
import gzip
import os
import subprocess
import tarfile
import tempfile


def create_default_sdist(project_dir):
    dist_files = set()
    dist_dir = os.path.join(project_dir, 'dist')
    if os.path.exists(dist_dir):
        dist_files = set(os.listdir(dist_dir))
    
    subprocess.check_call(['python', 'setup.py', 'sdist'], cwd=project_dir,
        stdout=subprocess.PIPE)
    new_dist_files = set(os.listdir(dist_dir)) - dist_files
    assert len(new_dist_files) == 1, 'did you remember to delete any preexisting .tar.gz in dist?'
    sdist_filename = new_dist_files.pop()
    return sdist_filename

def build_documentation(project_dir):
    doc_dir = os.path.join(project_dir, 'docs')
    temp_file = tempfile.TemporaryFile()
    # We don't need any output on stdout
    subprocess.call(['make', 'html'], cwd=doc_dir, stdout=temp_file)

def make_relative_filename(topdir, filename):
    assert filename.startswith(topdir)
    relative_filename = filename[len(topdir):]
    if relative_filename.startswith(os.sep):
        relative_filename = relative_filename[len(os.sep):]
    return relative_filename

def make_tarname(topdir, filename, path_prefix):
    relative_name = make_relative_filename(topdir, filename)
    tarname = '%s/%s' % (path_prefix, relative_name)
    return tarname

def add_file(tar, filename, arcname, project_dir, path_prefix):
    tarname = make_tarname(project_dir, filename, path_prefix)
    if arcname is not None:
        tarname = make_tarname(project_dir, arcname, path_prefix)
    tar.add(filename, arcname=tarname)

def build_fname_with_changed_path_prefix(project_dir, root, arcname, basename):
    nr_of_dirs = lambda path: len(path.split('/'))
    relative_root = make_relative_filename(project_dir, root)
    assert nr_of_dirs(arcname) <= nr_of_dirs(relative_root), 'Untested'
    
    offset_path_items = relative_root.split('/')[nr_of_dirs(arcname):]
    offset_path = os.path.join(arcname, *offset_path_items)
    tar_fname = os.path.join(project_dir, offset_path, basename)
    return tar_fname

def add_files_below_directory(tar, dirname, arcname, project_dir, path_prefix):
    for (root, dirs, files) in os.walk(dirname):
        for basename in files:
            if basename.endswith('.pyc'):
                continue
            fname = os.path.join(root, basename)
            tar_fname = fname
            if arcname is not None:
                tar_fname = build_fname_with_changed_path_prefix(project_dir, root, arcname, basename)
            tarname = make_tarname(project_dir, tar_fname, path_prefix)
            tar.add(fname, tarname)

def clone_tar(gzip_fp):
    target_fp = BytesIO()
    
    source_fp = BytesIO()
    source_fp.write(gzip_fp.read())
    source_fp.seek(0)
    source_tar = tarfile.open(fileobj=source_fp, mode='r')
    tar = tarfile.open(fileobj=target_fp, mode='w|gz')
    for tarinfo in source_tar.getmembers():
        member_fp = source_tar.extractfile(tarinfo)
        tar.addfile(tarinfo, fileobj=member_fp)
    source_tar.close()
    
    return (target_fp, tar)

def add_package_files_to_tarball(source_tar_fp, project_dir, package_files, path_prefix):
    target_fp, tar = clone_tar(source_tar_fp)
    for filename in package_files:
        arcname = None
        if not isinstance(filename, basestring):
            filename, arcname = filename
        filename = os.path.join(project_dir, filename)
        if os.path.isfile(filename):
            add_file(tar, filename, arcname, project_dir, path_prefix)
        else:
            add_files_below_directory(tar, filename, arcname, project_dir, path_prefix)
    tar.close()
    target_fp.seek(0,0)
    return target_fp

def get_name_and_version():
    release_info = {}
    execfile(os.path.join('pycerberus', 'release.py'), release_info)
    return (release_info['name'], release_info['version'])

def main():
    name, version = get_name_and_version()
    this_dir = os.path.abspath(os.path.dirname(__file__))
    
    sdist_filename = create_default_sdist(this_dir)
    build_documentation(this_dir)
    package_files = [('build/html', 'docs/html')]
    
    sdist_path = os.path.join(this_dir, 'dist', sdist_filename)
    tar_fp = gzip.open(sdist_path)
    # LATER: should compute the prefix automatically
    path_prefix = '%s-%s' % (name, version)
    targz_fp = add_package_files_to_tarball(tar_fp, this_dir, package_files, path_prefix)
    
    gz_filename = os.path.basename(sdist_filename)
    file(gz_filename, 'wb').write(targz_fp.read())

if __name__ == '__main__':
    main()


