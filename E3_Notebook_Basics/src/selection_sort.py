"""Selection sort practice for Experiment 3."""


def selection_sort(data):
    """
    Sort numbers in ascending order with selection sort.

    Parameters:
        data: an iterable of comparable values

    Returns:
        A new sorted list. The original input is not modified.
    """
    arr = list(data)
    for i in range(len(arr)):
        min_index = i
        for j in range(i + 1, len(arr)):
            if arr[j] < arr[min_index]:
                min_index = j
        arr[i], arr[min_index] = arr[min_index], arr[i]
    return arr


def parse_numbers(text):
    """Parse numbers separated by spaces or commas."""
    return [int(item) for item in text.replace(",", " ").split()]


def test_selection_sort():
    """Run basic test cases for selection_sort."""
    test_cases = [
        [64, 25, 12, 22, 11],
        [5, 4, 3, 2, 1],
        [1, 2, 3, 4, 5],
        [3, 3, 2, 1, 2],
        [],
        [42],
        [-1, 5, 0, -3, 2],
    ]

    for case in test_cases:
        result = selection_sort(case)
        expected = sorted(case)
        print(f"输入: {case} -> 输出: {result}")
        assert result == expected, f"测试失败: {case}"

    print("所有 selection_sort 测试均通过！")


def demo_user_input_sort():
    """Simulate user input, parse it, sort it, and print the result."""
    user_text = "64 25 12 22 11"
    numbers = parse_numbers(user_text)
    sorted_numbers = selection_sort(numbers)

    print("模拟输入:", user_text)
    print("解析结果:", numbers)
    print("排序结果:", sorted_numbers)


if __name__ == "__main__":
    test_selection_sort()
    demo_user_input_sort()
