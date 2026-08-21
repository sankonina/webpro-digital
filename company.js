const form = document.querySelector(".contact-form");

if (form) {

    form.addEventListener("submit", async function(event) {

        event.preventDefault();

        const customer = {

            name: form.querySelector('[name="name"]').value,

            phone: form.querySelector('[name="phone"]').value,

            business: form.querySelector('[name="business"]').value,

            service: form.querySelector('[name="service"]').value,

            message: form.querySelector('[name="message"]').value
        };


        try {

            const response = await fetch("/customers", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(customer)

            });


            const result = await response.json();


            if (result.success) {

                alert("תודה! הפרטים שלך התקבלו בהצלחה.");

                form.reset();

            } else {

                alert("אירעה שגיאה.");

            }

        } catch (error) {

            alert("לא ניתן להתחבר לשרת.");

            console.error(error);

        }

    });

}