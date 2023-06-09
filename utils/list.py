"""
полезные функции для работы с списками
"""
from typing import List, Tuple


def is_indexes_correct(arr: List[List[any]], i: int, j: int) -> bool:
    """
    не выходят ли индексы за границы списка
    """
    return 0 <= i < len(arr) and 0 <= j < len(arr[i])


def get_list_without_equal_elements(arr: List[any]) -> List[any]:
    """
    :param arr: одномерный список. Не изменяется
    :return: отсортированный список без одинаковых элементов
    """
    sorted_arr = sorted(arr)
    result = []
    i = 0
    while i < len(sorted_arr):
        old = sorted_arr[i]
        while i < len(sorted_arr) and sorted_arr[i] == old:
            i += 1
        result.append(old)
    return result


def delete_element(arr: List[any], i: int):
    """
    Удаление элемента (O(1) асимптотика).
    Порядок в списке не сохраняется (На место i попадает последний эл-т, если i - не последний эл-т).
    :param arr: список
    :param i: индекс
    """
    arr[i], arr[-1] = arr[-1], arr[i]
    arr.pop()


def copy_list(arr: List[any]) -> List[any]:
    """
    Копирует эл-ты arr и возвращает список. Не работает, если arr[i] содержит ссылку на объект
    """
    result = [item for item in arr]
    return result


def copy_2dimensional_list(arr: List[List[any]]) -> List[List[any]]:
    """
    Копирует эл-ты arr[i] и возвращает список. Не работает, если arr[i][j] содержит ссылку на объект
    """
    result = [copy_list(item) for item in arr]
    return result


def get_list_chance_sum(arr: List[Tuple[int, any]]):
    result = 0
    for item in arr:
        result += item[0]
    return result


def check_chance_list(arr: List[Tuple[int, any]]):
    sum_chance = get_list_chance_sum(arr)
    if sum_chance != 100:
        raise Exception('sum of chance list not equal 100. The value: {}'. \
                        format(sum_chance))
