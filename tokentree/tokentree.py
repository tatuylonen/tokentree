# (Obsolete for now, may be out of sync with the Cython version)
#
# Pure python version of a tree for storing integer tokens with extra data.
#
# Copyright (c) 2018 Tatu Ylonen.  See LICENSE and https://ylonen.org

import math

class Node(object):
    __slots__ = ("token", "next", "count", "extra")

    def __init__(self, token):
        self.token = token
        self.next = None
        self.count = 1
        self.extra = None

    def have_children(self):
        return self.next is not None

    def get_token(self):
        return self.token

    def get_count(self):
        return self.count

    def get_extra(self):
        return self.extra

    def set_extra(self, extra):
        self.extra = extra

    def add(self, new_node):
        token = new_node.token
        n = self.next
        if n is None:
            self.next = new_node
        elif isinstance(n, dict):
            n[token] = new_node
        else:
            self.next = { n.token: n,
                          new_node.token: new_node }
        return new_node

    def iter_next(self):
        n = self.next
        if n is None:
            return
        if isinstance(n, dict):
            for nn in n.values():
                yield nn
            return
        yield n

    def step(self, token):
        dispatch = self.next
        next_node = None
        if isinstance(dispatch, dict):
            next_node = dispatch.get(token, None)
        elif isinstance(dispatch, Node):
            if dispatch.token == token:
                next_node = dispatch
        return next_node


def _dummy_merge(a, b):
    return None

class TokenTree(object):
    """A class for trees of nodes used for parsing.  Any node can have
    additional information attached."""
    __slots__ = (
        "root",
        "token_counts",
        "distinct",
        "creator",
        "merge_extra",
        "merge_final",
    )

    def __init__(self, creator=Node,
                 merge_extra=None, merge_final=None):
        self.root = creator(None)
        self.root.count = 0
        self.distinct = 0
        self.token_counts = {}
        self.creator = creator
        if merge_extra is None:
            merge_extra = _dummy_merge
        if merge_final is None:
            merge_final = _dummy_merge
        self.merge_extra = merge_extra
        self.merge_final = merge_final

    def get_root(self):
        """Returns the root node of the three."""
        return self.root

    def get_count(self):
        """Returns the number of times self.add() has been called."""
        return self.root.count

    def find(self, seq):
        """Looks up a node for the given sequence.  This returns None if the
        sequence does not exist in the tree; otherwise this returns the node
        for the sequence.  This never creates new nodes."""
        assert isinstance(seq, (list, tuple))
        node = self.root
        for token in seq:
            node = node.step(token)
            if node is None:
                return None
        return node

    def add_no_extra(self, seq, count=1):
        """Adds the given sequence to the tree, increasing the counts of the
        nodes on the path.  This adds nodes if the sequence did not
        previously exist.  This returns the node for the sequence.
        If ``extra`` is not None, this calls ``self.merge_extra`` for
        each node in the path and ``self.merge_final`` for the final node
        (if they are not provided, the extra of the last node is set to
        ``extra``, but nothing is done to intermediate nodes)."""
        assert isinstance(seq, (list, tuple, str))
        node = self.root
        distinct = False
        node.count += count
        for token in seq:
            #if token in self.token_counts:
            #    self.token_counts[token] += count
            #else:
            #    self.token_counts[token] = count
            next_node = node.step(token)
            if next_node is None:
                next_node = self.creator(token)
                next_node.count = count
                distinct = True
                n = node.next
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
        if distinct:
            self.distinct += 1
        return node

    def add(self, seq, extra=None, count=1):
        """Adds the given sequence to the tree, increasing the counts of the
        nodes on the path.  This adds nodes if the sequence did not
        previously exist.  This returns the node for the sequence.
        If ``extra`` is not None, this calls ``self.merge_extra`` for
        each node in the path and ``self.merge_final`` for the final node
        (if they are not provided, the extra of the last node is set to
        ``extra``, but nothing is done to intermediate nodes)."""
        assert isinstance(seq, (list, tuple, str))
        node = self.root
        distinct = False
        node.count += count
        node.extra = self.merge_extra(node.extra, extra)
        for i in range(len(seq)):
            token = seq[i]
            if token in self.token_counts:
                self.token_counts[token] += count
            else:
                self.token_counts[token] = count
            next_node = node.step(token)
            if next_node is None:
                next_node = self.creator(token)
                next_node.count = count
                node.add(next_node)
                distinct = True
            else:
                next_node.count += count
            node = next_node
            if i < len(seq) - 1:
                node.extra = self.merge_extra(node.extra, extra)
            else:
                node.extra = self.merge_final(node.extra, extra)
        if distinct:
            self.distinct += 1
        return node

    def chance_loglikelihood(self, seq):
        """Returns the log2 likelihood of any added sequence being this
        particular sequence."""
        assert isinstance(seq, (list, tuple))

        node = self.root
        # If the tree is empty, return 0
        if node.count == 0:
            return 0

        chance_loglikelihood = 0
        logcount = math.log2(node.count)
        for token in seq:
            node = node.step(token)
            if node is None:
                return 0
            total = self.token_counts[token]
            if total == 0:
                return 0
            chance_loglikelihood += math.log2(total) - logcount
        return chance_loglikelihood

    def rel_likelihood(self, seq):
        """Returns log2 of how often the sequence occurs compared to
        the expected number of times it occurs.  Returns 0 if it has not
        occurred."""
        assert isinstance(seq, (list, tuple))
        chance_loglikelihood = self.chance_loglikelihood(seq)
        node = self.find(seq)
        logcount = math.log2(self.root.count)
        actual_loglikelihood = math.log2(node.count) - logcount
        #print("chance_loglikelihood", chance_loglikelihood)
        #print("actual_loglikelihood", actual_loglikelihood)
        return actual_loglikelihood - chance_loglikelihood

    def __iter__(self):
        """Iterates over all sequences of nodes in the tree.  At each
        iteration, this returns ((sequence of tokens), node).  This
        performs a depth-first iteration."""
        def iter_fn():
            q = []
            for next_node in sorted(self.root.iter_next(),
                                    key=lambda x: x.token,
                                    reverse=True):
                q.append(((next_node.token,), next_node))
            while q:
                seq, node = q.pop()
                yield seq, node
                for next_node in sorted(node.iter_next(),
                                        key=lambda x: x.token,
                                        reverse=True):
                    q.append((seq + (next_node.token,), next_node))

        return iter_fn()


if __name__ == "__main__":
    t = Tree()
    t.add((1, 2, 4))
    t.add((3, 2, 1))
    t.add((3, 2, 1))
    t.add((3, 2, 1))
    t.add((3, 2, 1))
    t.add((1, 3, 4))
    t.add((3, 2))
    import random
    import base64
    import time
    count = 100000
    random.seed(1)
    vals = list(tuple(random.randrange(100)
                      for i in range(0, random.randrange(10) + 2))
                for x in range(count))
    start_t = time.time()
    for seq in vals:
        t.add_no_extra(seq)
    dur = time.time() - start_t
    print("{:.3f}us/add; {:.0f} additions/sec"
          "".format(1e6 * dur / count, count / dur))
    import psutil
    import os
    p = psutil.Process(os.getpid())
    print("Memory usage: {:.3f} MB"
          "".format(p.memory_info().rss / 1024 / 1024))
    print(iter(t))
