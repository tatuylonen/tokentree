import time
import pickle
import random
import base64
import unittest
from tokentree import TokenTree

import psutil
import os

class TreeTests(unittest.TestCase):

    def test_simple(self):
        t = TokenTree()
        t.add((1, 2, 4))
        t.add((3, 2, 1))
        t.add((3, 2, 1))
        t.add((3, 2, 1))
        t.add((3, 2, 1))
        t.add((1, 3, 4))
        t.add((3, 2))
        assert t.get_root()
        assert t.get_count() == 7
        assert t.find((5, 6)) is None
        assert t.find((3, 2)) is not None
        assert t.find([3,]) is not None
        lst = list(x for x in t)
        seen = set()
        vals = set()
        for seq, node in lst:
            assert isinstance(seq, tuple)
            assert seq[0] in (1, 3)
            assert seq not in seen
            if len(seq) > 1:
                assert seq[:-1] in seen
            seen.add(seq)
            assert len(seq) > 1 or node.have_children()
            assert len(seq) < 3 or not node.have_children()
            vals.add(node.get_token())
            assert node.get_count() >= 1
            assert node.get_count() <= 5
            assert node.have_children() or node.get_count() <= 4
        assert list(sorted(vals)) == [1, 2, 3, 4]

    def test_random(self):
        count = 100000
        vals = list(tuple(random.randrange(100)
                          for i in range(0, random.randrange(10) + 2))
                    for x in range(count))
        start_t = time.time()
        t = TokenTree()
        for seq in vals:
            t.add(seq)
        dur = time.time() - start_t
        print("{:.3f}us/add; {:.0f} additions/sec"
            "".format(1e6 * dur / count, count / dur))
        p = psutil.Process(os.getpid())
        mb = p.memory_info().rss / 1024 / 1024
        print("Memory usage: {:.3f} MB"
              "".format(mb))
        assert mb < 100
        assert count / dur > 50000  # Might fail on a slow machine

    def test_pickle(self):
        t = TokenTree()
        t.add((1, 2, 4))
        t.add((3, 2, 1))
        t.add((3, 2, 1))
        t.add((3, 2, 1))
        t.add((3, 2, 1))
        t.add((1, 3, 4))
        t.add((3, 2))
        s = pickle.dumps(t)
        dt = pickle.loads(s)
        assert len(list(t)) == len(list(dt))

    def test_iter_next(self):
        t = TokenTree()
        t.add((1, 2, 4))
        t.add((3, 2, 1))
        t.add((3, 2, 1))
        t.add((3, 2, 1))
        t.add((3, 2, 1))
        t.add((1, 3, 4))
        t.add((3, 2))
        node = t.find([])
        assert node is t.get_root()
        assert node.get_count() == 7
        node = t.find([1])
        assert node.get_token() == 1
        assert node.get_count() == 2
        assert node
        lst = list(sorted((x for x in node.iter_next()),
                          key=lambda x: x.get_token()))
        assert len(lst) == 2
        assert lst[0].get_token() == 2
        assert lst[0].get_count() == 1
        assert lst[1].get_token() == 3
        assert lst[1].get_count() == 1
        node = t.find((3, 2))
        assert node.get_count() == 5
        lst = list(sorted((x for x in node.iter_next()),
                          key=lambda x: x.get_token()))
        assert len(lst) == 1
        assert lst[0].get_token() == 1
        assert lst[0].get_count() == 4

# add _ before node.add, node.step (remove add?)
