"""
Warning suppression module for google_genai and other libraries.
This file must be executed in the VERY FIRST cell of the notebook.
"""
import warnings
import logging
import sys

# Aggressive warning suppression
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Suppress everything below ERROR level for the root logger and specific modules
logging.basicConfig(level=logging.ERROR)
logging.getLogger('google_genai').setLevel(logging.ERROR)
logging.getLogger('google_genai.types').setLevel(logging.ERROR)

# Custom warning handler to completely ignore specific messages
def custom_showwarning(message, category, filename, lineno, file=None, line=None):
    msg = str(message)
    # Ignore specific noisy messages
    if 'non-text parts' in msg or 'EXPERIMENTAL' in msg:
        return
    # Default behavior for everything else
    sys.stderr.write(warnings.formatwarning(message, category, filename, lineno, line))

warnings.showwarning = custom_showwarning

print("✅ Aggressive warning/log suppression enabled.")