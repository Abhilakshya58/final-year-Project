import itertools
import operator
import os
import string

from collections import deque, namedtuple

from . import data


def write_tree (directory='.'):
    entries = []
    with os.scandir (directory) as it:
        for entry in it:
            full = f'{directory}/{entry.name}'
            if is_ignored (full):
                continue

            if entry.is_file (follow_symlinks=False):
                type_ = 'blob'
                with open (full, 'rb') as f:
                    oid = data.hash_object (f.read ())
            elif entry.is_dir (follow_symlinks=False):
                type_ = 'tree'
                oid = write_tree (full)
            entries.append ((entry.name, oid, type_))

    tree = ''.join (f'{type_} {oid} {name}\n'
                    for name, oid, type_
                    in sorted (entries))
    return data.hash_object (tree.encode (), 'tree')


def _iter_tree_entries (oid):
    if not oid:
        return
    tree = data.get_object (oid, 'tree')
    for entry in tree.decode ().splitlines ():
        type_, oid, name = entry.split (' ', 2)
        yield type_, oid, name


def get_tree (oid, base_path=''):
    result = {}
    for type_, oid, name in _iter_tree_entries (oid):
        assert '/' not in name
        assert name not in ('..', '.')
        path = base_path + name
        if type_ == 'blob':
            result[path] = oid
        elif type_ == 'tree':
            result.update (get_tree (oid, f'{path}/'))
        else:
            assert False, f'Unknown tree entry {type_}'
    return result


def _empty_current_directory ():
    for root, dirnames, filenames in os.walk ('.', topdown=False):
        for filename in filenames:
            path = os.path.relpath (f'{root}/{filename}')
            if is_ignored (path) or not os.path.isfile (path):
                continue
            os.remove (path)
        for dirname in dirnames:
            path = os.path.relpath (f'{root}/{dirname}')
            if is_ignored (path):
                continue
            try:
                os.rmdir (path)
            except (FileNotFoundError, OSError):
                # Deletion might fail if the directory contains ignored files,
                # so it's OK
                pass


def read_tree (tree_oid):
    _empty_current_directory ()
    for path, oid in get_tree (tree_oid, base_path='./').items ():
        os.makedirs (os.path.dirname (path), exist_ok=True)
        with open (path, 'wb') as f:
            f.write (data.get_object (oid))


def commit (message):
    commit = f'tree {write_tree ()}\n'

    HEAD = data.get_ref ('HEAD')
    if HEAD:
        commit += f'parent {HEAD}\n'

    commit += '\n'
    commit += f'{message}\n'

    oid = data.hash_object (commit.encode (), 'commit')

    data.update_ref ('HEAD', oid)

    return oid


def checkout(oid):
    # Resolve tag to OID if necessary
    ref_path = f'{data.GIT_DIR}/refs/tags/{oid}'
    if os.path.isfile(ref_path):  # Check if it's a tag
        with open(ref_path) as f:
            oid = f.read().strip()  # Resolve to the actual OID

    # Proceed with the resolved OID
    commit = get_commit(oid)
    read_tree(commit.tree)
    data.update_ref('HEAD', oid)


def create_tag (name, oid):
    data.update_ref (f'refs/tags/{name}', oid)


Commit = namedtuple ('Commit', ['tree', 'parent', 'message'])


def get_commit (oid):
    parent = None

    commit = data.get_object (oid, 'commit').decode ()
    lines = iter (commit.splitlines ())
    for line in itertools.takewhile (operator.truth, lines):
        key, value = line.split (' ', 1)
        if key == 'tree':
            tree = value
        elif key == 'parent':
            parent = value
        else:
            assert False, f'Unknown field {key}'

    message = '\n'.join (lines)
    return Commit (tree=tree, parent=parent, message=message)


def iter_commits_and_parents (oids):
    oids = deque (oids)
    visited = set ()

    while oids:
        oid = oids.popleft ()
        if not oid or oid in visited:
            continue
        visited.add (oid)
        yield oid

        commit = get_commit (oid)
        # Return parent next
        oids.appendleft (commit.parent)


def get_oid (name):
    if name == '@': name = 'HEAD'

    # Name is ref
    refs_to_try = [
        f'{name}',
        f'refs/{name}',
        f'refs/tags/{name}',
        f'refs/heads/{name}',
    ]
    for ref in refs_to_try:
        if data.get_ref (ref):
            return data.get_ref (ref)

    # Name is SHA1
    is_hex = all (c in string.hexdigits for c in name)
    if len (name) == 40 and is_hex:
        return name

    assert False, f'Unknown name {name}'


def is_ignored (path):
    return '.ugit' in path.split ('/')




