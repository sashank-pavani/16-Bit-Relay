def monitor_resource_usage(memory_values, cpu_values, threshold, num_of_consecutive_val):
    """
    Monitors memory and CPU usage and marks values exceeding a threshold.

    If the memory or CPU value exceeds the `threshold` for `num_of_consecutive_val` consecutive measurements,
    all subsequent values (starting from the `num_of_consecutive_val`th measurement onward) will be marked in red.
    This marking will continue until the memory or CPU values fall below the threshold for at least
    `num_of_consecutive_val` consecutive measurements.

    :param memory_values: List of memory usage values.
    :type memory_values: list
    :param cpu_values: List of CPU usage values.
    :type cpu_values: list
    :param threshold: The threshold value for memory and CPU usage.
    :type threshold: int or float
    :param num_of_consecutive_val: The number of consecutive measurements required to trigger the marking.
    :type num_of_consecutive_val: int

    :return: A tuple containing the marked memory and CPU values.
    :rtype: tuple

    .. note::

        This function assumes that the input lists `memory_values` and `cpu_values` are of the same length.
        Inconsistent lengths may result in incorrect markings.

    .. warning::

        Ensure that `threshold` and `num_of_consecutive_val` are set appropriately. Incorrect values may
        lead to inaccurate monitoring results.

    .. seealso::
        :func:`reset_markings` - Resets all markings to the default state.

    :example:

    >>> memory_values = [70, 75, 80, 85, 90, 95]
    >>> cpu_values = [60, 65, 70, 75, 80, 85]
    >>> threshold = 80
    >>> num_of_consecutive_val = 3
    >>> marked_memory, marked_cpu = monitor_resource_usage(memory_values, cpu_values, threshold, num_of_consecutive_val)
    >>> print(marked_memory)
    ['normal', 'normal', 'normal', 'red', 'red', 'red']
    >>> print(marked_cpu)
    ['normal', 'normal', 'normal', 'red', 'red', 'red']
    """
    # Function implementation
    pass

def reset_markings():
    """
    Resets all markings to the default state.
    """
    # Function implementation
    pass
