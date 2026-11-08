import numpy as np

# 1. Vektor Input (x): 2 fitur (misal: Jam Belajar = 4, Jam Tidur = 7)
# Bentuk array: 2 baris, 1 kolom (2x1)
x = np.array([
    [4],
    [7]
])

# 2. Matriks Weight (W): 3 Neuron, masing-masing melihat 2 input
# Bentuk array: 3 baris, 2 kolom (3x2)
W = np.array([
    [ 0.5,  0.2],  # Bobot Neuron 1
    [-0.1,  0.8],  # Bobot Neuron 2
    [ 0.9, -0.3]   # Bobot Neuron 3
])

# 3. Vektor Bias (b): 3 Neuron, masing-masing punya 1 bias
# Bentuk array: 3 baris, 1 kolom (3x1)
b = np.array([
    [ 0.1],
    [ 0.5],
    [-0.2]
])

# 4. Operasi Jaringan Saraf Tiruan: y = Wx + b
# np.dot() digunakan untuk perkalian matriks (dot product)
Wx = np.dot(W, x)
y = Wx + b

print("Hasil Output Layer (y):")
print(y)