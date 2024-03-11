import json

from PyQt5.QtWidgets import QMessageBox
from jsonschema import validate
from app.locales.locales import locales
from app.utils.error_messages import show_error

schema = {
    "type": "object",
    "properties": {
        "yLabel": {"type": "string"},
        "calibrationData": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer"},
                    "y": {"type": "number"}
                },
                "required": ["x", "y"]
            }
        }
    },
    "required": ["yLabel", "calibrationData"]
}


def validate_calibration(data, locale):
    try:
        json_data = json.loads(data)
        validate(instance=json_data, schema=schema)
        return True
    except Exception as e:
        show_error(QMessageBox.Critical, locales[locale]["invalid_file_format"], locales[locale]["unknown_format_file"])
        print(e)
        return False
