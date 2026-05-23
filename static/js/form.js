document.addEventListener("DOMContentLoaded", () => {

    // =========================
    // ELEMENTLER
    // =========================
    const steps = document.querySelectorAll(".form-step");
    const wizardSteps = document.querySelectorAll(".step");

    const nextBtn = document.getElementById("btn-next");
    const backBtn = document.getElementById("btn-back");

    let currentStep = 0;

    // =========================
    // STEP GÖSTER
    // =========================
    function showStep(index) {

        steps.forEach((step, i) => {
            step.classList.toggle("active", i === index);
        });

        wizardSteps.forEach((step, i) => {
            step.classList.toggle("active", i === index);
        });

        // Geri butonu
        backBtn.disabled = index === 0;

        // Sonuç ekranı
        if (index === steps.length - 1) {

            nextBtn.style.display = "none";
            backBtn.style.display = "none";

        } else {

            nextBtn.style.display = "flex";
            backBtn.style.display = "flex";

        }

        // Hesapla butonu
        if (index === steps.length - 2) {

            nextBtn.innerHTML =
                'ANALYZE RISK <i class="fa-solid fa-wand-magic-sparkles"></i>';

            nextBtn.classList.add("danger-btn");

        } else {

            nextBtn.innerHTML =
                'NEXT <i class="fa-solid fa-chevron-right"></i>';

            nextBtn.classList.remove("danger-btn");
        }
    }

    // =========================
    // NEXT
    // =========================
    nextBtn.addEventListener("click", async () => {

        // Son adım öncesi -> API
        if (currentStep === steps.length - 2) {

            await analyzeRisk();

        } else {

            currentStep++;
            showStep(currentStep);

        }
    });

    // =========================
    // BACK
    // =========================
    backBtn.addEventListener("click", () => {

        if (currentStep > 0) {

            currentStep--;
            showStep(currentStep);

        }
    });

    // =========================
    // ANALİZ
    // =========================
    async function analyzeRisk() {

        try {

            // =========================
            // LOADING
            // =========================
            nextBtn.innerHTML =
                '<i class="fa-solid fa-spinner fa-spin"></i> ANALYZING...';

            nextBtn.disabled = true;

            // =========================
            // FORM DATA
            // =========================
            const data = {

                age: parseInt(document.getElementById("age").value) || 0,

                gender: document.getElementById("gender").value,

                fever:
                    document.getElementById("fever").checked ? 1 : 0,

                cough:
                    document.getElementById("cough").checked ? 1 : 0,

                breath_shortness:
                    document.getElementById("breath_shortness").checked ? 1 : 0,

                rodent_contact:
                    document.getElementById("rodent_contact").checked ? 1 : 0,

                humidity: Math.floor(Math.random() * 40) + 40,

                temperature: Math.floor(Math.random() * 15) + 15
            };

            // =========================
            // API REQUEST
            // =========================
            const response = await fetch("/api/predict", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(data)
            });

            const result = await response.json();

            // =========================
            // ERROR
            // =========================
            if (!result.success) {

                alert(result.error || "Prediction failed.");

                nextBtn.disabled = false;

                return;
            }

            // =========================
            // RESULT UI
            // =========================
            renderResults(result, data);

            // Son adıma geç
            currentStep = steps.length - 1;

            showStep(currentStep);

        } catch (error) {

            console.error(error);

            alert("System error occurred.");

        } finally {

            nextBtn.disabled = false;

        }
    }

    // =========================
    // RESULT RENDER
    // =========================
    function renderResults(result, formData) {

        const scoreElement =
            document.getElementById("riskScore");

        const statusElement =
            document.getElementById("riskStatus");

        const suggestionsList =
            document.getElementById("suggestions-list");

        const patientText =
            document.getElementById("res-isim");

        // =========================
        // HASTA BİLGİSİ
        // =========================
        patientText.innerText =
            `Age ${formData.age} • ${formData.gender}`;

        // =========================
        // SCORE ANIMATION
        // =========================
        animateScore(
            scoreElement,
            result.risk_score
        );

        // =========================
        // RISK STATUS
        // =========================
        statusElement.innerText =
            result.risk_level.toUpperCase();

        // =========================
        // RISK COLORS
        // =========================
        if (result.risk_score < 40) {

            statusElement.style.background =
                "#1e8e3e";

        } else if (result.risk_score < 70) {

            statusElement.style.background =
                "#f9a825";

        } else {

            statusElement.style.background =
                "#c62828";
        }

        // =========================
        // CLINICAL SUGGESTIONS
        // =========================
        suggestionsList.innerHTML = "";

        // Kritik semptom
        if (formData.breath_shortness) {

            suggestionsList.innerHTML += `
                <li class="danger-text">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                    Severe respiratory symptom detected.
                    Immediate medical evaluation recommended.
                </li>
            `;
        }

        // Risk bazlı öneriler
        if (result.risk_score >= 70) {

            suggestionsList.innerHTML += `
                <li>
                    <i class="fa-solid fa-virus"></i>
                    High-risk clinical profile detected.
                    Laboratory testing strongly recommended.
                </li>
            `;

        } else if (result.risk_score >= 40) {

            suggestionsList.innerHTML += `
                <li>
                    <i class="fa-solid fa-stethoscope"></i>
                    Moderate risk detected.
                    Monitor symptoms carefully.
                </li>
            `;

        } else {

            suggestionsList.innerHTML += `
                <li>
                    <i class="fa-solid fa-circle-check"></i>
                    Low risk profile detected.
                    Continue preventive measures.
                </li>
            `;
        }

        // Genel bilgi
        suggestionsList.innerHTML += `
            <li>
                <i class="fa-solid fa-circle-info"></i>
                AI prediction results are not a final diagnosis.
            </li>
        `;
    }

    // =========================
    // SCORE ANIMATION
    // =========================
    function animateScore(element, targetScore) {

        let current = 0;

        const interval = setInterval(() => {

            current++;

            element.innerText = current;

            if (current >= targetScore) {

                clearInterval(interval);

            }

        }, 20);
    }

    // =========================
    // INIT
    // =========================
    showStep(currentStep);

});
