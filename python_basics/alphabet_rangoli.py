# size = 3
# row = size
#
# for i in range(row):
#     x = []
#     for i in range(size):
#         x.append(chr(ord('a') + (size - i - 1)))
#     x = x[:-1]
#     for i in range(size):
#         x.append(chr(ord('a') + (i)))
#     print(x)
#     size -= 1
# Editor > General > Code Completion > Machine Learning-Assisted Completion.

def print_rangoli(size):
    total_width = 4*size - 3
    top = []

    for row in range(size):

        left = []
        for i in range( size-1, size-2-row , -1 ):
            left.append(chr(ord('a') + i))

        full = left + left[:-1][::-1]
        line = "-".join(full)
        line = line.center(total_width, "-")

        top.append(line)

    bottom = top[:-1][::-1]

    for line in top + bottom:
        print(line)

print_rangoli(3)
alphabet = []
for i in range(ord('a'), ord('z')+1):
    alphabet.append(chr(i))

# get index of z
print(alphabet.index('z'))