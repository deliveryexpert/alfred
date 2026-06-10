from alfred.bench.prompts import CHALLENGES, total_weight
from alfred.judging.rubric import RUBRIC, weight_sum


def test_challenge_keys_unique():
    keys = [c.key for c in CHALLENGES]
    assert len(keys) == len(set(keys))


def test_have_a_decent_battery():
    assert len(CHALLENGES) >= 8
    assert total_weight() > 0


def test_rubric_weights_sum_to_one():
    assert abs(weight_sum() - 1.0) < 1e-9
    assert len(RUBRIC) >= 4
