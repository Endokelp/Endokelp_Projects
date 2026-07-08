from hypnos_edge.policy import decide

_LIGHT_TOKENS = {"seek_bright", "seek_dark", "maintain"}


def test_basic_decision_shape():
    rec = decide(0.5, 300.0, True)
    assert rec.light_action in _LIGHT_TOKENS
    assert isinstance(rec.caffeine_note, str) and len(rec.caffeine_note) > 0


def test_hysteresis_holds_in_dead_zone():
    rec1 = decide(0.25, 100, True)
    assert rec1.risk_label == "high_risk"
    rec2 = decide(0.35, 100, True, prev=rec1)
    assert rec2.risk_label == "high_risk"  # 0.35 is inside the 0.30-0.40 dead zone
    rec3 = decide(0.45, 100, True, prev=rec2)
    assert rec3.risk_label != "high_risk"  # crossed the 0.40 exit threshold


def test_caffeine_never_actionable():
    for a in (0.1, 0.3, 0.5, 0.7, 0.9):
        rec = decide(a, 200.0, True)
        assert rec.caffeine_note not in _LIGHT_TOKENS
