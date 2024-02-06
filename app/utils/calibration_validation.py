import json

from PyQt5.QtWidgets import QMessageBox
from jsonschema import validate

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


def validate_calibration(data):
    try:
        json_data = json.loads(data)
        validate(instance=json_data, schema=schema)
        return True
    except Exception as e:
        show_error(QMessageBox.Critical, "Неверный формат файла", "Файл неизвестного формата")
        print(e)
        return False
