# Cookie Cats A/B Test Analysis

Cookie Cats, Tactile Entertainment tarafından geliştirilen bir mobil bulmaca oyunu. Oyunda belirli bir levela gelince oyuncu duraksatılıyor — bu noktaya "gate" (kapı) deniyor. Oyuncu ya bir süre bekliyor, ya arkadaşından yardım istiyor, ya da para ödeyip devam ediyor. Bu analizde kapının 30. levelde mi yoksa 40. levelde mi olmasının oyuncu tutma oranına (retention) etkisini inceledim.

## Problem

Şirket iki farklı versiyon test etti:
- **gate_30**: Oyuncu 30. levelde duraksatılıyor
- **gate_40**: Oyuncu 40. levelde duraksatılıyor

Soru: Hangisi oyuncuyu daha uzun süre oyunda tutuyor?

## Veri

- 90.189 oyuncu kaydı
- Kolonlar: `userid`, `version`, `sum_gamerounds` (ilk 14 günde oynanan tur), `retention_1` (1. gün geri döndü mü), `retention_7` (7. gün geri döndü mü)
- Kaynak: [Kaggle - Mobile Games A/B Testing](https://www.kaggle.com/datasets/yufengsui/mobile-games-ab-testing)
- Tek aşırı outlier temizlendi (bir oyuncu 49.854 tur oynamış, ortalama 52 iken — bu tek değer tüm istatistikleri kaydırıyordu)

> Not: Aşağıdaki görsellerin dosya adlarını `visuals/` klasöründeki kendi PNG isimlerinle eşleştir.

## 1. Grup Dağılımı

![](visuals/versiyon_dagilim.png)

A/B testinde ilk kontrol grupların dengeli olması. gate_40'a 45.489, gate_30'a 44.700 oyuncu atanmış. Gruplar birbirine yakın, randomizasyon büyük ölçüde sağlıklı görünüyor.

## 2. Retention Karşılaştırması

![](visuals/retention.png)

| Metrik | gate_30 | gate_40 | Göreli fark |
|--------|---------|---------|-------------|
| retention_1 | %44.82 | %44.23 | +%1.33 |
| retention_7 | %19.02 | %18.20 | +%4.51 |

İki versiyonda da retention oranları birbirine çok yakın. Ama dikkat çeken şu: 7. gündeki göreli fark (%4.51), 1. güne (%1.33) kıyasla yaklaşık 3 kat daha büyük. Yani kapının etkisi zamanla belirginleşiyor. gate_30'da oyuncular erken duraksatıldığı için hem 1. hem 7. gün daha fazla geri dönmüş.

## 3. İstatistiksel Testler

Farkın gerçek mi yoksa şans eseri mi olduğunu 5 farklı yöntemle test ettim.

![](visuals/bootstrap.png)

![](visuals/bayesian.png)

**retention_7 sonuçları:**
- Z-test: p = 0.0016 (anlamlı)
- Ki-kare: p = 0.0016 (anlamlı)
- Bootstrap: gate_30'un daha iyi olma olasılığı %99.7
- Bayesian: P(gate_30 > gate_40) = %99.9, lift = %4.51
- Cohen's h = 0.021 → etki gerçek ama küçük

**retention_1** için ise hiçbir frekantist test anlamlı çıkmadı (p > 0.05). Yani 1. günde iki versiyon arasında güvenle fark diyemiyoruz, ama 7. günde diyebiliyoruz.

Cohen's h değeri her iki metrikte de çok küçük. Bu önemli bir nokta: 90 bin kişilik büyük örneklem sayesinde küçük bir farkı bile istatistiksel olarak yakaladık, ama bu fark oyun mekaniğini kökten değiştirecek büyüklükte değil.

## 4. Oynanan Tur Sayısı: Dönen vs Dönmeyen

![](visuals/boxplot.png)

Dağılım aşırı sağa çarpık olduğu için ortalama yerine medyan kullandım (ortalama alsaydım az sayıdaki aşırı oyuncu sonucu saptırırdı).

| | Dönmedi | Döndü |
|--|---------|-------|
| retention_7 medyan | 11 tur | ~105-111 tur |

Dönmeyen oyuncular medyan sadece 6-11 tur oynamış — yani oyunu keşfetmeden bırakmışlar, büyük ihtimalle onboarding'de kaybedilen kullanıcılar. Dönenler ise 8-10 kat daha fazla oynamış.

İlginç bir detay: gate_30'da dönmeyenler arasında çok yüksek aykırı değerler var. Bunlar muhtemelen kapıya çarpan aktif oyuncular — para istenince oyunu bırakmış olabilirler.

## 5. Kaçıncı Turdan Sonra Oyuncular Dönmüyor?

![](visuals/churn_overlay.png)

500+ tur oynayan oyuncuların neredeyse tamamı hem 1. hem 7. gün geri dönmüş. Yani çok oynayan oyuncuyu kaybetmiyorsun — retention doğrudan oynama miktarıyla ilişkili.

İki versiyonu aynı grafikte karşılaştırınca: retention_1'de çizgiler neredeyse üst üste (fark yok, p=0.074 ile tutarlı). retention_7'de ise 41-50 turdan itibaren gate_40'ın dönmeme oranı yükseliyor. Fark en belirgin 51-100 tur aralığında — tam gate_30'un devreye girdiği bölge. Bu, kapının etkisini ancak orta vadede gösterdiğini kanıtlıyor.

## 6. Retention Funnel ve Geçiş Oranı

![](visuals/funnel.png)

1. gün dönen oyuncuların kaçı 7. güne kadar kaldı (geçiş oranı):
- gate_30: %33.3
- gate_40: %32.3

1. gün dönmeyip 7. gün geri gelen "geri dönenler":
- gate_30: %7.40
- gate_40: %6.99

Hem 1. hem 7. gün kalan en sadık oyuncular:
- gate_30: %14.94
- gate_40: %14.30

Buradaki asıl mesaj tutarlılık: fark her segmentte küçük (yarım-bir puan) ama istisnasız her senaryoda gate_30 önde. Eğer bu rastgele olsaydı bazı metriklerde gate_40 öne geçerdi, ama geçmiyor. Bu tutarlılık, tek tek küçük farklardan daha ikna edici.

4 senaryo tablosundan bir gözlem daha: en büyük grup "ne 1. gün ne 7. gün dönen" oyuncular (%51). Yani oyuncuların yarısı daha baştan kayıp. Kapıyı optimize etmek önemli ama asıl büyük fırsat bu %51'i azaltmakta — yani onboarding'de.

## Karar

Kapı 30. levelde kalmalı. Sezgi "oyuncu daha çok oynasın, kapıyı geç koyalım" der ama veri tersini söylüyor: kapı erken gelince oyuncu beklerken oyuna bağlılığı pekişiyor ve geri dönüyor. Tüm testler aynı yönde işaret ediyor ve bu tutarlılık kararı sağlam kılıyor.

**Kısıtlamalar:**
- Monetizasyon verisi yok — gate_40 belki daha az retention ama daha çok gelir getiriyor olabilir; gelir etkisi ayrıca ölçülmeli
- Test süresi 14 gün, uzun vadeli (D30+) etki bilinmiyor
- SRM testi sınırda sinyal veriyor (p=0.009), atama mekanizması doğrulanmalı

## Kullanılan Araçlar

Python, pandas, numpy, matplotlib, seaborn, scipy, statsmodels

## Dosya Yapısı

```
cookie-cats-ab-test/
├── data/
│   └── cookie_cats.csv
├── notebooks/
│   └── cookie_cats.py
├── visuals/
│   └── (tüm grafikler)
└── README.md
```
