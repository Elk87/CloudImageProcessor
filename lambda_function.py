import json
import base64
import io
from PIL import Image, ImageOps

def lambda_handler(event, context):
    try:
        # 1) Parámetros en la query string (para la acción).
        query_params = event.get("queryStringParameters") or {}
        action = query_params.get("action", "grayscale").lower()
        width_str = query_params.get("width")
        height_str = query_params.get("height")

        # 2) Validamos que llegue "body" y en base64
        if "body" not in event or not event["body"]:
            return {
                "statusCode": 400,
                "body": "No image found in body."
            }
        if not event.get("isBase64Encoded", False):
            return {
                "statusCode": 400,
                "body": "The body was not base64 encoded."
            }

        # 3) Decodificamos la imagen
        image_data = base64.b64decode(event["body"])
        image = Image.open(io.BytesIO(image_data))

        # 4) Procesamos la imagen (grayscale o resize)
        if action == "grayscale":
            image = ImageOps.grayscale(image)
        elif action == "resize":
            if not width_str or not height_str:
                return {
                    "statusCode": 400,
                    "body": "For 'resize' you must provide 'width' and 'height' in the query string."
                }
            width = int(width_str)
            height = int(height_str)
            image = image.resize((width, height))
        else:
            return {
                "statusCode": 400,
                "body": f"Unsupported action '{action}'. Use 'grayscale' or 'resize'."
            }

        # 5) Guardamos la imagen resultante en un buffer (binario)
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        buffer.seek(0)

        # 6) Convertimos a base64 para el "body" de la respuesta
        output_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # 7) Construir la respuesta en JSON.
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "image": output_base64
            }),
            "isBase64Encoded": False  # Enfoque B => Va como JSON de texto normal
        }


    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
