# This file defines exports from the tokentree module.
#
# Copyright (c) Tatu Ylonen.  See LICENSE and https://ylonen.org

import pyximport; pyximport.install()
from tokentree.ctokentree import TokenTree

__all__ = ["TokenTree"]
