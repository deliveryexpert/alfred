from alfred.judging.rating import score_to_rating, MAX_RATING


def test_extremes():
    assert score_to_rating(0).value == 0.0
    assert score_to_rating(100).value == MAX_RATING


def test_snaps_to_quarters():
    for s in range(0, 101):
        v = score_to_rating(s).value
        # every rating is a clean multiple of 0.25
        assert abs((v * 4) - round(v * 4)) < 1e-9
        assert 0.0 <= v <= MAX_RATING


def test_pretty_has_quarter_fraction():
    # 85/100 -> 4.25 -> should render with a ¼
    r = score_to_rating(85)
    assert r.value == 4.25
    assert "¼" in r.pretty()


def test_robot_anchors_match_house_style():
    # 70/100 -> 3.5 -> Chappie; 95/100 -> 4.75 -> Johnny Five
    assert score_to_rating(70).value == 3.5
    assert score_to_rating(70).robot == "Chappie"
    assert score_to_rating(95).value == 4.75
    assert score_to_rating(95).robot == "Johnny Five"


def test_top_and_bottom_robots():
    assert score_to_rating(100).robot == "Bender"
    assert score_to_rating(0).robot == "HAL 9000"


def test_pretty_format():
    assert score_to_rating(95).pretty() == "4¾/5 — Johnny Five ⚡"
