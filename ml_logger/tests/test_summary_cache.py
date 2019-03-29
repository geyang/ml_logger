from ml_logger.caches.summary_cache import SummaryCache
from ml_logger.helpers.print_utils import PrintHelper
import numpy as np


def save_mock_data(cache: SummaryCache):
    i = 1
    for j in range(500):
        cache.store(
            reward=(1 - np.exp(i)) + 0.1 * np.random.rand(),
            activations=np.random.normal(5, 0.5),
            actions=np.random.normal(50, 0.5),
            scalar=np.random.rand(1)[0]
        )


def test_summary_cache():
    print_helper = PrintHelper()
    cache = SummaryCache(mode='tiled')
    for i in range(10):
        save_mock_data(cache)
        stats = cache.get_stats(reward="mean", activations="quantile", actions="histogram")
        s = print_helper.format_tabular(stats)
        # s = print_helper.format_row_table(stats)
        print(s)
