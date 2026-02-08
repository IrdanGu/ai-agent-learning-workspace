kata = input("Masukkan kata : ")

kata_array = []
# ubah variable string menjadi array
for i in kata:
    print(i)
    kata_array.append(i)

print(kata_array)
jumlah_huruf = len(kata_array)
y = 0
print(jumlah_huruf)
for i in range(jumlah_huruf):
    if kata_array[i] == kata_array[jumlah_huruf - 1]:
        print("polindrome")
        jumlah_huruf -= 1
    else:
        print("not polindrome")