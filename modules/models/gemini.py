import base64
import json
import os
from io import BytesIO

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from PIL import Image

from modules.data.receipt_data import AdditionalCharge, ItemData, ReceiptData
from modules.utils import AIError, SettingsError

from .base import AIModel

MODEL_NAME = "gemini-2.0-flash"

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


class GeminiModel(AIModel):
    """Receipt reader menggunakan Gemini vision API."""

    def __init__(self) -> None:
        if "GOOGLE_API_KEY" not in os.environ or os.environ["GOOGLE_API_KEY"] == "":
            raise SettingsError(
                "Google API Key belum diset. Silakan set di Settings."
            )
        self.llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.0)

    def run(self, image: Image.Image) -> ReceiptData:
        image_b64 = self._encode_image(image)
        message = HumanMessage(
            content=[
                {"type": "text", "text": PROMPT},
                {
                    "type": "image_url",
                    "image_url": f"data:image/png;base64,{image_b64}",
                },
            ]
        )
        response = self.llm.invoke([message]).content
        if not isinstance(response, str):
            raise AIError(f"Gemini tidak merespons dengan string: {response}")
        try:
            return self._parse_response(response)
        except Exception as err:
            raise AIError(f"Gagal parsing respons Gemini: {response}") from err

    def _encode_image(self, image: Image.Image) -> str:
        """Encode gambar ke base64 untuk dikirim ke Gemini."""
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _parse_response(self, response: str) -> ReceiptData:
        """Parse teks JSON dari Gemini menjadi ReceiptData."""
        # Bersihkan markdown jika ada
        clean = response.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean)

        # Parse items
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
