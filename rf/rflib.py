#!/usr/bin/env python
""" rf - A framework for collaborative computational research

    Copyright (C) 2015 Apua Paquola <apuapaquola@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import argparse
import os
import subprocess

__author__ = 'Apua Paquola'


def is_ready_to_run(node):
    """Tests if a node is ready to run.

    Args:
        node: a directory (node)
    Returns:
        bool: True if the node is ready to run, i.e., if it has no _/ dir and if there is an executable driver script at __/
    """
    return node is not None and \
           os.path.isdir(node + '/__') and \
           not os.path.exists(node + '/_') and \
           os.access(node + '/__/driver', os.X_OK)


def find_dependencies(node, recursive):
    """Finds the human directories __/ in a subtree, and .

    Args:
        node (str): a node at the root of the tree.
        recursive (bool): whether to look at the entire tree recursively.

    Yields:
        (list, str): a tuple that contains a list of dependencies and a node, for each node of the tree that is ready to run.

    """
    assert os.path.isdir(node)
    queue = [(None, node)]
    while queue:
        (parent, child) = queue.pop(0)

        l = list(dependency_links(child))
        dependencies = [x for x in [parent] + l \
                        if x is not None and \
                        is_ready_to_run(os.path.realpath(x)) and \
                        belongs_to_tree(x, node)]

        if is_ready_to_run(os.path.realpath(child)) and \
           belongs_to_tree(child, node):
            yield (dependencies, child)

        if recursive:
            queue.extend(((child, xx) for xx in filter(os.path.isdir, (os.path.join(child,x) for x in os.listdir(child) if x not in ['_','__']))))


def nohup_out(node):
    return node + '/_/nohup.out'


def rule_string(dependencies, node):
    """Generates a makefile rule for a node given its dependencies.

    Args:
        dependencies (list of str): list of nodes
        node (str): the base directory of the node

    Returns:
        str: a makefile rule specifying how to generate the machine directory
            of the current node, given the its dependencies.
    """

    dep_string = ' '.join((nohup_out(x) for x in dependencies))
    return '''.ONESHELL:
%s: %s
\tdate
\tmkdir %s/_
\tcd %s/_
\tnohup ../__/driver

''' % (nohup_out(node), dep_string, node, node)


def dependency_links(node):
    """Finds out the dependencies of a given node and yields them one by one.

    Args:
        node (str): a tree node.

    Yields:
        str: a node that is a dependency of node.

    """

    depdir = node+'/__/dep'
    if os.path.isdir(depdir):
        for x in os.listdir(depdir):
            if os.path.islink(depdir+'/'+x) and os.path.isdir(depdir+'/'+x):
                yield os.path.realpath(depdir+'/'+x)


def belongs_to_tree(dirname, basedir):
    """Tests if a node belongs to a tree.

    Args:
        dirname (str): a directory (node)
    Returns:
        bool: True if the node is under basedir.

    """
    assert os.path.isdir(dirname) and os.path.isdir(basedir)
    return (os.path.realpath(dirname)+'/').startswith(os.path.realpath(basedir)+'/')


def makefile(dependency_iter):
    """Generates a makefile given a list of tuples specifying nodes and dependencies.

    Args:
        dependency_iter (iterable on list of tuples): output of find_human_dirs
    Returns:
        str: a makefile

    """
    dependency_set = set()
    child_set = set()

    makefile_string = ''
    for (dependencies, child) in dependency_iter:
        makefile_string += rule_string(dependencies, child)

        for p in dependencies:
            dependency_set.add(p)

        child_set.add(child)

    for node in dependency_set.difference(child_set):
        makefile_string += rule_string([], node)

    makefile_string = 'all: ' + ' '.join(map(nohup_out, dependency_set.union(child_set))) + \
               '\n\n' + makefile_string

    return makefile_string


def run_make(makefile_string):
    """Runs make on makefile_string
    :param makefile_string:
    :return:
    """
    p = subprocess.Popen(['make', '-f', '-'], stdin=subprocess.PIPE)

    p.stdin.write(makefile_string.encode())
    p.stdin.close()
    p.wait()


def run(args):
    run_make(makefile(find_dependencies(os.path.realpath(args.node), args.recursive)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('node')
    parser.add_argument('--dry-run', '-n', action='store_true', default=False)
    parser.add_argument('--verbose', '-v', action='store_true', default=False)
    parser.add_argument('--recursive', '-r', action='store_true', default=False)
    args = parser.parse_args()

    run(args)


if __name__ == "__main__":
    main()