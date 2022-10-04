from tau_performance import particle_matching as pm


def test_check_for_double_count():
    input_map = {
        1: 1,
        2: 2,
        3: 3,
        4: 2
    }
    expected_double_count = 1
    observed_double_count, obj_sharing = pm.check_for_double_count(input_map)
    assert expected_double_count == observed_double_count
    assert obj_sharing == [2, 4]
