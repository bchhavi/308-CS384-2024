x = list(map(int, input("Enter List Numbers : ").split()))

i = 0
j = i+1
k = len(x)-1
x = sorted(x)
a = []
while i < k-1:
  if x[i] + x[j] + x[k] == 0:
    l = []
    l.append(x[i])
    l.append(x[j])
    l.append(x[k])
    a.append(l)
    j+=1
  elif x[i] + x[j] + x[k] > 0:
    k-=1
  else:
    j+=1

  if j >= k:
    i+=1
    j = i+1
    k = len(x) - 1


set_of_triplets = set(tuple(triplet) for triplet in a)

print(set_of_triplets)