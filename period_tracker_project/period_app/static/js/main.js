document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('form');

    form.addEventListener('submit', function (event) {
        event.preventDefault();  // Zatrzymanie domyślnego działania formularza

        const formData = new FormData(form);
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': form.querySelector('[name="csrfmiddlewaretoken"]').value
            }
        })
        .then(response => {
            if (response.ok) {
                window.location.href = '/calendar/';
            } else {
                response.text().then(errorText => {
                    alert('Wystąpił błąd: ' + errorText);
                });
            }
        })
        .catch(error => {
            alert('Wystąpił błąd: ' + error);
        });
    });
});


