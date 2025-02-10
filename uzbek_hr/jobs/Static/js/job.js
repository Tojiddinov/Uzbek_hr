document.addEventListener("DOMContentLoaded", function() {
    let universityStatus = document.querySelector("#id_is_university_student");
    let universityInfo = document.querySelector("#university-info");
    let graduateInfo = document.querySelector("#graduate-info");

    function toggleFields() {
        if (universityStatus && universityStatus.value === "Yes") {
            universityInfo.style.display = "block";
            graduateInfo.style.display = "none";
        } else if (universityStatus) {
            universityInfo.style.display = "none";
            graduateInfo.style.display = "block";
        }
    }

    if (universityStatus) {
        universityStatus.addEventListener("change", toggleFields);
        toggleFields();
    }
});
document.addEventListener("DOMContentLoaded", function () {
    let studyYearsPicker = flatpickr("#id_study_years", {
        mode: "range",
        dateFormat: "Y",
        minDate: "2000",
        maxDate: "2035",
        onChange: function(selectedDates) {
            if (selectedDates.length === 2) {
                let startYear = selectedDates[0].getFullYear();
                let endYear = selectedDates[1].getFullYear();
                document.querySelector("#id_graduation_year").value = endYear; // Tugatish yilini avtomatik to'ldirish
            }
        }
    });

    flatpickr("#id_graduation_year", {
        dateFormat: "Y",
        minDate: "2000",
        maxDate: "2035"
    });
});


document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("resumeForm").onsubmit = async function (e) {
        e.preventDefault();
        let formData = new FormData(this);

        let response = await fetch("/upload_resume/", {
            method: "POST",
            body: formData,
        });

        let data = await response.json();
        if (data.status === "success") {
            document.getElementById("result").classList.remove("hidden");
            let questionsList = document.getElementById("questionsList");
            questionsList.innerHTML = "";
            data.questions.split("\n").forEach(q => {
                let li = document.createElement("li");
                li.textContent = q;
                questionsList.appendChild(li);
            });
        }
    };
});
