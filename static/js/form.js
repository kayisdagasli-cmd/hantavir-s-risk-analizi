document.addEventListener("DOMContentLoaded", function () {
    const steps = document.querySelectorAll(".form-step");
    const nextButton = document.getElementById("btn-next");
    const prevButton = document.getElementById("btn-back");
    const wizardSteps = document.querySelectorAll(".step-wizard .step");
    let currentStep = 0;

    function showStep(stepIndex) {
        steps.forEach((step, index) => {
            step.classList.toggle("active", index === stepIndex);
        });
        wizardSteps.forEach((step, index) => {
            step.classList.toggle("active", index === stepIndex);
        });

        prevButton.disabled = stepIndex === 0;
        
        if (stepIndex === steps.length - 2) {
            nextButton.innerHTML = 'HESAPLA <i class="fa-solid fa-wand-magic-sparkles"></i>';
            nextButton.style.backgroundColor = '#8b0000'; // Bordo renk vurgusu
        } else if (stepIndex === steps.length - 1) {
            nextButton.style.display = 'none';
            prevButton.style.display = 'none';
        } else {
            nextButton.innerHTML = 'İLERİ <i class="fa-solid fa-chevron-right"></i>';
            nextButton.style.backgroundColor = ''; 
        }
    }

    nextButton.addEventListener("click", function () {
        if (currentStep === steps.length - 2) {
            hesaplaVeGonder();
        } else if (currentStep < steps.length - 2) {
            currentStep++;
            showStep(currentStep);
        }
    });

    prevButton.addEventListener("click", function () {
        if (currentStep > 0) {
            currentStep--;
            showStep(currentStep);
        }
    });

    function hesaplaVeGonder() {
        const formData = {
            yas: parseInt(document.getElementById("yas").value) || 0,
            cinsiyet: parseInt(document.getElementById("cinsiyet").value) || 0,
            bolge: document.getElementById("bolge").value,
            cevre_tipi: document.getElementById("cevre_tipi").value,
            
            // Maruziyetler
            kirsal_temas: document.getElementById("kirsal_temas")?.checked ? 1 : 0,
            kemirgen_temas: document.getElementById("kemirgen_temas")?.checked ? 1 : 0,
            toz_maruziyeti: document.getElementById("toz_maruziyeti")?.checked ? 1 : 0,
            son_seyahat: document.getElementById("son_seyahat")?.checked ? 1 : 0,
            bagisiklik: document.getElementById("bagisiklik")?.checked ? 1 : 0,
            
            // Semptomlar
            ates: document.getElementById("ates")?.checked ? 1 : 0,
            kas_agrisi: document.getElementById("kas_agrisi")?.checked ? 1 : 0,
            bas_agrisi: document.getElementById("bas_agrisi")?.checked ? 1 : 0,
            yorgunluk: document.getElementById("yorgunluk")?.checked ? 1 : 0,
            bulanti: document.getElementById("bulanti")?.checked ? 1 : 0,
            nefes_darligi: document.getElementById("nefes_darligi")?.checked ? 1 : 0
        };

        const adSoyad = document.getElementById("ad_soyad").value || "Anonim Vaka";

        fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById("res-isim").innerText = adSoyad + " — " + formData.bolge + " Bölgesi";
                document.getElementById("riskScore").innerText = data.risk_score;
                document.getElementById("riskStatus").innerText = "RİSK SEVİYESİ: " + data.risk_status;
                
                // Klinik dinamik öneriler ekleme alanı
                const list = document.getElementById("suggestions-list");
                list.innerHTML = ""; // Temizle
                
                if (formData.nefes_darligi) {
                    list.innerHTML += "<li style='color: #ff4d4d; font-weight: bold;'><i class='fa-solid fa-circle-exclamation'></i> ACİL DURUM: Nefes darlığı hantavirüs için kritik bir evredir. En yakın sağlık kuruluşuna başvurun!</li>";
                }
                if (data.risk_score >= 50) {
                    list.innerHTML += "<li><i class='fa-solid fa-triangle-exclamation'></i> Risk puanınız yüksek çıkmıştır. Kan tetkiki (Hantavirüs IgM/IgG) yaptırmanız önerilir.</li>";
                } else {
                    list.innerHTML += "<li><i class='fa-solid fa-circle-check'></i> Risk seviyeniz düşük seyrediyor. Hijyen kurallarına ve kemirgen kontrolüne devam edin.</li>";
                }

                currentStep = steps.length - 1;
                showStep(currentStep);
            } else {
                alert("Hata: " + data.error);
            }
        })
        .catch(error => {
            alert("Sistem hatası: " + error.message);
        });
    }
});
