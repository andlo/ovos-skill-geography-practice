"""Tests for generate_border_question() - pure logic, no mocking
needed. Runs many iterations since it's randomized."""
ITERATIONS = 300


def test_true_case_always_picks_an_actual_border():
    from geographypractice_skill import generate_border_question, CORE_DATA
    for _ in range(ITERATIONS):
        cca3, other, is_true = generate_border_question()
        if is_true:
            assert other in CORE_DATA[cca3]["borders"]


def test_false_case_never_picks_an_actual_border():
    from geographypractice_skill import generate_border_question, CORE_DATA
    for _ in range(ITERATIONS):
        cca3, other, is_true = generate_border_question()
        if not is_true:
            assert other not in CORE_DATA[cca3]["borders"]
            assert other != cca3


def test_country_with_no_borders_always_gets_a_false_question():
    """An island nation with an empty borders list has no true pairs
    to draw from - confirms it always falls through to the false
    branch rather than erroring."""
    from geographypractice_skill import generate_border_question, CORE_DATA
    island_nations = [cca3 for cca3, c in CORE_DATA.items() if not c["borders"]]
    assert island_nations, "expected at least one country with zero land borders"
    target = island_nations[0]
    for _ in range(ITERATIONS):
        cca3, other, is_true = generate_border_question(country_codes=[target])
        assert cca3 == target
        assert is_true is False


def test_both_true_and_false_cases_occur_over_many_iterations():
    from geographypractice_skill import generate_border_question
    results = {generate_border_question()[2] for _ in range(ITERATIONS)}
    assert results == {True, False}
