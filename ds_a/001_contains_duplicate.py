def containsDuplicate(given_list):
    temp_dict = {}
    for num in given_list:
        if num in temp_dict:
            return True
        else:
            temp_dict[num] = True
    return False


def test_large_input_no_duplicates():
    input_array = list(range(10_000_000))
    assert containsDuplicate(input_array) is False


def test_large_input_with_duplicate():
    input_array = list(range(10_000_000)) + [1]
    assert containsDuplicate(input_array) is True

test_large_input_no_duplicates()
test_large_input_with_duplicate()