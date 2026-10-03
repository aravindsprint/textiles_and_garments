"""
Unit tests for the frappe-free decision helpers of stock_integrity.
Run without a site:  python -m pytest tests/test_stock_integrity_pure.py
"""

import importlib.util
import pathlib

_path = pathlib.Path(__file__).resolve().parents[1] / "textiles_and_garments" / "stock_integrity" / "pure.py"
_spec = importlib.util.spec_from_file_location("pure", _path)
pure = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pure)


def test_median():
    assert pure.median([]) is None
    assert pure.median([3]) == 3
    assert pure.median([1, 3, 2]) == 2
    assert pure.median([1, 2, 3, 4]) == 2.5
    # one absurd transfer rate (SKF11647 picked Rs 27,441/kg as "latest") does not move a median
    assert pure.median([357.19, 360, 355, 27440.98]) == 358.595


def test_chain_ok_catches_unapplied_entry():
    # MF/25/10763: +24.84 kg posted but the running balance never moved
    assert pure.chain_ok(2930.838, 24.84, 2955.678)
    assert not pure.chain_ok(2930.838, 24.84, 2930.838)
    assert pure.chain_ok(None, 5, 5)
    assert pure.chain_ok(10, -0.0005, 10)  # within 0.001 tolerance


def test_snap_remainder():
    assert pure.snap_remainder(25.163, 25.16, 0.005) == 0.003   # crumb taken along
    assert pure.snap_remainder(25.2, 25.16, 0.005) == 0          # real stock stays
    assert pure.snap_remainder(25.16, 25.16, 0.005) == 0         # nothing left
    assert pure.snap_remainder(25.0, 25.16, 0.005) == 0          # taking more than there is: not our job
    assert pure.snap_remainder(25.163, 25.16, 0) == 0            # disabled


def test_repost_hits_protected():
    assert pure.repost_hits_protected("2026-02-10 10:00:00", "2026-10-03 11:48:14")       # backdated: refuse
    assert pure.repost_hits_protected("2026-10-03 11:48:14", "2026-10-03 11:48:14")       # same moment: refuse
    assert not pure.repost_hits_protected("2026-10-03 12:30:00", "2026-10-03 11:48:14")   # later: fine


def test_classify_row():
    assert pure.classify_row(False, 0, False, False, 4, 0.05) == "U"
    assert pure.classify_row(True, 50.31, True, True, 50.31, 0.05) == "K"
    assert pure.classify_row(True, 0.008, True, True, 0.008, 0.05) == "Z"
    assert pure.classify_row(True, 0, False, True, 0, 0.05) == "C"
    assert pure.classify_row(True, 0, False, False, 0, 0.05) == "S"   # only negative batches


def test_chunk_groups_never_splits_an_item():
    groups = [[1] * 40, [2] * 40, [3] * 20, [4] * 5]
    chunks = pure.chunk_groups(groups, 90)
    assert [len(c) for c in chunks] == [80, 25]
    big = pure.chunk_groups([[1] * 120, [2] * 3], 90)
    assert [len(c) for c in big] == [120, 3]
    assert pure.chunk_groups([], 90) == []


def test_is_red_and_out_of_sync():
    assert pure.is_red(50.31, -33341.29)
    assert pure.is_red(-25.12, 0)
    assert not pure.is_red(0, -0.5)             # dust, not red
    assert not pure.is_red(-0.0005, -0.08)      # rounds to -0.001, not below it
    assert pure.out_of_sync(26.6, -33869.87, 1.76, -33869.87)
    assert not pure.out_of_sync(26.6, 3186.41, 26.6, 3186.41)
