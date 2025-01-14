import json
import base64
from PIL import Image, ImageOps
import io

def lambda_handler(event, context):
    try:
        # Decodificar la imagen desde el cuerpo de la solicitud
        if 'body' not in event:
            return {"statusCode": 400, "body": json.dumps({"error": "No image provided"})}

        body = event['body']
        is_base64_encoded = event.get("isBase64Encoded", False)

        if is_base64_encoded:
            image_data = base64.b64decode(body)
        else:
            return {"statusCode": 400, "body": json.dumps({"error": "Image must be base64 encoded"})}

        # Leer la imagen desde los datos binarios
        image = Image.open(io.BytesIO(image_data))

        # Leer los parámetros de la solicitud para determinar la acción
        query_params = event.get("queryStringParameters", {})
        action = query_params.get("action", "grayscale").lower()
        width = query_params.get("width")
        height = query_params.get("height")

        # Procesar la imagen según la acción
        if action == "grayscale":
            # Convertir a escala de grises
            image = ImageOps.grayscale(image)
        elif action == "resize":
            if not width or not height:
                return {"statusCode": 400, "body": json.dumps({"error": "Width and height are required for resizing"})}
            image = image.resize((int(width), int(height)))
        else:
            return {"statusCode": 400, "body": json.dumps({"error": "Unsupported action. Use 'grayscale' or 'resize'"})}

        # Guardar la imagen procesada en un buffer
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        buffer.seek(0)

        # Codificar la imagen resultante en base64
        encoded_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Devolver la imagen procesada como respuesta
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"image": encoded_image}),
            "isBase64Encoded": True
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }