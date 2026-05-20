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

        // Buton durumlarını ayarla
        prevButton.disabled = stepIndex === 0;
        
        if (stepIndex === steps.length - 2) {
            nextButton.innerHTML = 'HESAPLA <i class="fa-solid fa-wand-magic-sparkles"></i>';
            nextButton.style.backgroundColor = 'var(--accent-bordo)';
        } else if (stepIndex === steps.length - 1) {
            nextButton.style.display = 'none';
            prevButton.style.display = 'none';
        } else {
            nextButton.innerHTML = 'İLERİ <i class="fa-solid fa-chevron-right"></i>';
            nextButton.style.backgroundColor = 'var(--primary)';
        }
    }

    nextButton.addEventListener("click", function () {
        // Eğer belirtiler adımındaysak ve Hesapla'ya basıldıysa sunucuya gönder
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
            kirsal_temas: document.getElementById("kirsal_temas")?.checked ? 1 : 0,
            kemirgen_temas: document.getElementById("kemirgen_temas")?.checked ? 1 : 0,
            ates: document.getElementById("ates")?.checked ? 1 : 0,
            kas_agrisi: document.getElementById("kas_agrisi")?.checked ? 1 : 0,
            bulanti: document.getElementById("bulanti")?.checked ? 1 : 0,
            nefes_darligi: document.getElementById("nefes_darligi")?.checked ? 1 : 0
        };

        const adSoyad = document.getElementById("ad_soyad").value || "İsimsiz Hasta";
        const bolge = document.getElementById("bolge").value;

        fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById("res-isim").innerText = adSoyad + " — " + bolge + " Bölgesi";
                document.getElementById("riskScore").innerText = data.risk_score;
                document.getElementById("riskStatus").innerText = "RİSK SEVİYESİ: " + data.risk_status;
                
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
