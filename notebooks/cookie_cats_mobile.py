import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest

# cookie cats ab testi - gate 30 mu 40 mi daha iyi tutuyor oyuncuyu

df = pd.read_csv("/Users/burak.zeytin/Downloads/cookie_cats.csv", sep=";")
# dosya virgulle degil ; ile ayrilmis, sep vermezsek tek kolon geliyor

print(df.shape)
print(df.isnull().sum())
print(df["version"].value_counts())
print(df["sum_gamerounds"].describe())

# bir oyuncu 49854 tur oynamis, ortalama 52. bu tek deger her seyi kaydiriyor, atiyorum
df = df[df["sum_gamerounds"] < 45000].copy()

gate30 = df[df["version"] == "gate_30"]
gate40 = df[df["version"] == "gate_40"]

mavi = "#5B8FF9"
turuncu = "#F6A623"

# ---- gruplar dengeli mi ----
# ab testinde iki grubun yakin olmasi lazim, once ona bakiyorum
sayilar = df["version"].value_counts()
print(sayilar)

plt.figure(figsize=(7, 5))
bar = plt.bar(sayilar.index, sayilar.values, color=[mavi, turuncu], width=0.5)
for b in bar:
    plt.text(b.get_x() + b.get_width() / 2, b.get_height() + 300,
             format(int(b.get_height()), ","), ha="center", fontweight="bold")
plt.ylabel("oyuncu sayisi")
plt.title("Oyuncularin versiyon dagilimi")
plt.tight_layout()
plt.show()

# ---- genel retention ----
print(df.groupby("version")[["retention_1", "retention_7"]].mean() * 100)

ret = df.groupby("version")[["retention_1", "retention_7"]].mean() * 100
x = np.arange(2)
plt.figure(figsize=(9, 5))
plt.bar(x - 0.18, ret.loc["gate_30"], 0.35, label="gate_30", color=mavi)
plt.bar(x + 0.18, ret.loc["gate_40"], 0.35, label="gate_40", color=turuncu)
plt.xticks(x, ["retention_1", "retention_7"])
plt.ylabel("Retention %")
plt.legend()
plt.title("Versiyona gore retention")
plt.tight_layout()
plt.show()


# ---- z test ----
# oran karsilastirdigimiz icin z test mantikli, ornekleme de buyuk
for col in ["retention_1", "retention_7"]:
    a = gate30[col]
    b = gate40[col]
    z, p = proportions_ztest([a.sum(), b.sum()], [len(a), len(b)])
    print(col, "z:", round(z, 3), "p:", round(p, 4))


# ---- ki kare ----
for col in ["retention_1", "retention_7"]:
    tablo = pd.crosstab(df["version"], df[col])
    chi2, p, dof, exp = stats.chi2_contingency(tablo)
    print(col, "chi2:", round(chi2, 3), "p:", round(p, 4))


# ---- bootstrap ----
# z teste ek olarak, varsayimsiz kontrol. veriyi 1000 kez yeniden ornekleyip farka bakiyoruz
def bootstrap(col, n=1000):
    farklar = []
    for i in range(n):
        ornek = df.sample(frac=1, replace=True)
        oran = ornek.groupby("version")[col].mean()
        farklar.append(oran["gate_30"] - oran["gate_40"])
    return np.array(farklar)

boot1 = bootstrap("retention_1")
boot7 = bootstrap("retention_7")

print("ret1 gate30 daha iyi olasilik:", (boot1 > 0).mean())
print("ret7 gate30 daha iyi olasilik:", (boot7 > 0).mean())

plt.figure(figsize=(13, 5))
for i, (boot, ad) in enumerate([(boot1, "retention_1"), (boot7, "retention_7")]):
    plt.subplot(1, 2, i + 1)
    plt.hist(boot * 100, bins=40, color=mavi, alpha=0.85)
    plt.axvline(0, color="red", ls="--")
    plt.axvline(boot.mean() * 100, color="black")
    plt.title(ad + "  P(30>40)=" + str(round((boot > 0).mean() * 100, 1)))
    plt.xlabel("gate_30 - gate_40 (puan)")
plt.tight_layout()
plt.show()


# ---- cohens h ----
# p value 90k satirda cok kolay anlamli cikiyor. etki gercekten buyuk mu ona bakiyoruz
def cohens_h(p1, p2):
    return 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))

for col in ["retention_1", "retention_7"]:
    h = cohens_h(gate30[col].mean(), gate40[col].mean())
    print(col, "cohens h:", round(h, 4))
# ikisi de 0.2'nin cok altinda yani etki kucuk


# ---- bayesian ----
# gate30'un gercekten daha iyi olma olasiligini direkt veriyor
def bayesian(col, n=100000):
    a = gate30[col]
    b = gate40[col]
    ornek30 = np.random.beta(1 + a.sum(), 1 + (~a).sum(), n)
    ornek40 = np.random.beta(1 + b.sum(), 1 + (~b).sum(), n)
    prob = (ornek30 > ornek40).mean()
    lift = ((ornek30 - ornek40) / ornek40 * 100).mean()
    return ornek30, ornek40, prob, lift

plt.figure(figsize=(13, 5))
for i, col in enumerate(["retention_1", "retention_7"]):
    o30, o40, prob, lift = bayesian(col)
    print(col, "P(30>40):", round(prob * 100, 1), "lift:", round(lift, 2))
    plt.subplot(1, 2, i + 1)
    plt.hist(o30 * 100, bins=80, alpha=0.6, color=mavi, label="gate_30")
    plt.hist(o40 * 100, bins=80, alpha=0.6, color=turuncu, label="gate_40")
    plt.title(col + "  P=" + str(round(prob * 100, 1)))
    plt.legend()
plt.tight_layout()
plt.show()


# ---- ki kare heatmap ----
plt.figure(figsize=(13, 5))
for i, col in enumerate(["retention_1", "retention_7"]):
    tablo = pd.crosstab(df["version"], df[col])
    yuzde = tablo.div(tablo.sum(axis=1), axis=0) * 100
    plt.subplot(1, 2, i + 1)
    sns.heatmap(yuzde, annot=True, fmt=".1f", cmap="Blues")
    plt.title(col)
    plt.xlabel("dondu mu")
plt.tight_layout()
plt.show()


# ---- sum_gamerounds donen vs donmeyen ----
# ortalama alirsak asiri oynayanlar kaydirir, o yuzden medyan
for col in ["retention_1", "retention_7"]:
    tablo = df.groupby(["version", col])["sum_gamerounds"].median().unstack()
    print(col)
    print(tablo)

plt.figure(figsize=(14, 6))
for i, col in enumerate(["retention_1", "retention_7"]):
    kutular = []
    etiketler = []
    renkler = []
    for v, c in [("gate_30", mavi), ("gate_40", turuncu)]:
        for ret_deger in [False, True]:
            veri = df[(df["version"] == v) & (df[col] == ret_deger)]["sum_gamerounds"]
            veri = veri[veri <= 200]  # ustunu kirptim yoksa outlier basiyor
            kutular.append(veri)
            etiketler.append(v + ("\ndondu" if ret_deger else "\ndonmedi"))
            renkler.append(c if ret_deger else "#d0d0d0")
    plt.subplot(1, 2, i + 1)
    bp = plt.boxplot(kutular, patch_artist=True,
                     medianprops=dict(color="black", linewidth=2))
    for kutu, c in zip(bp["boxes"], renkler):
        kutu.set_facecolor(c)
    plt.xticks([1, 2, 3, 4], etiketler, fontsize=8)
    plt.title(col)
plt.tight_layout()
plt.show()


# boxplot biraz karisik, sadece medyanlari bar olarak da cizeyim, daha net okunuyor
plt.figure(figsize=(13, 5))
for i, col in enumerate(["retention_1", "retention_7"]):
    plt.subplot(1, 2, i + 1)
    gruplar = []
    medyanlar = []
    renkler = []
    for v, c_dondu, c_donmedi in [("gate_30", mavi, "#1a4fa0"),
                                   ("gate_40", turuncu, "#c47a00")]:
        for ret_deger in [False, True]:
            veri = df[(df["version"] == v) & (df[col] == ret_deger)]["sum_gamerounds"]
            gruplar.append(v + ("\ndondu" if ret_deger else "\ndonmedi"))
            medyanlar.append(veri.median())
            renkler.append(c_dondu if ret_deger else c_donmedi)
    bar = plt.bar(gruplar, medyanlar, color=renkler, width=0.5)
    for b, m in zip(bar, medyanlar):
        plt.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.5,
                 str(int(m)), ha="center", fontweight="bold")
    plt.ylabel("medyan tur")
    plt.title(col)
    plt.xticks(fontsize=8)
plt.tight_layout()
plt.show()


# ---- tur araligina gore donmeme orani, iki grup ayni grafikte ----
bins = [0, 5, 10, 15, 20, 30, 40, 50, 75, 100, 200, 500, 100000]
labels = ["1-5", "6-10", "11-15", "16-20", "21-30", "31-40",
          "41-50", "51-75", "76-100", "101-200", "201-500", "500+"]
df["bin"] = pd.cut(df["sum_gamerounds"], bins=bins, labels=labels, include_lowest=True)

# once her tur araliginda kac kisi dondu kac kisi donmedi, yigili bar
plt.figure(figsize=(14, 6))
for i, col in enumerate(["retention_1", "retention_7"]):
    grp = df.groupby("bin", observed=True)[col].agg(["count", "sum"])
    dondu = grp["sum"]
    donmedi = grp["count"] - grp["sum"]
    donmeme = donmedi / grp["count"] * 100
    xx = range(len(grp))

    plt.subplot(1, 2, i + 1)
    plt.bar(xx, dondu, color=mavi, label="dondu")
    plt.bar(xx, donmedi, bottom=dondu, color="#d0d0d0", label="donmedi")
    ax2 = plt.gca().twinx()
    ax2.plot(xx, donmeme, color="red", marker="o")
    ax2.set_ylabel("donmeme %", color="red")
    plt.xticks(xx, labels, rotation=45, ha="right", fontsize=8)
    plt.title(col)
    plt.legend(loc="upper right", fontsize=8)
plt.tight_layout()
plt.show()

# ayni seyi g30 ve g40 icin ayri ayri, kapinin etkisi bir grupta farkli mi diye
plt.figure(figsize=(16, 11))
sira = 1
for col in ["retention_1", "retention_7"]:
    for v in ["gate_30", "gate_40"]:
        sub = df[df["version"] == v]
        grp = sub.groupby("bin", observed=True)[col].agg(["count", "sum"])
        dondu = grp["sum"]
        donmedi = grp["count"] - grp["sum"]
        donmeme = donmedi / grp["count"] * 100
        xx = range(len(grp))
        c = mavi if v == "gate_30" else turuncu

        plt.subplot(2, 2, sira)
        plt.bar(xx, dondu, color=c, label="dondu")
        plt.bar(xx, donmedi, bottom=dondu, color="#d0d0d0", label="donmedi")
        ax2 = plt.gca().twinx()
        ax2.plot(xx, donmeme, color="red", marker="o")
        plt.xticks(xx, labels, rotation=45, ha="right", fontsize=7)
        plt.title(v + " | " + col)
        plt.legend(loc="upper right", fontsize=7)
        sira += 1
plt.tight_layout()
plt.show()

plt.figure(figsize=(14, 6))
for i, col in enumerate(["retention_1", "retention_7"]):
    plt.subplot(1, 2, i + 1)
    for v, c, cizgi in [("gate_30", mavi, "-"), ("gate_40", turuncu, "--")]:
        sub = df[df["version"] == v]
        grp = sub.groupby("bin", observed=True)[col].agg(["count", "sum"])
        donmeme = (grp["count"] - grp["sum"]) / grp["count"] * 100
        plt.plot(range(len(donmeme)), donmeme, color=c, ls=cizgi, marker="o", label=v)
    plt.xticks(range(len(labels)), labels, rotation=45, ha="right", fontsize=8)
    plt.ylabel("donmeme orani %")
    plt.title(col)
    plt.legend()
plt.tight_layout()
plt.show()


# ---- funnel: 1. gun donen kaci 7. gune kaldi ----
plt.figure(figsize=(14, 6))
for i, (v, c) in enumerate([("gate_30", mavi), ("gate_40", turuncu)]):
    sub = df[df["version"] == v]
    toplam = len(sub)
    gun1 = sub["retention_1"].sum()
    gun1_7 = sub[sub["retention_1"]]["retention_7"].sum()
    print(v, "gecis orani:", round(gun1_7 / gun1 * 100, 2))

    plt.subplot(1, 2, i + 1)
    plt.bar(["tum", "1.gun donen", "1.+7.gun"], [toplam, gun1, gun1_7], color=c)
    plt.title(v)
plt.tight_layout()
plt.show()


# ---- 4 senaryo ----
for v in ["gate_30", "gate_40"]:
    sub = df[df["version"] == v]
    print(v)
    print(pd.crosstab(sub["retention_1"], sub["retention_7"], normalize=True) * 100)

# sonuc: ret7'de tum testler gate30 lehine. etki kucuk ama her metrikte tutarli.
# karar: kapi 30'da kalsin. tek eksik monetizasyon verisi yok.