from bs4 import BeautifulSoup


def analyze_forms(html):
    """
    Analyze all forms present on the webpage.
    """

    soup = BeautifulSoup(html, "lxml")

    forms = soup.find_all("form")

    form_details = []

    total_inputs = 0
    total_buttons = 0
    email_fields = 0
    password_fields = 0
    search_fields = 0
    hidden_fields = 0
    checkbox_fields = 0

    for index, form in enumerate(forms, start=1):

        inputs = form.find_all("input")
        buttons = form.find_all("button")

        total_inputs += len(inputs)
        total_buttons += len(buttons)

        form_type = "Unknown Form"

        for field in inputs:

            field_type = field.get("type", "text").lower()

            if field_type == "email":
                email_fields += 1
                form_type = "Login / Registration"

            elif field_type == "password":
                password_fields += 1
                form_type = "Login Form"

            elif field_type == "search":
                search_fields += 1
                form_type = "Search Form"

            elif field_type == "hidden":
                hidden_fields += 1

            elif field_type == "checkbox":
                checkbox_fields += 1

        if "contact" in form.get_text().lower():
            form_type = "Contact Form"

        form_details.append({
            "Form": index,
            "Type": form_type,
            "Inputs": len(inputs),
            "Buttons": len(buttons)
        })

    return {

        "forms_found": len(forms),

        "form_details": form_details,

        "total_inputs": total_inputs,

        "total_buttons": total_buttons,

        "email_fields": email_fields,

        "password_fields": password_fields,

        "search_fields": search_fields,

        "hidden_fields": hidden_fields,

        "checkbox_fields": checkbox_fields

    }