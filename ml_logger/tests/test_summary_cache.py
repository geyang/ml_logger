from ml_logger.caches.summary_cache import SummaryCache, flatten
from ml_logger.helpers.print_utils import PrintHelper
import numpy as np


def test_flatten():
    a = [[0], [1, 2], np.array([10, 1]), [np.array([10])]]
    flat = flatten(a)
    assert flat == [0.0, 1.0, 2.0, 10.0, 1.0, 10.0]


def test_flatten_different_shape():
    a = [[0], [1, 2], np.array([10, 1]), [np.array([10]), np.array([1, 2])]]
    flat = flatten(a)
    assert flat == [0.0, 1.0, 2.0, 10.0, 1.0, 10.0, 1.0, 2.0]


def test_flatten_containing_None():
    a = [[0], [1, 2], np.array([None, 1]), [np.array([10]), np.array([1, 2])]]
    flat = flatten(a)
    assert np.allclose(flat,
                       [0.0, 1.0, 2.0, np.NaN, 1.0, 10.0, 1.0, 2.0], equal_nan=True)


def test_flatten_containing_NaN():
    a = [[0], [1, 2], np.array([np.nan, 1]), [np.array([10]), np.array([1, 2])]]
    flat = flatten(a)
    assert np.allclose(flat,
                       [0.0, 1.0, 2.0, np.NaN, 1.0, 10.0, 1.0, 2.0], equal_nan=True)


def save_mock_data(cache: SummaryCache):
    np.random.seed(0)
    i = 1
    for j in range(500):
        cache.store(
            reward=(1 - np.exp(i)) + 0.1 * np.random.rand(),
            activations=np.random.normal(5, 0.5),
            actions=np.random.normal(50, 0.5),
            scalar=np.random.rand(1)[0],
            uneven_length=np.array([1] * np.random.randint(0, 5))
        )


def test_summary_cache():
    print_helper = PrintHelper()
    cache = SummaryCache(mode='tiled')
    print()
    for i in range(10):
        save_mock_data(cache)
        stats = cache.summary_stats(reward="mean", activations="quantile", actions="histogram")
        s = print_helper.format_tabular(stats)
        # s = print_helper.format_row_table(stats)


def test_single_key():
    print_helper = PrintHelper()
    cache = SummaryCache(mode='tiled')
    print()
    for i in range(10):
        save_mock_data(cache)
        mean_reward = cache.get("reward").mean()
        assert isinstance(mean_reward, float)


def test_pop():
    print_helper = PrintHelper()
    cache = SummaryCache(mode='tiled')
    print()
    for i in range(10):
        save_mock_data(cache)
        mean_reward = cache.pop("reward").mean()
        assert isinstance(mean_reward, float)
        assert "reward" not in cache.data


def test_repr():
    print_helper = PrintHelper()
    cache = SummaryCache(mode='tiled')
    print()
    for i in range(10):
        save_mock_data(cache)
        stats = cache.summary_stats(reward="mean", activations="quantile", actions="histogram")
        # s = print_helper.format_tabular(stats)
        # s = print_helper.format_row_table(stats)
        # print(s)

    np.mean(cache.get('reward'))
    from textwrap import dedent
    assert str(cache) == dedent("""
    SummaryCache:  reward: Shape()[:5000]
      activations: [5.370795870404581, 4.241508632737578][:5000]
      actions: [50.77645686095641, 49.56686189467056][:5000]
      scalar: Shape()[:5000]
      uneven_length: Shape(1,)[:5000]
    """)[1:]


if __name__ == '__main__':
    test_single_key()
    test_pop()
