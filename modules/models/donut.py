import re
import torch
import xmltodict
from PIL import Image
from transformers import AutoModelForVision2Seq, AutoProcessor

from modules.data.receipt_data import ItemData, ReceiptData

from .base import AIModel

MODEL_NAME = "naver-clova-ix/donut-base-finetuned-cord-v2"


class DonutModel(AIModel):
    """Receipt reader menggunakan Donut (lokal, tanpa API key)."""

    def __init__(self):
        self.processor = AutoProcessor.from_pretrained(MODEL_NAME)
        self.model = AutoModelForVision2Seq.from_pretrained(
            MODEL_NAME, 
            device_map="cpu",
            ignore_mismatched_sizes=True
        )
        self.model.eval()

    def run(self, image: Image.Image) -> ReceiptData:
        decoder_input_ids, pixel_values = self._preprocess(image)
        generation_output = self._inference(decoder_input_ids, pixel_values)
        receipt_dict = self._postprocessing(generation_output)
        return self._formatting(receipt_dict)

    def _preprocess(self, image: Image.Image):
        decoder_input_ids = self.processor.tokenizer(
            "<s_cord-v2>", add_special_tokens=False
        ).input_ids
        decoder_input_ids = torch.tensor(decoder_input_ids).unsqueeze(0)
        pixel_values = self.processor(image, return_tensors="pt").pixel_values
        return decoder_input_ids, pixel_values

    def _inference(self, decoder_input_ids, pixel_values):
        with torch.no_grad():
            generation_output = self.model.generate(
                pixel_values,
                decoder_input_ids=decoder_input_ids,
                max_length=self.model.decoder.config.max_position_embeddings,
                pad_token_id=self.processor.tokenizer.pad_token_id,
                eos_token_id=self.processor.tokenizer.eos_token_id,
                use_cache=True,
                num_beams=1,
                bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
                return_dict_in_generate=True,
            )
        return generation_output

    def _postprocessing(self, generation_output) -> dict:
        decoded = self.processor.batch_decode(generation_output.sequences)[0]

        decoded = decoded.replace(self.processor.tokenizer.eos_token, "")
        decoded = decoded.replace(self.processor.tokenizer.pad_token, "")
        decoded = decoded.replace(self.processor.tokenizer.bos_token, "")
        decoded = decoded.strip()

        if not decoded.startswith("<s_cord-v2>"):
            decoded = "<s_cord-v2>" + decoded

        if not decoded.endswith("</s_cord-v2>"):
            matches = list(re.finditer(r"</\w+>", decoded))
            if matches:
                decoded = decoded[:matches[-1].end()]
            decoded += "</s_cord-v2>"

        try:
            return xmltodict.parse(decoded)
        except Exception:
            return {"s_cord-v2": {}}

    def _formatting(self, receipt_dict: dict) -> ReceiptData:
        data = receipt_dict.get("s_cord-v2", {})
        menus_raw = data.get("s_menu", {})

        def to_list(val):
            if val is None:
                return []
            return val if isinstance(val, list) else [val]

        if isinstance(menus_raw, list):
            menu_items = menus_raw
        elif isinstance(menus_raw, dict):
            names = to_list(menus_raw.get("s_nm"))
            counts = to_list(menus_raw.get("s_cnt"))
            prices = to_list(menus_raw.get("s_price"))
            n = max(len(names), len(prices))
            menu_items = [
                {
                    "s_nm": names[i] if i < len(names) else "Item",
                    "s_cnt": counts[i] if i < len(counts) else "1",
                    "s_price": prices[i] if i < len(prices) else "0",
                }
                for i in range(n)
            ]
        else:
            menu_items = []

        items = []
        for m in menu_items:
            try:
                items.append(
                    ItemData(
                        name=str(m.get("s_nm", "Item")),
                        count=max(1, int(str(m.get("s_cnt", "1")).replace(",", ""))),
                        total_price=_safe_float(m.get("s_price", "0")),
                    )
                )
            except Exception:
                continue

        total_raw = data.get("s_total", {})
        if isinstance(total_raw, dict):
            total = _safe_float(total_raw.get("s_total_price", "0"))
        else:
            total = _safe_float(str(total_raw))

        if total == 0 and items:
            total = sum(it.total_price for it in items)

        return ReceiptData(
            items={it.id: it for it in items},
            total=total,
            additional_charges=[],
        )


def _safe_float(val) -> float:
    """Konversi string harga ke float, handle koma sebagai separator."""
    try:
        return float(str(val).replace(",", "").strip())
    except (ValueError, TypeError):
        return 0.0