# -*- python -*-
#
# Optimized tree of integer tokens with counts and optional extra data.
# This is intended as a component for various machine learning applications.
#
# Copyright (c) 2018 Tatu Ylonen.  See LICENSE and https://ylonen.org

import math


def count_merge(ht, key, count):
    """Merges new extra data to existing extra data in a node."""
    if ht is None:
        return {key: count}
    if key in ht:
        ht[key] += count
        return ht
    ht[key] = count
    return ht


cdef class Node(object):
    cdef public double count
    cdef public int token
    cdef public object next
    cdef public object extra

    def __init__(self, int token):
        self.token = token
        self.next = None
        self.count = 0
        self.extra = None

    cpdef have_children(self):
        """Returns True if the node has children."""
        return self.next is not None

    cpdef get_token(self):
        """Returns the token of the node (an integer)."""
        return self.token

    cpdef get_count(self):
        """Returns the count of the node.  Note that this is floating point."""
        return self.count

    cpdef get_extra(self):
        """Returns extra data associated with the node (the return value
        of the last call to merge_extra or merge_final for the node)."""
        return self.extra

    def __iter__(self):
        """Iterates over children of the node."""
        n = self.next
        if n is None:
            return
        if isinstance(n, dict):
            for nn in n.values():
                yield nn
            return
        yield n


def _dummy_merge(a, b, count):
    return None


cdef class TokenTree(object):
    """A class for trees of nodes used for parsing.  Any node can have
    additional information attached."""
    cdef object root
    cdef dict token_counts
    cdef object merge_extra
    cdef object merge_final

    def __init__(self, merge_extra=None, merge_final=None):
        self.root = Node(0)
        self.root.count = 0
        self.token_counts = {}
        if merge_extra is None:
            merge_extra = _dummy_merge
        if merge_final is None:
            if merge_extra:
                merge_final = merge_extra
            else:
                merge_final = _dummy_merge
        self.merge_extra = merge_extra
        self.merge_final = merge_final

    def _add_no_extra(self, seq, double count):
        """Adds without extra data."""
        assert isinstance(seq, (tuple, list))
        node = self.root
        node.count += count
        for i in range(len(seq)):
            token = seq[i]
            # Look up the next node
            next_node = None
            n = node.next
            if isinstance(n, dict):
                next_node = n.get(token, None)
            elif isinstance(n, Node):
                if n.token == token:
                    next_node = n
            # Increment the count of all nodes (doing this here in between
            # seems to improve performance by about 5% - probably due to
            # memory latencies)
            if token in self.token_counts:
                self.token_counts[token] += count
            else:
                self.token_counts[token] = count
            # If we didn't get a node, create a new one.  Otherwise increment
            # its count.
            if next_node is None:
                next_node = Node(token)
                next_node.count = count
                if n is None:
                    node.next = next_node
                elif isinstance(n, dict):
                    n[token] = next_node
                else:
                    node.next = { n.token: n,
                                  token: next_node }
            else:
                next_node.count += count
            node = next_node
        return node

    def _add_with_extra(self, seq, extra, double count):
        """Adds with extra data."""
        assert isinstance(seq, (tuple, list))
        node = self.root
        node.count += count
        node.extra = self.merge_extra(node.extra, extra, count)
        for i in range(len(seq)):
            token = seq[i]
            # Look up the next node
            next_node = None
            n = node.next
            if isinstance(n, dict):
                next_node = n.get(token, None)
            elif isinstance(n, Node):
                if n.token == token:
                    next_node = n
            # Increment the count of all nodes (doing this here in between
            # seems to improve performance by about 5% - probably due to
            # memory latencies)
            if token in self.token_counts:
                self.token_counts[token] += count
            else:
                self.token_counts[token] = count
            # If we didn't get a node, create a new one.  Otherwise increment
            # its count.
            if next_node is None:
                next_node = Node(token)
                next_node.count = count
                if n is None:
                    node.next = next_node
                elif isinstance(n, dict):
                    n[token] = next_node
                else:
                    node.next = { n.token: n,
                                  token: next_node }
            else:
                next_node.count += count
            node = next_node
            if i < len(seq) - 1:
                node.extra = self.merge_extra(node.extra, extra, count)
            else:
                node.extra = self.merge_final(node.extra, extra, count)
        return node

    def add(self, seq, extra=None, double count=1):
        """Adds the given sequence to the tree, increasing the counts of the
        nodes on the path.  This adds nodes if the sequence did not
        previously exist.  This returns the node for the sequence.
        If ``extra`` is not None, this calls ``self.merge_extra`` for
        each node in the path and ``self.merge_final`` for the final node
        (if they are not provided, the extra of the last node is set to
        ``extra``, but nothing is done to intermediate nodes)."""
        if extra is not None:
            self._add_with_extra(seq, extra, count)
        else:
            self._add_no_extra(seq, count)

    def get_root(self):
        """Returns the root node of the three."""
        return self.root

    def get_count(self):
        """Returns the number of times self.add() has been called."""
        return self.root.count

    def get_token_count(self, token):
        """Returns the number of time the given token has been added (in
        any position in any sequence)."""
        assert isinstance(token, int)
        if token in self.token_counts:
            return self.token_counts[token]
        return 0

    def find(self, seq):
        """Looks up a node for the given sequence.  This returns None if the
        sequence does not exist in the tree; otherwise this returns the node
        for the sequence.  This never creates new nodes."""
        assert isinstance(seq, (list, tuple))
        node = self.root
        for token in seq:
            n = node.next
            next_node = None
            if isinstance(n, dict):
                next_node = n.get(token, None)
            elif isinstance(n, Node):
                if n.token == token:
                    next_node = n
            if next_node is None:
                return None
            node = next_node
        return node

    def __iter__(self):
        """Iterates over all sequences of nodes in the tree.  At each
        iteration, this returns ((sequence of tokens), node).  This
        performs a depth-first iteration."""
        def iter_fn():
            q = []
            for next_node in sorted(self.root,
                                    key=lambda x: x.token,
                                    reverse=True):
                q.append(((next_node.token,), next_node))
            while q:
                seq, node = q.pop()
                yield seq, node
                for next_node in sorted(node,
                                        key=lambda x: x.token,
                                        reverse=True):
                    q.append((seq + (next_node.token,), next_node))

        return iter_fn()
