import sys

sys.path.insert(0, "backend")

from faithfulness import check_answer


def test_numbers_from_tools_are_accepted():
    tools = {"cash_now": 9500.0, "lowest_week": 11}
    result = check_answer("Your cash is $9,500 and bottoms out in week 11.", tools)
    assert result["faithful"] is True


def test_invented_numbers_are_caught():
    tools = {"cash_now": 9500.0}
    result = check_answer("Your cash is $9,500, and a 15% buffer is about 1,425.", tools)
    assert result["faithful"] is False                                 