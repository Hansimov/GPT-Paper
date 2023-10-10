"""
python -m cProfile -o tests/output.pstats -m utils.layout_analyzer && python -m tests.test_pstats > tests/output.pstats.txt
"""

import pstats
from pathlib import Path

stats_path = Path(__file__).parents[1] / "tests" / "output.pstats"
p = pstats.Stats(str(stats_path))
p.sort_stats(pstats.SortKey.CUMULATIVE)
p.print_stats(100)
