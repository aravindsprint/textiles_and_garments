# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Store original execute functions for monkey-patched reports
_original_batch_execute = None
_original_gl_execute = None
_original_gl_get_conditions = None

# Import the monkey patches when this module is loaded (optional)
# Commented out to avoid circular imports
# from .general_ledger import custom_execute, custom_get_conditions
# __all__ = ['custom_execute', 'custom_get_conditions']
