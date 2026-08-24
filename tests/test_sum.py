"""Tests for the sum utility."""

from feature_crew.sum import sum_list


def test_sum_list_non_empty() -> None:
    assert sum_list([1, 2, 3, 4, 5]) == 15


def test_sum_list_empty() -> None:
    assert sum_list([]) == 0


def test_sum_list_single_element() -> None:
    assert sum_list([42]) == 42
