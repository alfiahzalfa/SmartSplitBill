import base64
import json
import os
from io import BytesIO

from groq import Groq
from PIL import Image

from modules.data.receipt_data import AdditionalCharge, ItemData, ReceiptData
from modules.utils import AIError, SettingsError

from .base import AIModel

MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"

PROMPT = """
You are given an image of a receipt/bill. Extract all data into this exact JSON format:

{
    "menus": [
        {
            "name": "<item name>",
            "count": <quantity as integer, default 1 if not shown>,
            "price": <total price for this line item as plain number>
        }
    ],
    "additional_charges": [
        {
            "name": "<charge label, e.g. PPN 10%, Service Charge, Discount>",
            "amount": <amount as plain number, NEGATIVE for discounts>
        }
    ],
    "subtotal": <sum of all menu item prices, BEFORE any extra charges>,
    "total": <final grand total the customer pays>
}

Rules:
- Prices are plain numbers WITHOUT comma separators. Example: 15000 not 15,000
- count defaults to 1 if not explicitly shown
- additional_charges = [] if none exist on the receipt
- subtotal = sum of menu items only (before tax/service/discount)
- total = final amount after all charges

Return ONLY the JSON object, no explanation, no markdown backticks.
"""


class GroqModel(AIModel):
    """Receipt reader menggunakan Groq API (LLaMA Vision) sebagai alternatif Gemini."""

    def __init__(self) -> None:
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise SettingsError(
                "Groq API Key belum diset. Silakan set di Settings. "
                "Daftar gratis di https://console.groq.com"
            )
        self.client = Groq(api_key=api_key)

    def run(self, image: Image.Image) -> ReceiptData:
        image_b64 = self._encode_image(image)
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_b64}"
                                },
                            },
                            {
                                "type": "text",
                                "text": PROMPT,
                            },
                        ],
                    }
                ],
                temperature=0,
                max_tokens=2000,
            )
            raw = response.choices[0].message.content
            return self._parse_response(raw)
        except Exception as err:
            raise AIError(f"Groq API error: {err}") from err

    def _encode_image(self, image: Image.Image) -> str:
        """Encode gambar ke base64."""
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _parse_response(self, response: str) -> ReceiptData:
        """Parse JSON response dari Groq menjadi ReceiptData."""
        clean = response.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(clean)
        except json.JSONDecodeError as err:
            raise AIError(f"Gagal parsing respons Groq: {response}") from err

        items = [
            ItemData(
                name=str(item["name"]),
                count=int(item.get("count", 1)),
                total_price=float(item["price"]),
            )
            for item in data.get("menus", [])
        ]

        charges = [
            AdditionalCharge(
                name=str(ch["name"]),
                amount=float(ch["amount"]),
            )
            for ch in data.get("additional_charges", [])
        ]

        total = float(data.get("total", sum(it.total_price for it in items)))
        return ReceiptData(
            items={it.id: it for it in items},
            total=total,
            additional_charges=charges,
        )