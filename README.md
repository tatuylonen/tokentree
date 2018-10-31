# Tokentree

An optimized tree of integer tokens with counts and extra data in each node

## Overview

This package provides an optimized tree structure containing integer tokens
and extra data associated with them.  This is intended for supporting
certain machine learning applications involving strings and grammatical
learning.

## Getting started

### Installation

For now, install from the [github repository](https://github.com/tatuylonen/tokentree).

### Running tests

This package includes tests written using the ``unittest`` framework.
They can be run using, for example, ``nose``, which can be installed
using ``pip3 install nose``.

To run the tests, just use the following command in the top-level directory:
```
nosetests
```

## Usage

### Adding data to a tree

To create a tree and add sequences, use something like the following:
```
from tokentree import TokenTree

t = TokenTree()
t.add((1, 2, 3))
t.add((1, 3, 8, 10))
```

The tree is designed to accomodate millions or even hundreds of
millions of values.  Insertion time is linear in the length of the
sequence.  The sequences can consist of arbitrary integers, positive
or negative.  Tokens must fit in a 64-bit integer.

It is possible to store extra data with each node.  Functions for
merging extra data with each node are provided as arguments the
constructor (see below).  The extra data is provided as the ``extra``
keyword argument to ``add``.

It is also possible to specify a count or weight for each addition.
This value will be added to the count of each node in the path.  The
value is stored as a floating point number and defaults to 1.  The
optional count is specified with the ``count`` keyword argument to
``add``.

The following illustrates adding with extra data and weight:
```
t.add(seq, count=3.5, extra="noun")
```

### Creating a tree

The tree is created using the ``TokenTree()`` constructor.  This
constructor accepts the following keyword arguments:

* ``merge_extra``: a function to merge the ``extra`` argument in a
  newly added node to the information already in a tree node.  The
  function is called as ``merge_extra(old_data, extra, count)``.  For the
  first call, ``old_data`` will be None.  This should return the new
  data.  Default is ``None``.
* ``merge_final``: like ``merge_extra``, but this function is used for
  the last node of the sequence.  It defaults to ``merge_extra`` if
  not specified or ``None``.

Note that ``merge_extra`` adds ``extra`` to each node on the path,
whereas ``merge_final`` only adds it to the final node.  If only
``merge_extra`` is provided, then ``merge_final`` defaults to
``merge_extra``.

For convenience, a function ``tokentree.count_merge`` is provided,
which will maintain in each node a dictionary keyed by the ``extra``,
whose value is the sum of all ``count`` arguments from the additions
with that value for ``extra``.  It requires ``extra`` to be a hashable
value.

### Enumerating sequences from the tree

The tree works as an iterator.  This makes it very easy to enumerate
through all paths in the tree.  The enumerator will also enumerate
through all prefixes of sequences that were added to the tree.  It is
guaranteed that the prefix of a sequence will always be enumerated
before any longer sequences with the same prefix.  In effect, the
iteration is in depth-first order.  Within each prefix, the sequences
of the next length are enumerated in ascending order of their token
values.

The following illustrates enumerating the sequences.  For each
iteration, the iterator returns ``(seq, node)``, where ``seq`` is a
tuple of integers, and ``node`` is the node at that sequence.

```
import tokentree
t = TokenTree()
t.add((1, 2))
...
for seq, node in t:
    print(node.get_count(), seq)
```

### Looking up a specific sequence

The ``find`` function looks up a specific sequence from the tree.  It is
possible to look up added sequences and their prefixes.  It returns ``None``
if the given sequence is not in the tree.

```
import tokentree
t = TokenTree()
t.add((1, 2))
...
node = t.find(seq)
if node is None:
    print("Not found")
print(node.get_count(), node.get_token(), node.get_extra())
```

### Counting tokens

The ``get_token_count(token)`` method on the tree returns the number
of times that the given token has been added to the tree (in any
position in any sequence), or when ``count`` is used when adding, the
sum of all counts for all occurrences of the token.

This function merely retrieves precomputed data, so it is quite fast.

### Tree-level information functions

The ``get_root()`` method returns the root node of the tree.  The root
node always exists and corresponds to the empty sequence.

The ``get_count()`` method returns the sum of all weights added to the
tree.  it is the same as the value of ``get_count()`` on the root
node.

### Node-level information and iteration functions

A node is mostly opaque for applications.  However, the following functions
can be used to query information about a node.

The ``have_children()`` method on a node returns ``True`` if the node
has children, and ``False`` otherwise.

The ``get_token()`` method on a node returns the token of the node.  The token
is always an integer value (but can be negative).

The ``get_count()`` method on a node returns the count value of the
node.  The count is the sum of the ``count`` values of all sequences
that have been added that have the sequence leading to the node as
their prefix (including the count value for the sequence of the node).

### Iterating over children of a node

It is possible to iterate over the children of the node by simply using the
node as an iterator.  The following illustrates this:
```
import tokentree
t = TokenTree()
t.add([1, 3, 4])
...
node = t.find([1, 3])
for child in node:
    print(child.get_count(), child.get_token())
```

## Contributing

The official repository of this project is on
[github](https://github.com/tatuylonen/tokentree).

Please email to ylo at clausal.com if you wish to contribute or have
patches or suggestions.

## License

Copyright (c) 2018 [Tatu Ylonen](https://ylonen.org).  This package is
free for both commercial and non-commercial use.  It is licensed under
the MIT license.  See the file
[LICENSE](https://github.com/tatuylonen/tokentree/blob/master/LICENSE)
for details.

Credit and linking to the project's website and/or citing any future
papers on the project would be highly appreciated.
