# ServicePilot Fizibilite Araştırması: Aktif Servis Triyajı ve Kanıt Toplama Sistemi

**Araştırma tarihi:** 27 Ekim 2026  
**Hedef program:** TÜBİTAK BİGGVADİ  
**Önerilen ilk PoC ortağı:** Anadolu Isuzu  
**Karar:** **GO — ancak “AI arıza teşhisi” değil, “risk kontrollü aktif kanıt toplama ve uzman yönlendirme motoru” olarak daraltılmalı.**

## Yönetici özeti

Araştırmanın sonucu ServicePilot fikrini **destekliyor**, fakat ilk düşündüğümüz gerekçeden biraz farklı bir biçimde.

Ticari araç servis sektöründe “diagnostics”, “root-cause analysis”, teknisyen kapasitesi ve maliyet kontrolü gerçekten belgelenmiş sorunlar. American Trucking Associations’ın Technology & Maintenance Council’i, 400’den fazla filo üyesiyle yaptığı 2025 sonbahar araştırmasında **Diagnostics’i üçüncü, Root Cause Analysis’i dördüncü en önemli bakım problemi** olarak buldu; 2025 ilkbaharında ise Diagnostics birinci, Technician Shortage ikinci sıradaydı. citeturn18view3 ABD işgücü verileri de dizel servis teknisyenleri için 2025–2035 döneminde yılda ortalama 24.400 açık pozisyon oluşacağını öngörüyor; yani uzman emeğinin ölçeklenmesi gerçekten ekonomik bir sorun. citeturn20search0

Anadolu Isuzu tarafında daha da önemli bir bulgu var: bizim tasarladığımız iş akışının bağlanabileceği altyapı **zaten mevcut**. Şirket 2021'den beri ProEye ile merkez servis destek personelinin yurt içi ve yurt dışındaki servis teknisyenlerine telefon veya VR gözlüğü üzerinden uzaktan bağlanmasını, aracı görmesini, teknisyeni yönlendirmesini ve video/doküman paylaşmasını sağlıyor. Ayrı Teknoloji Merkezi'nde sürekli görev yapan uzman teknik destek ekibinin sahadaki teknisyenlerle video görüşmesi yaparak problemi değerlendirdiği de şirket tarafından açıklanmış durumda. 2025 Entegre Raporunun indekslenmiş metni ise ProEye'ın satış sonrası süreçlerin hızlandırılması ve verimliliği amacıyla kullanılmaya devam ettiğini gösteriyor. citeturn17search4turn17search16turn17search15

Bu, ServicePilot'ın varsaydığı **“sahadaki teknisyen → merkez uzman” darboğazının var olduğu operasyonel yapıyı doğruluyor**. Fakat kamuya açık veriler Anadolu Isuzu'da vaka başına kaç uzman dakikası harcandığını, kaç vakanın eksik bilgiyle geldiğini, kaç defa ek fotoğraf veya ölçüm istendiğini veya yanlış uzman kuyruğuna düşen vaka oranını göstermiyor. Dolayısıyla bunları gerçekmiş gibi başvuruya yazmak doğru olmaz.

Daha da önemlisi, pazar boş değil. Mart 2026'da ticari araç servis yönetimi şirketi Decisiv, TRITECH Expert Technician Support ile entegrasyon duyurdu. Sistem yapılandırılmış araç, teşhis ve onarım verilerini uzman destek sistemine aktarıyor, destek vakasını otomatik oluşturuyor ve teknisyene canlı uzman troubleshooting desteği sağlıyor. Bu, **problemin satın alınabilir olduğunu çok güçlü biçimde doğruluyor**, ama aynı zamanda “uzmanı teknisyene bağlayan platform” geliştirmenin artık yeterli farklılaşma olmadığını gösteriyor. citeturn18view4

Bu nedenle gerçek ürünün çekirdeğini şu şekilde tanımlamak gerekir:

> **ServicePilot, servis problemini kendisi teşhis etmeye çalışan bir AI değildir. Eksik bir servis vakasında karar verebilmek için sırada hangi kanıtın toplanmasının en değerli olduğunu belirleyen ve ancak yeterli kanıt oluştuğunda vakayı doğru teknik uzmanlığa yönlendiren düşük gecikmeli karar katmanıdır.**

Jev bu ürün için iyi bir **enabling technology**. TypeSafe'in güncel dokümantasyonuna göre `Choice`, `Score` ve `Noul` sorularını aynı state üzerinde paralel çalıştırabiliyor ve doğrudan olasılık dağılımları üretiyor. Bu yapı “hangi uzmanlık?”, “kanıt yeterli mi?”, “kritik vaka mı?”, “hangi kanıt sırada istenmeli?” gibi küçük kararları tek round-trip'te almak için doğal biçimde uygun. citeturn18view5 Fakat görüntü ve `Box` özellikleri TypeSafe tarafından halen açıkça üretime hazır olmayan deneysel özellikler olarak tanımlanıyor. Bu nedenle ilk PoC'nin başarısını görüntü kabiliyetine bağlamamak gerekir. citeturn18view6

En kritik teknik bulgu ise şu: **“active evidence acquisition” fikrinin kendisi akademik olarak yeni değil.** Active Feature Acquisition literatürü yıllardır tam olarak “eksik bilgi varken hangi bilgiyi, hangi maliyet karşılığında sırada almalıyım?” sorusunu inceliyor. 2026 tarihli güncel literatür taraması alanı POMDP, model-based, model-free ve hibrit yöntemler altında sınıflandırıyor. citeturn18view8 Bu nedenle BİGG Ar-Ge iddiamızı “value of information geliştirdik” şeklinde kuramayız.

**Savunulabilir yenilik alanı**, heterojen servis kanıtlarında gerçek operasyon maliyetini, Jev gibi typed-decision modellerinin olasılıklarını, servis riskini, hiyerarşik uzmanlık yapısını ve insan eskalasyonunu tek bir **risk-budgeted active evidence policy** altında birleştirmek olacaktır.

Benim nihai değerlendirmem:

| BİGG açısından kriter | Puan | Gerekçe |
|---|---:|---|
| **Teknolojik yenilikçilik** | **7.5/10** | Temel AFA/selective prediction bilinen alanlar; servis bağlamındaki risk-maliyet politikası özgünleştirilebilir |
| **Teknik yapılabilirlik** | **8/10** | Routing kolay; gerçek active evidence policy için doğru geçmiş veri gerekiyor |
| **Ticari potansiyel** | **8.5/10** | Problem sektör tarafından doğrulanıyor ve rakipler bu probleme para harcandığını kanıtlıyor |
| **Anadolu Isuzu PoC erişilebilirliği** | **8/10** | ProEye + teknik destek merkezi + BİGGVADİ ortaklığı güçlü; veri erişimi garanti değil |
| **Genel değerlendirme** | **8/10** | **GO**, doğru daraltma ve veri stratejisiyle |

BİGGVADİ açısından zamanlama da iyi: Bilişim Vadisi, programı Ar-Ge odaklı teknoloji fikirleri için yürüttüğünü, Anadolu Isuzu ile mobilite alanında mentörlük, doğrulama ve iş birliği imkânı sunduğunu ve tematik alanlar arasında Akıllı Ulaşım ile İletişim ve Sayısal Teknolojiyi açıkça saydığını belirtiyor. citeturn24view0turn24view1

## Problem gerçekten var mı ve ekonomik değeri ne?

### Sektörde doğrulayabildiğimiz problem

ServicePilot'ın ekonomik gerekçesini “AI çok hızlı” üzerinden değil, **nitelikli teknik karar emeğinin pahalı ve kıt olması** üzerinden kurmak daha güçlü.

ATA/TMC'nin 9 Ocak 2026'da yayımladığı çalışmada 400'den fazla ağır vasıta filo üyesine 85 farklı bakım sorunu arasından en önemli beşini seçmeleri soruldu. Sonuçlarda Diagnostics üçüncü, Root Cause Analysis dördüncü, Labor Rates beşinci sırada. Bir önceki, 2025 ilkbahar araştırmasında ise Diagnostics doğrudan birinci, Technician Shortage ikinci sıradaydı. citeturn18view3

Bu iki sonuç birlikte bize şu tabloyu veriyor:

**Araçtan veri almak problem değil sadece; o veriden hızlı ve doğru teknik karar çıkarmak da problem.**

İşgücü tarafında ABD Bureau of Labor Statistics, dizel servis teknisyenleri için Mayıs 2025 medyan yıllık ücretini 61.770 dolar olarak raporluyor ve 2025–2035 boyunca yılda yaklaşık 24.400 açılış öngörüyor. Heavy Vehicle and Mobile Equipment Service Technician kategorisinde medyan yıllık ücret 63.850 dolar ve istihdam artış beklentisi %7. citeturn20search0turn20search8 Bunlar Türkiye için ücret karşılığı değildir; fakat dünya ölçeğinde **uzman teknisyen zamanının ekonomik olarak değerli bir üretim faktörü olduğunu** destekler.

Burada çok önemli bir dürüstlük çizgisi var:

> **Araştırmada ticari araç OEM'lerinde “yanlış routing vaka başına X dakika kaybettiriyor” veya “eksik kanıt vakaların %Y'sinde tekrar iletişim gerektiriyor” şeklinde güvenilir, sektöre genellenebilir açık bir veri bulamadım.**

Bu ServicePilot için kötü bir bulgu değil. Sadece problem cümlesini şu şekilde kurmamızı gerektiriyor:

> “Ticari araç sektöründe teşhis, kök neden analizi ve teknik işgücü kapasitesi belgelenmiş operasyonel sorunlardır. ServicePilot, bu toplam problemin servis vakalarının ilk teknik triyaj ve kanıt toplama bölümündeki payını ölçmeyi ve azaltmayı hedeflemektedir.” citeturn18view3turn20search0

Bu ifade jüride savunulabilir. “Isuzu yılda X milyon kaybediyor” gibi doğrulanmamış bir iddia savunulamaz.

### Anadolu Isuzu'da ürünün oturacağı yer çok net

Anadolu Isuzu'nun 26 Ocak 2021 tarihli resmî ProEye açıklaması oldukça değerli. ProEye ile satış sonrası servis destek personelinin Türkiye veya yurt dışındaki servisin telefonuna ya da VR gözlüğüne bağlanıp aracı görmesi, teknisyeni yönlendirmesi ve çözümü hızlandırması amaçlanıyor; sistem ayrıca yapılan çalışmaların kaydedilmesini ve video/doküman desteğini mümkün kılıyor. citeturn17search4

23 Eylül 2021'de açıklanan Anadolu Isuzu Technology Center modeli ise daha doğrudan: merkezde sürekli çalışan **uzman teknik destek ekibi**, sahadaki teknisyenle video görüşmesi yapabiliyor, ihtiyacı belirliyor, doküman ve prosedür paylaşabiliyor ve teknisyene araç başında ayrıntılı yönlendirme sağlıyor. citeturn17search0turn17search16

Üstelik bu yalnız geçmişte başlatılıp unutulmuş bir proje gibi görünmüyor. Anadolu Isuzu'nun Temmuz 2026'da yayımlanan 2025 Entegre Raporunun indekslenmiş metni ProEye AR uzaktan destek sisteminin satış sonrası süreçleri hızlandırmak ve verimliliği artırmak için kullanıldığını ifade ediyor. citeturn17search15

Dolayısıyla ServicePilot için **uydurulmuş bir kurumsal use-case üretmiyoruz**. Şirketin zaten sahip olduğu bir süreç var:

**Servis teknisyeni → teknik problem → merkezdeki uzman → uzaktan yönlendirme → prosedür/doküman → çözüm**

Bizim ürünümüz bunun önüne bir karar katmanı koyuyor:

**Servis teknisyeni → ServicePilot → kanıt yeterli değilse doğru kanıtı iste → yeterliyse doğru uzmanlığa route et → merkez uzman → çözüm**

Bu fark kritik.

### ServicePilot'ın satın alınabilir ekonomik birimi

İlk ticari modelde “araç başına tasarruf” yerine **servis vakası başına uzman emeği** ekonomik birim olarak kullanılmalı.

Gerçek müşteri verisi geldiğinde hesap şu olmalı:

\[
\text{Yıllık Operasyonel Fayda}
=
N_{\text{vaka}}
\times
\left[
\Delta t_{\text{uzman}}\cdot C_{\text{uzman}}
+
\Delta t_{\text{teknisyen}}\cdot C_{\text{teknisyen}}
+
\Delta t_{\text{çözüm}}\cdot C_{\text{downtime}}
\right]
\]

Burada hiçbir sayıyı bugün uydurmamamız gerekiyor.

İlk ölçülecek değerler:

| Ölçüm | Neden önemli? |
|---|---|
| Vaka başına merkez uzman dakikası | Doğrudan kapasite ve maliyet |
| İlk uzman temasından sonra ek bilgi talebi sayısı | Eksik kanıt probleminin büyüklüğü |
| Vakayı doğru teknik gruba yönlendirme süresi | Routing maliyeti |
| İlk seferde yeterli kanıtla açılan vaka oranı | ServicePilot'ın asıl müdahale noktası |
| Açılıştan çözüme kadar geçen süre | İş sonucuna bağlantı |
| Tekrar servis/tekrar teknik destek teması | “Fix-right” etkisine yaklaşan gösterge |

Böylece PoC sonunda “classifier accuracy %92” yerine **“her 100 teknik destek vakasında X uzman-saatini serbest bırakıyoruz”** denebilir. Asıl satış cümlesi budur.

## Rakipler ve gerçek pazar boşluğu

Araştırmanın en önemli kısmı burada çünkü ilk bakışta ServicePilot'ın yaptığı işin önemli bölümleri piyasada zaten bulunuyor.

### En ciddi rakip: Decisiv + TRITECH

16 Mart 2026'da Decisiv, TRITECH Expert Technician Support'u kendi Service Relationship Management platformuna entegre edeceğini açıkladı. Açıklamada amaç açıkça **commercial vehicle service operations için diagnostic time'ı azaltmak** olarak belirtiliyor. Entegrasyon yapılandırılmış araç, diagnostik ve onarım verilerini TRITECH'e aktaracak; vaka otomatik oluşturulabilecek; teknisyen canlı uzman troubleshooting, diagnostics ve parts assistance desteği alabilecek. Decisiv ayrıca platformunun 5.000'den fazla servis lokasyonu, 74.000 filo ve yılda 4 milyondan fazla servis olayıyla çalıştığını bildiriyor. citeturn18view4

Bu bulgunun iki sonucu var.

Birincisi olumlu:

**Biz hayali bir problem seçmedik.** Büyük bir commercial-vehicle service software sağlayıcısı aynı problem alanına 2026'da yatırım yapıyor.

İkincisi daha önemli:

**“Teknisyeni uzmana bağlarız” ürün tezi öldü.**

Çünkü bunu Decisiv/TRITECH zaten yapıyor.

ServicePilot'ın sorusu bir adım önce başlamalı:

> “Uzmanın karşısına bu vaka gelmeden önce gerçekten hangi kanıtların toplanmış olması gerekiyor?”

Decisiv/TRITECH'in yayımlanmış ürün açıklamasında yapılandırılmış veri aktarımı, otomatik vaka açılışı ve insan uzman desteği bulunuyor; incelediğim kamuya açık materyalde **her vaka için maliyet-duyarlı olarak bir sonraki en değerli kanıtı öğrenen adaptif bir politika** tarif edilmiyor. Bu, ServicePilot için olası boşluk; ancak rakibin yayımlamadığı dahili fonksiyonların bulunmadığını kanıtlayamayız. citeturn18view4

### Komşu rakipler de yaklaşıyor

Fullbay'in 2026'da duyurduğu AI özellikleri teknisyen notlarının düzenlenmesi, görüntülerin servis emrine alınması ve görüntülerde sorunlu görünen noktaların işaretlenmesi gibi işlevleri içeriyor. Bu, genel amaçlı “AI servis asistanı” pozisyonunun giderek metalaştığını gösteriyor. citeturn15search4turn15search13

Augmentir ise endüstriyel bakım için AI-native connected-worker platformu, dijital iş talimatları, uzaktan uzman desteği ve bakım workflow'larına bağlanan agent'lar sunuyor. Yani “AI + saha çalışanı + prosedür” alanı da boş değil. citeturn15search20turn15search11 TeamViewer Frontline Assist gibi ürünler de uzaktaki uzmanın teknisyenin gördüğünü görmesi ve canlı görsel yönlendirme vermesi problemini doğrudan çözüyor. citeturn14search18

Mercedes-Benz Trucks Uptime, Volvo Trucks'ın connected-services/Uptime yaklaşımı ve Scania'nın uzaktan diagnostik çözümleri ise araç telemetrisi üzerinden sorunu servis öncesinde anlamaya odaklanıyor. citeturn4search10turn4search9turn4search22

Dolayısıyla aşağıdaki alanlara **girmemeliyiz**:

| Konumlandırma | Karar | Neden |
|---|---|---|
| AI arıza teşhisi | **Hayır** | OEM telematics/diagnostics sistemleriyle doğrudan rekabet |
| Uzaktan uzman görüntülü görüşmesi | **Hayır** | ProEye, TeamViewer ve benzeri sistemler zaten var |
| Servis yönetim yazılımı | **Hayır** | Decisiv, Fullbay ve mevcut DMS/SRM'lerle rekabet |
| Teknik chatbot | **Kesinlikle hayır** | Düşük savunulabilirlik ve zayıf BİGG Ar-Ge tezi |
| Fotoğraftan hasar classifier | **Hayır** | Jev'in asıl avantajını kullanmıyor |
| **Aktif kanıt orkestrasyonu** | **Evet** | Mevcut sistemlerin arasına karar katmanı olarak oturabilir |

### En iyi ürün konumlandırması

Bence kategoriyi kendimiz tanımlamalıyız:

> **Active Evidence Orchestration for Technical Service**

ServicePilot'ın rakibi ProEye değildir.

ServicePilot **ProEye'ın ne zaman gerekli olduğuna karar verir.**

ServicePilot'ın rakibi DTC cihazı değildir.

ServicePilot **DTC çıktısının mevcut vakada yeterli olup olmadığına karar verir.**

ServicePilot'ın rakibi teknik uzman değildir.

ServicePilot **uzmanın önüne daha iyi hazırlanmış vaka getirir.**

Bu mimari sayesinde ürünün yalnız Isuzu'ya özgü kalması da gerekmiyor.

TEMSA, 2026 itibarıyla araçlarının 70 ülkede bulunduğunu ve 140.000'den fazla araç üretmiş olduğunu açıklıyor. citeturn20search5turn20search9 Otokar da otobüslerinin 60'tan fazla ülkede hizmet verdiğini ve satış sonrası hizmetlerini küresel operasyonunun bir parçası olarak sunduğunu belirtiyor. citeturn20search6turn20search22 Bu, dağıtık servis ağları ve merkez teknik uzmanlık modelinin Anadolu Isuzu'ya özgü olmadığını gösteren önemli bir ölçeklenme sinyali.

Dahası aynı problem otomotiv dışına da taşınabilir: iş makineleri, tarım makineleri, endüstriyel jeneratörler, HVAC sistemleri, medikal cihazlar veya havacılık bakımında da **sahadaki teknisyenin merkez uzmanına heterojen kanıtlarla vaka açması** benzer bir yapı oluşturabilir. Bu sektörlere ilişkin ürün-pazar uyumu ayrıca doğrulanmalıdır; burada yaptığım çıkarım iş akışının yapısal benzerliğine dayanıyor.

### Pazar büyüklüğü konusunda dikkat

Burada pazarlama raporları çok tutarsız. Örneğin bir ticari araştırma sağlayıcısı commercial-vehicle remote diagnostics pazarını 2024 için 5,1 milyar dolar ve 2030 için 8,2 milyar dolar olarak tahmin ederken, başka bir sağlayıcı tüm remote-vehicle diagnostics kategorisini 2025'te 17 milyar dolar olarak tahmin ediyor. Kategorilerin tanımı aynı olmadığı için bu rakamları **ServicePilot'ın TAM'i olarak kullanmak metodolojik olarak hatalı olur.** citeturn20search3turn20search7

BİGG sunumunda:

> “Global remote diagnostics pazarı X milyar dolardır, bunun %1'ini alacağız.”

demek yerine bottom-up pazar hesabı öneririm:

\[
TAM =
\sum_i
(\text{OEM}_i\text{ yıllık teknik destek vakası})
\times
(\text{vaka başına ödenebilir ServicePilot değeri})
\]

Ancak ikinci terimi gerçek müşteri PoC'si olmadan güvenilir biçimde bilmiyoruz.

Bu dürüstlük aslında jüri karşısında avantaj.

## Teknik Ar-Ge: Jev nerede oturuyor ve bizim gerçek teknolojimiz ne?

### Jev neden bu probleme iyi oturuyor?

TypeSafe'in güncel dokümantasyonunda Jev, genel amaçlı metin üretmek yerine **state + typed questions → structured decisions** modeli olarak tanımlanıyor. `Choice`, seçenek ve her seçenek için olasılık dağılımı; `Score`, rubric üzerinde skor ve dağılım; `Noul`, 0–1 arasında önerme olasılığı döndürüyor. Farklı tipte sorular aynı API isteğine konulabiliyor ve TypeSafe'e göre aynı state üzerinde bağımsız/paralel değerlendiriliyor. citeturn18view5

ServicePilot için bu özellikle uygun:

```text
STATE
 ├── technician_note
 ├── DTCs
 ├── vehicle_family
 ├── configuration
 ├── recent_repairs
 ├── currently_available_measurements
 └── photo(s) [optional]

PARALLEL DECISIONS
 ├── Choice: probable technical route
 ├── Noul: evidence sufficient?
 ├── Noul: immediate human expert required?
 ├── Score: review priority
 └── Choice: candidate next evidence
```

Ancak burada önemli bir tasarım değişikliği öneriyorum:

**Jev'e doğrudan “next_evidence nedir?” deyip onun cevabını ürünün aktif kanıt algoritması olarak sunmamalıyız.**

Çünkü o zaman tüm Ar-Ge:

> “Jev'e seçenek sorduk.”

seviyesine iner.

Jev bir **semantic sensor** gibi kullanılmalı.

Bizim algoritmamız Jev'in probability vector'larını alıp sonraki aksiyonu hesaplamalı.

### Jev'in bağımsız değerlendirmeleri ne söylüyor?

29 Eylül 2026 tarihli bağımsız Jev benchmark çalışması 37 veri setinde toplam 346.009 istek değerlendirdi. Jev 1.13.0, CLINC150 intent-routing veri setinde 151 seçenekle %89,5 doğruluk elde etti; daha ince sınıflı Banking77'de performans %79,7'ye düştü. Araştırmacılar düşük kaynaklı dillerde, ince/örtüşen sınıflarda ve gürültülü etiketlerde performans düşüşü raporluyor. citeturn24view3turn24view4

Bundan ServicePilot için önemli bir ders çıkıyor:

**Elektrik / mekanik / batarya / fren gibi kolay ayrımlar iyi çalışabilir; çok ince teknik uzmanlık sınıfları daha zor olacaktır.**

Daha da önemlisi, aynı araştırmada Jev'in confidence değerleri selective prediction için yararlı bulundu. Banking77'de yalnız en güvenli %50'lik tahminler tutulduğunda doğruluk %79,7'den %96,3'e çıktı. Fakat binary problemlerde varsayılan 0,5 eşiği her zaman iyi değildi; veri üzerinde eşik ayarlamak bazı görevlerde F1 skorunu ciddi biçimde iyileştirdi. citeturn24view5

Bu bizim ürün tezimizi güçlendiriyor:

> **Jev sonucunu “cevap” olarak değil, risk kontrollü karar politikasının girdisi olarak kullanmalıyız.**

Ayrıca görüntü tarafında acele etmemeliyiz. TypeSafe, `Box` ve görüntü desteğini açıkça “production-ready değil” şeklinde işaretliyor; API formatı, doğruluk ve limitlerin sürümler arasında değişebileceğini belirtiyor. citeturn18view6

Bu nedenle PoC'nin çekirdeği:

**text + JSON + DTC + metadata**

olmalı.

Fotoğraf:

**opsiyonel ve shadow-mode multimodal arm**

olmalı.

`Box` ise ilk BİGG MVP'sinin kritik yolunda hiç bulunmamalı.

### Active Evidence Acquisition zaten var

Burada jüri karşısında çok dikkatli davranmamız gerekiyor.

Active Feature Acquisition literatürü, **tahmin sırasında tüm bilgiyi önceden toplamak yerine, mevcut bilgiye bakarak sıradaki en yararlı özelliği edinmek ve edinim maliyetiyle doğruluğu dengelemek** problemini doğrudan ele alıyor. 2026'da güncellenen kapsamlı çalışma bunu POMDP çerçevesi üzerinden formalize ediyor. citeturn18view8

ICML 2021'de yayımlanan *Active Feature Acquisition with Generative Surrogate Models* çalışması da şu yapıyı açıkça kullanıyor: mevcut özellikler state, alınacak yeni özellik action, bilgi alma maliyeti cost ve özel bir stop action. Amaç tahmin kaybıyla kanıt toplama maliyetini birlikte minimize etmek. citeturn22view0turn23view0

ICML 2023'teki *Learning to Maximize Mutual Information for Dynamic Feature Selection* çalışması ise her örnek için mevcut bilgiye göre değişen özelliklerin seçilmesini inceliyor ve conditional mutual information tabanlı greedy politika üzerinde çalışıyor. citeturn22view1turn23view1

Dolayısıyla:

> ❌ “Biz hangi bilgiyi sırada isteyeceğini bulan yeni bir AI algoritması icat ettik.”

denemez.

Bunun yerine:

> ✅ “Mevcut aktif özellik edinimi ve selective prediction prensiplerini, maliyeti heterojen ve semantik olarak tanımlanan teknik servis kanıtlarına, typed multimodal karar modellerine ve güvenlik-duyarlı insan eskalasyonuna uyarlayan yeni bir karar politikası geliştiriyoruz.”

çok daha doğru.

### Önerdiğim özgün algoritma: RAEP

Çalışma adı:

**Risk-Aware Evidence Policy — RAEP**

Her vaka anındaki state:

\[
s_t =
\{x_t,\;p_t,\;q_t,\;m_t\}
\]

Burada:

- \(x_t\): şu ana kadar elde edilmiş gerçek servis kanıtları,
- \(p_t\): Jev'in route `Choice` olasılık vektörü,
- \(q_t\): `Noul` ve `Score` çıktıları,
- \(m_t\): araç ailesi, dil, servis noktası, risk sınıfı ve benzeri metadata.

Sistemin üç tür aksiyonu bulunur:

\[
a_t \in
\{\text{route},\text{request evidence},\text{human escalate}\}
\]

Her kanıt aksiyonunun maliyetini ayrıca modellemek gerekir:

\[
C(e)=
\alpha T_e+
\beta E_e+
\gamma S_e
\]

Burada:

- \(T_e\): kanıtı toplama süresi,
- \(E_e\): teknisyen eforu,
- \(S_e\): güvenlik/operasyon maliyeti.

Örneğin:

**“konnektörün ikinci fotoğrafını çek”** çok ucuz olabilir.

**“voltaj ölçümü yap”** daha maliyetli olabilir.

**“aracı yeniden çalıştırıp arızayı üret”** daha pahalı ve bazı vakalarda uygun olmayabilir.

**“canlı merkez uzman bağlantısı aç”** en pahalı bilgi edinim aksiyonlarından biri olabilir.

Her aday kanıt için sistem:

\[
U(e|s_t)
=
\underbrace{\widehat{R}(s_t)
-
\mathbb E[\widehat{R}(s_{t+1})|e]}_{\text{beklenen risk azalması}}
-
\lambda C(e)
\]

hesaplar.

Yani:

> **“Bu kanıtı istersem karar riskim ne kadar düşecek ve bunun operasyonel bedeli ne?”**

En yüksek faydayı veren kanıt istenir.

Eğer hiçbir kanıtın beklenen faydası maliyetinden yüksek değilse iki seçenek kalır:

**güven yeterliyse route et, değilse insana eskale et.**

### Neden bu, basit “information gain”den daha güçlü?

Çünkü gerçek servis ortamında bütün yanlış kararların maliyeti aynı değil.

Örneğin “kaporta” vakasının yanlışlıkla “mekanik” kuyruğuna gitmesiyle yüksek voltajlı batarya probleminde yanlış self-service akışına devam edilmesinin riski aynı değildir.

Bu yüzden:

\[
L(\text{critical false automation})
\gg
L(\text{ordinary misroute})
\]

olmalı.

Bu bizi **selective prediction** alanına getiriyor. Selective classification'da model, düşük güvenli durumlarda tahmin vermek yerine abstain eder; temel ölçütler risk ve coverage'dır. NeurIPS 2024 çalışması da sistemleri yalnız tek bir confidence threshold ile değil, tüm risk–coverage davranışı üzerinden değerlendirmeyi öneriyor. citeturn18view9turn19view0

Daha ilginç olarak hierarchical selective classification literatürü, modelin emin olmadığı durumda tamamen “bilmiyorum” demek yerine **daha üst/genel bir sınıfa geri çekilmesini** sağlıyor. citeturn22view2

Bu ServicePilot'a çok iyi uyuyor.

Örneğin:

```text
Powertrain
├── ICE
├── Transmission
└── Hybrid

Electrical
├── Low Voltage
├── ECU / Communication
└── High Voltage
    ├── Battery
    ├── Charging
    └── Inverter
```

Model `Battery` ile `Inverter` arasında güvenli karar veremiyorsa yanlış bir alt uzmanlığa zorlamak yerine:

**High Voltage Technical Support**

seviyesine route edebilir.

Bu özellik hem teknik olarak daha savunulabilir hem ürün açısından çok mantıklı.

### BİGG Ar-Ge tezini böyle yazardım

> **“Proje kapsamında, çok-modlu servis vakalarında typed-decision modellerinden elde edilen olasılık dağılımlarını; kanıt edinim süresi, operasyonel maliyet, vaka kritiklik seviyesi ve hiyerarşik uzmanlık yapısıyla birlikte değerlendiren risk-duyarlı aktif kanıt toplama algoritması geliştirilecektir. Algoritma, her adımda vakayı otomatik yönlendirme, yeni teknik kanıt isteme veya insan uzmana eskale etme seçenekleri arasında maliyet-risk optimizasyonu gerçekleştirecektir.”**

Bu, “Jev API kullanan uygulama”dan çok daha güçlü bir Ar-Ge projesidir.

## PoC tasarımı ve Anadolu Isuzu entegrasyonu

### Teknik mimari

ServicePilot'ı ProEye'ın yerine değil, önüne veya servis vaka yönetim sistemine paralel yerleştirmek gerekir:

```text
Servis Teknisyeni
       │
       ▼
Teknik Vaka Formu
       │
       ├── açıklama
       ├── DTC
       ├── araç konfigürasyonu
       ├── bakım geçmişi
       ├── mevcut ölçümler
       └── fotoğraf (opsiyonel)
       │
       ▼
Deterministik Safety Gate
       │
       ▼
JEV
Choice │ Noul │ Score │ ...
       │
       ▼
Probability / Typed Decision Vector
       │
       ▼
┌─────────────────────────────┐
│ ServicePilot RAEP Engine    │
│                             │
│ risk calibration            │
│ evidence-value estimation   │
│ acquisition cost model      │
│ hierarchical routing        │
│ escalation policy           │
└─────────────────────────────┘
        │
   ┌────┼───────────┐
   ▼    ▼           ▼
ROUTE   REQUEST     HUMAN
        EVIDENCE    EXPERT
                    │
                    ▼
                ProEye /
              Expert Desk
```

Burada Jev **karar motorunun tamamı değil**.

Jev:

> anlamsal sinyalleri çok hızlı şekilde yapılandırılmış olasılıklara dönüştürüyor.

RAEP:

> bu sinyallere bakarak operasyonel aksiyonu seçiyor.

Bu ayrım hem IP hem vendor bağımlılığı açısından önemli. ServicePilot'ın iç modeli:

```python
DecisionProvider
```

gibi soyut bir arabirim üzerinden tasarlanırsa bugün Jev, ileride başka bir System One/typed-decision modeli veya şirket içi model kullanılabilir.

### Hangi veri gerçekten gerekiyor?

İlk offline deney için yalnızca “servis açıklaması + final diagnosis” yetersiz.

Asıl Ar-Ge iddiasını test etmek için **vakanın zaman içindeki akışı** lazım.

| Veri | Önemi |
|---|---|
| İlk teknisyen açıklaması | Başlangıç state'i |
| İlk DTC'ler | Başlangıç teknik kanıtı |
| Araç ailesi / konfigürasyonu | Routing ve prior |
| İlk gönderilen görseller | Mevcut kanıt |
| İlk yönlendirilen uzmanlık | Routing ground truth adayı |
| Uzmanın istediği ek bilgi | **Aktif kanıt öğrenimi için kritik** |
| İstenen ek fotoğraf/ölçüm | Evidence action |
| Her mesaj/aksiyon timestamp'i | Süre KPI'ları |
| Nihai çözüm / teknik kategori | Outcome |
| Eskalasyon bilgisi | Risk ground truth |
| Dil / ülke / servis noktası | Distribution shift testi |

Bunların en kritik olanı:

> **“Uzman ilk vakayı görünce hangi ek kanıtı istedi?”**

Bu veri tutulmuyorsa ServicePilot'ın classifier/routing kısmını hâlâ geliştirebiliriz.

Ancak **active evidence policy'yi gerçek veriden öğrenmek çok daha zorlaşır.**

### Çok önemli metodolojik risk: counterfactual problem

Diyelim geçmiş vakada uzman:

> “Konnektörün yakından fotoğrafını gönder.”

dedi.

Bizim algoritma ise:

> “Voltaj ölçümü iste.”

diyor.

Geçmiş kayıttan hangisinin daha iyi olduğunu bilemeyiz; çünkü voltaj ölçümü yapılmadı.

Bu bir **counterfactual evaluation** problemidir.

Dolayısıyla geçmiş veride yalnızca:

> “algoritma uzmanla aynı kanıtı istedi mi?”

ölçmek yetmez.

Önerim PoC'yi iki aşamaya bölmek.

### Offline replay

İlk aşamada kapatılmış vakalar kullanılır.

Vakanın final kanıtlarını algoritmadan saklarız.

Örneğin sadece:

```text
t0:
technician note
DTC
vehicle configuration
```

verilir.

Sistem karar verir:

```text
route?
request?
escalate?
```

Sonra gerçek geçmişte gelen bir sonraki kanıt açılır.

Böylece sıralı replay yapılabilir.

Bu aşamada karşılaştırılacak baselinelar:

| Sistem | Ne yapıyor? |
|---|---|
| **Baseline A** | Mevcut/manual geçmiş süreç |
| **Baseline B** | Sabit kanıt checklist'i |
| **Baseline C** | Jev tek-shot routing |
| **Baseline D** | Jev confidence threshold + human |
| **ServicePilot** | Jev + RAEP active evidence policy |

Bu yapı BİGG için çok güçlü bir deney tasarımı oluşturur.

### Shadow mode

Offline replay başarılı olduktan sonra sistem 2–3 servis noktasında veya merkez teknik destek masasında **shadow mode** çalışır.

Gerçek teknisyene hiçbir otomatik teknik talimat verilmez.

Sistem yalnız arka planda:

```text
Ben olsam:
→ battery support'a route ederdim
→ connector photo isterdim
→ human escalation önerirdim
```

diye log tutar.

Gerçek uzman ne yaptı?

Karşılaştırılır.

Bu hem güvenlik riskini ciddi azaltır hem gerçek veri toplamayı sağlar.

### Gerçekçi haftalık plan

| Dönem | Çalışma |
|---|---|
| **Hafta 1–2** | Vaka taksonomisi, veri şeması, expert-route ağacı, safety rules |
| **Hafta 3–4** | 500–2.000 kapalı vaka ile dataset oluşturma; baseline Jev routing |
| **Hafta 5–6** | Calibration, risk–coverage ve hierarchical routing |
| **Hafta 6–8** | Evidence-value model ve RAEP policy |
| **Hafta 8–9** | Historical replay ve ablation testleri |
| **Hafta 9–10** | Dil, araç ailesi ve servis lokasyonuna göre subgroup testleri |
| **Hafta 10–12** | Shadow-mode pilot ve operasyon KPI ölçümü |

**500–2.000 vaka burada doğrulanmış Anadolu Isuzu veri hacmi değildir; PoC tasarım önerisidir.** Veri sayısı, mevcut kayıtların kalitesine göre yeniden hesaplanmalıdır.

### Başarı kriterleri

Ana KPI'ları doğru seçmişiz. Ben yalnız biraz yeniden düzenlerdim:

**Birincil iş KPI'ları**

| KPI | Asıl soru |
|---|---|
| `median time-to-correct-route` | Vaka doğru yere daha hızlı gidiyor mu? |
| `expert minutes / case` | Uzman kapasitesi gerçekten serbest kalıyor mu? |
| `additional evidence requests / case` | Daha doğru kanıtı daha erken mi topluyoruz? |
| `first-contact evidence completeness` | İlk seferde hazırlanmış vaka oranı artıyor mu? |

**Güvenlik KPI'ları**

| KPI | Asıl soru |
|---|---|
| `critical escalation recall` | Kritik vakayı kaçırıyor muyuz? |
| `selective risk @ coverage` | Ne kadarını güvenli otomatikleştirebiliyoruz? |
| `risk-coverage curve / AURC` | Automation arttıkça hata nasıl büyüyor? |

**Model KPI'ları**

`route accuracy`, `top-2 accuracy`, `ECE/Brier veya benzeri calibration`, dil/araç ailesine göre subgroup performance.

Sadece:

> **Accuracy = %94**

sunmamalıyız.

Bunun yerine:

> **“%50 otomasyon coverage'ında yanlış routing riski X; %70 coverage'da Y; kritik sınıflarda recall Z.”**

demek çok daha profesyonel.

Jev'in bağımsız benchmark'ında confidence ile düşük güvenli cevaplar elendiğinde doğruluğun belirgin şekilde artması da bu değerlendirme yaklaşımının teknik gerekçesini destekliyor. citeturn24view5

## Ticarileşme ve BİGG stratejisi

### İlk müşteri

**Anadolu Isuzu Satış Sonrası Hizmetler / teknik destek organizasyonu**

en mantıklı ilk hedef.

Bunun üç nedeni var.

BİGGVADİ programı Anadolu Isuzu'yu resmen mobilite alanındaki stratejik ortak olarak gösteriyor ve girişimlere doğrulama/iş birliği fırsatları sunduğunu belirtiyor. citeturn24view0

Anadolu Isuzu'nun ProEye ve Technology Center ile dağıtık servislerden merkez uzman desteğine giden dijital bir iş akışı zaten bulunuyor. citeturn17search4turn17search16

Ürün araç üzerindeki safety-critical fonksiyonlara müdahale etmiyor; servis workflow'unda **decision support** olarak başlayabildiği için PoC riski ADAS gibi bir üründen çok daha düşük.

### Türkiye'deki ikinci dalga

PoC başarılı olursa doğal adaylar:

**TEMSA, Otokar, Ford Trucks/Mercedes-Benz Türk ve benzer uluslararası servis ağı bulunan OEM'ler.**

TEMSA araçlarının 70 ülkede bulunduğunu bildiriyor; Otokar 60'tan fazla ülkeyi kapsayan otobüs operasyonundan söz ediyor. Bu şirketlerin gerçek teknik destek süreçlerinin Anadolu Isuzu ile birebir aynı olduğunu iddia edemeyiz, ancak küresel servis ağı ölçeği benzer bir problem sınıfının bulunma ihtimalini ciddi biçimde artırıyor. citeturn20search5turn20search22

### Sonraki pazar aslında daha büyük olabilir

ServicePilot'ın en değerli taraflarından biri “otomotiv ürünü” olmak zorunda olmaması.

Ürün çekirdeği:

> **distributed field technician + centralized expertise + costly evidence acquisition**

problemini çözüyor.

Dolayısıyla uzun vadede dikeyler:

```text
Commercial Vehicles
       ↓
Construction Equipment
       ↓
Agricultural Machinery
       ↓
Industrial Machinery
       ↓
HVAC / Energy Systems
       ↓
Medical Device Field Service
```

olabilir.

Bu noktada girişimin marka ve teknoloji mimarisini “Isuzu servis uygulaması” şeklinde değil, **industrial technical-service decision infrastructure** şeklinde kurmak daha doğru.

### Fiyatlandırma

Bugün spesifik TL veya dolar rakamı vermek için yeterli piyasa verisi yok.

En mantıklı model:

**Enterprise platform subscription + usage component**

olur.

Örneğin:

\[
\text{Yıllık Lisans}
+
(\text{aktif teknik destek vakası}\times \text{usage})
+
\text{entegrasyon}
\]

Alternatif olarak büyük OEM'lerde:

**ülke / servis noktası / aktif teknisyen lisansı**

kullanılabilir.

Ancak ServicePilot'ın fiyat tavanını API maliyeti değil, yarattığı uzman kapasitesi belirlemeli.

Örneğin müşterinin yılda:

\[
N\times\Delta t
\]

uzman-saat kazanmasını sağlıyorsak satış argümanı Jev'in çağrı maliyeti değil **kurtarılan servis kapasitesi ve downtime** olur.

### BİGGVADİ'ye uyum

BİGGVADİ'nin resmî sayfası programı teknoloji tabanlı ve Ar-Ge odaklı iş fikirlerine yönelik tanımlıyor; Anadolu Isuzu ile mobilite doğrulaması/iş birliği fırsatlarını açıkça belirtiyor ve tematik alanlarda Akıllı Ulaşım ile İletişim ve Sayısal Teknolojiyi kapsıyor. citeturn24view0turn24view1 Ayrıca mevcut sayfada Mükemmeliyet Mührü alan şirketler için TÜBİTAK BİGG Fonu'nun %3 hisse karşılığında 1.350.000 TL yatırım yaptığı belirtiliyor. citeturn24view2

ServicePilot bu programa bence **“AI destekli servis yazılımı” olarak değil**, şu çerçevede sunulmalı:

> **Akıllı ulaşım sistemlerinde satış sonrası teknik operasyonların ölçeklenmesini sağlayan risk-duyarlı adaptif karar teknolojisi.**

## Nihai karar, riskler ve başvuruda kullanacağım tez

### En büyük riskler

| Risk | Ciddiyet | Neden | Karşı hamle |
|---|---:|---|---|
| **Geçmişte hangi kanıtın ne zaman istendiğinin kayıtlı olmaması** | Çok yüksek | Active evidence modelini öğrenmek zorlaşır | Offline masked replay + uzman etiketleri + shadow-mode veri toplama |
| **Decisiv/Augmentir benzeri oyuncuların aynı özelliği hızla eklemesi** | Yüksek | Genel AI özellikleri kolay kopyalanabilir | IP'yi Jev entegrasyonunda değil risk/evidence policy ve veri katmanında oluştur |
| **Jev'in domain calibration'ının yetersiz olması** | Yüksek | Genel benchmark servis verisini temsil etmiyor | Her dil/araç ailesi için ayrı calibration ve selective thresholds |
| **Görüntü desteğinin olgun olmaması** | Orta-yüksek | TypeSafe görüntüyü production-ready saymıyor | MVP text/JSON-first; görüntü yalnız shadow-mode/optional |
| **Yanlış routing veya automation'ın kritik vakayı geciktirmesi** | Çok yüksek | Safety ve operasyon riski | Deterministic safety gate + critical-class recall constraint + human abstention |

Jev tarafındaki risk özellikle gerçek. Bağımsız benchmark sonuçları modelin routing ve selective prediction açısından umut verici olduğunu gösterirken, ince sınıflarda performansın düştüğünü ve binary threshold'ların domain verisinde yeniden ayarlanması gerektiğini de gösteriyor. citeturn24view3turn24view4turn24view5

### GO / PIVOT / NO-GO

## **GO**

Ama **yalnızca aşağıdaki ürün tanımıyla**:

> **ServicePilot — dağıtık teknik servis organizasyonlarında eksik ve heterojen vakaları, risk ve bilgi değeri tabanlı olarak tamamlayan ve doğru uzmanlığa yönlendiren aktif kanıt orkestrasyon sistemi.**

Şu ürün tanımıyla ise:

> “Jev kullanıp servis notlarını ve fotoğrafları classify eden AI servis asistanı.”

**NO-GO derdim.**

Çünkü bunda ne güçlü moat var ne de yeterli BİGG Ar-Ge derinliği.

### Bence en güçlü tek problem cümlemiz

> **“Dağıtık ticari araç servis ağlarında merkez teknik uzmanları, çözüm için gereken kanıtları eksik veya heterojen biçimde gelen vakaları değerlendirmek ve eksik kanıtı tekrar istemek zorunda kalabilmektedir. ServicePilot, her vaka için karar vermeye en çok katkı sağlayacak sıradaki teknik kanıtı risk ve edinim maliyetini birlikte değerlendirerek seçmeyi ve yeterli kanıt oluştuğunda vakayı doğru uzmanlığa yönlendirmeyi amaçlamaktadır.”**

Bu cümlede doğrulayamadığımız hiçbir sayı veya Isuzu iç KPI'ı yok. Buna rağmen gerçek ve satın alınabilir bir probleme işaret ediyor.

### En güçlü ürün cümlesi

> **“Uzmanı AI ile değiştirmiyoruz; uzmanın önüne gelen vakayı hazırlıyoruz.”**

### En güçlü teknik cümle

> **“Geliştirilecek risk-duyarlı aktif kanıt politikası, düşük gecikmeli typed-decision modellerinin olasılık çıktılarını; kanıt toplama süresi, teknisyen eforu, vaka kritiklik seviyesi ve hiyerarşik uzmanlık yapısıyla birlikte değerlendirerek her adımda yeni kanıt isteme, otomatik yönlendirme veya insan eskalasyonu arasında karar verecektir.”**

### En güçlü Jev anlatımı

Jev'i başvuruya **ürün olarak değil teknoloji bileşeni olarak** yazardım:

> “Projenin anlamsal karar katmanında düşük gecikmeli typed-decision modellerinden yararlanılacaktır. Bu modeller aynı vaka state'i üzerinde teknik yönlendirme, kanıt yeterliliği, kritiklik ve eskalasyon gibi dar kararlar için yapılandırılmış olasılık çıktıları sağlayacaktır. Projenin özgün Ar-Ge bileşeni bu çıktıları nihai karar olarak kullanmak yerine risk ve kanıt maliyetiyle kalibre eden aktif karar politikasıdır.”

Bu ifade TypeSafe'in Jev için tavsiye ettiği atomik soru ve kod tarafında kompozisyon yaklaşımıyla da doğrudan uyumlu. citeturn18view5

### BİGG için araştırma hipotezi

Bence başvuruya taşıyacağımız bilimsel/teknik hipotez artık oldukça net:

> **H₁:** *Risk-duyarlı ve maliyet-duyarlı aktif kanıt seçimi kullanan ServicePilot, aynı güvenlik seviyesinde sabit servis checklist'i ve tek-aşamalı AI routing yöntemlerine kıyasla doğru teknik yönlendirmeye ulaşmak için gereken ortalama kanıt toplama maliyetini ve uzman müdahalesini azaltabilir.*

Bunu dört sistemle test ederiz:

\[
\text{Manual}
\quad vs \quad
\text{Fixed Checklist}
\quad vs \quad
\text{One-Shot Jev}
\quad vs \quad
\boxed{\text{Jev + ServicePilot RAEP}}
\]

Ve başarı ölçümüz:

\[
\boxed{
\text{daha düşük expert-minutes}
+
\text{daha az evidence request}
+
\text{daha kısa routing time}
}
\]

**aynı veya daha düşük kritik-vaka riski altında.**

Bu, BİGG açısından bence projenin en güçlü hali. Çünkü teknoloji yalnızca “classification” yapmıyor; **classification'ın gerçek endüstriyel ekonomik değere dönüşmesini sağlayan adaptif karar sistemi geliştiriyoruz.**

Ayrıca araştırmanın sonucu bize bir stratejik avantaj daha veriyor: Anadolu Isuzu'nun ProEye'ı bizim rakibimiz değil, **ServicePilot'ın neden var olması gerektiğini açıklayan mevcut operasyonel altyapı**. Decisiv/TRITECH ise problemin ticari olarak satın alınabilir olduğunu doğruluyor. Active Feature Acquisition literatürü de problemin teknik olarak ciddiye alınmış bir araştırma alanı olduğunu gösteriyor. citeturn17search4turn18view4turn18view8

Dolayısıyla nihai tez basitçe **“Jev hızlı, bunu serviste kullanalım”** değil:

> **“Uzaktan teknik servis sistemleri bugün uzmanı sahaya bağlayabiliyor; uzaktan diagnostik sistemleri araçtan veri çekebiliyor. Eksik kalan katman, hangi vakada hangi kanıtın sırada toplanacağını ve ne zaman artık insana ihtiyaç olduğunu ekonomik risk altında optimize eden karar altyapısıdır. ServicePilot bu katmanı ürünleştiriyor.”**

Bu haliyle benim değerlendirmem **GO: 8/10**, ve şimdiye kadar BİGGVADİ–Anadolu Isuzu ekseninde araştırdığımız fikirler arasında **hem gerçek kurumsal altyapıya bağlanması hem Jev'in özgün avantajını doğru yerde kullanması hem de BİGG'e sunulabilecek ölçülebilir bir Ar-Ge hipotezi bulunması açısından en güçlü adaylardan biri**.