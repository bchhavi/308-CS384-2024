s = input("Enter a string: ")
perm = [""]

for char in s:
  new_perm = []

  for p in perm:
    for i in range(len(p) + 1):
      new_perm.append(p[:i] + char + p[i:])
      perm = new_perm


perm = set(perm)

for p in perm:
  print(p)