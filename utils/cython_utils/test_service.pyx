from libcpp.vector cimport vector
from libc.stdlib cimport rand, srand
from libcpp.algorithm cimport sort
from libc.time cimport time


cdef class Test:
    """
    Тестовый класс, для интеграции с C++
    """

    cdef vector[int] cdef_list_generator(self, int count):
        """
        C++ генерация вектора
        :param count: количество чисел
        :return: C++ вектор
        """

        cdef vector[int] c_vector
        cdef int i, num
        srand(time(NULL))
        for i in range(count):
            num = rand() % 100
            c_vector.push_back(num)
        sort(c_vector.begin(), c_vector.end())
        return c_vector

    cpdef list generate_and_sort_numbers(self, int count):
        """
        Генерация списка, с использованием C++
        :param count: количество чисел
        :return: сгенерированный список, с использованием C++
        """

        c_vector = self.cdef_list_generator(count)
        return [c_vector[i] for i in range(c_vector.size())]