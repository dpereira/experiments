import sys

assignments = [
    (0, sys.maxsize, 0)
]

def add_partition(identifier, assignments):

    reassignments = []

    current_partition_count = len(assignments)
    new_partition_count = current_partition_count + 1

    insertion_index = int(current_partition_count / 2)
    _, max_size, _ = assignments[-1]
    new_partition_size = int(max_size / new_partition_count)

    for i in range(new_partition_count):
        if i == insertion_index:
            partition_identifier = identifier
        elif i < insertion_index:
            partition_identifier = assignments[i][2]
        else:
            partition_identifier = assignments[i-1][2]

        reassignments.append(
            (i * new_partition_size, (i + 1) * new_partition_size, partition_identifier)
        )


    print('\n'.join(['{} -> {}'.format(x, x[1] - x[0]) for x in reassignments]))

    return reassignments

print('\n'.join(['{} -> {}'.format(x, x[1] - x[0]) for x in assignments]))
print('=========================================================')

p = assignments
for i in range(1, 64):
    p = add_partition(i, p)
    print('=========================================================')
