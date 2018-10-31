XXX this code saved temporarily and needs fixing

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
