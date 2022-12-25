import pandas as pd
df = pd.read_csv("merge_from_ofoct.csv")
a = df["Продукт"].tolist()
for i in range(len(a)):
    a[i] = a[i].lower()

df["Продукт"] = a




