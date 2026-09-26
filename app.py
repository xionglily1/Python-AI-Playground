from decimal import Decimal, InvalidOperation

from flask import Flask, render_template, request

app = Flask(__name__)


def format_number(value):
    if value == 0:
        return "0"
    formatted = format(value, "f")
    if "." in formatted:
        formatted = formatted.rstrip("0").rstrip(".")
    return formatted


def calculate(left, right, operator):
    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    if operator == "/":
        if right == 0:
            raise ZeroDivisionError
        return left / right
    return right


@app.route("/", methods=["GET", "POST"])
def calculator():
    display = "0"
    stored_value = ""
    operator = ""
    replace_display = True
    tone = "0"

    if request.method == "POST":
        display = request.form.get("display", "0")[:16]
        stored_value = request.form.get("stored_value", "")[:64]
        operator = request.form.get("operator", "")
        replace_display = request.form.get("replace_display") == "true"
        tone = request.form.get("tone", "0")
        if tone not in "0123456789":
            tone = "0"

        key = request.form.get("key", "")
        try:
            if key == "clear":
                display, stored_value, operator = "0", "", ""
                replace_display, tone = True, "0"
            elif key.isdigit() and len(key) == 1:
                if replace_display or display == "0" or display == "Error":
                    display = key
                elif len(display) < 16:
                    display += key
                replace_display = False
                tone = key
            elif key == "decimal":
                if replace_display or display == "Error":
                    display = "0"
                if "." not in display:
                    display += "."
                replace_display = False
            elif key in ("+", "-", "*", "/"):
                current = Decimal(display)
                if operator and not replace_display:
                    current = calculate(Decimal(stored_value), current, operator)
                    display = format_number(current)
                stored_value = format_number(current)
                operator = key
                replace_display = True
            elif key == "equals" and operator:
                result = calculate(Decimal(stored_value), Decimal(display), operator)
                display = format_number(result)
                stored_value, operator = "", ""
                replace_display = True
        except (InvalidOperation, ValueError, ZeroDivisionError):
            display = "Cannot divide by zero" if key == "equals" else "Error"
            stored_value, operator = "", ""
            replace_display = True

    return render_template(
        "index.html",
        display=display,
        stored_value=stored_value,
        operator=operator,
        replace_display=replace_display,
        tone=tone,
    )


if __name__ == "__main__":
    app.run(debug=True)