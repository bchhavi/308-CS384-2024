a = input("Enter a list of words: ").split()

print("Words: ")
print(a)


b = {}

for c in a:
    d = ''.join(sorted(c))
    if d in b:
        b[d].append(c)
    else:
        b[d] = [c]

e = {}
f = None
g = 0

for h, i in b.items():
    j = {}
    for k in i:
        for l in k:
            if l in j:
                j[l] += 1
            else:
                j[l] = 1

    m = 0
    for n in j:
        j[n] *= len(i)
        m += j[n]

    e[h] = j

    if m > g:
        g = m
        f = i


print("\nAnagram Groups:")
for h, i in b.items():
    print(f"'{h}': {i}")

print("\nCharacter Frequencies:")
for h, i in e.items():
    print(f"'{h}': {i}")

print("\nGroup with the highest character frequency:")
print(f"Group: {f}, Total Frequency: {g}")