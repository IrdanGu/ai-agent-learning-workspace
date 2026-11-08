s = "chris alan"
print(s[0])
for i in s:
    if i == " ":
        # lest say b itu huruf yang aku ingin ubah jadi uppercase
        # s[i].replace("b")
        # s[s.index(i)+1] == "b


        print(s[s.index(i)+1])
s.title()