# src/summariser.py

from dataclasses import dataclass
from typing import List

from transformers import pipeline


@dataclass
class SummaryResult:
    tldr: str
    bullet_points: List[str]


class NewsSummariser:
    """
    Real summariser (first version).

    - Uses a small transformer summarisation model for the TL;DR.
    - Bullet points are still dummy for now (we'll improve that later).
    """

    def __init__(
        self,
        model_name: str = "sshleifer/distilbart-cnn-12-6",
        device: int = -1,  # -1 = CPU, 0 = first GPU if you have one
    ) -> None:
        # Create a summarisation pipeline using a pre-trained model.
        # This is loaded once when you create the NewsSummariser.
        self._summariser = pipeline(
            "summarization",
            model=model_name,
            tokenizer=model_name,
            device=device,
        )

    def summarise(self, text: str, max_chars: int = 300) -> SummaryResult:
        """
        Summarise the given text into:
          - a TL;DR paragraph (using the transformer model)
          - dummy bullet points (for now)

        max_chars here is an approximate control on length;
        we convert it into a rough token limit.
        """
        text = text.strip()

        if not text:
            return SummaryResult(tldr="", bullet_points=[])

        # For now, if the text is extremely long, truncate it so the model doesn't choke.
        # Later we can add a smarter "chunking" strategy.
        max_input_chars = 4000  # arbitrary for now
        if len(text) > max_input_chars:
            text = text[:max_input_chars]

        # Rough mapping: characters → tokens is not exact, but this is fine for now.
        # We map max_chars to a max_length in tokens.
        max_tokens = max(50, min(200, max_chars))  # keep it in a safe range

        # Call the transformer summarisation pipeline for the TL;DR
        summary_output = self._summariser(
            text,
            max_length=max_tokens,
            min_length=max_tokens // 4,
            do_sample=False,  # deterministic
            truncation=True,  # safely cut inputs that are too long

        )

        # The pipeline returns a list of dicts; we take the first one
        tldr = summary_output[0]["summary_text"].strip()

        # Now generate bullet points using a second call.
        # We tell the model explicitly what format we want.
        bullet_prompt = (
            "Summarise the following text into 3–5 short bullet points. "
            "Return them as separate lines, each starting with a dash '-'.\n\n"
            + text
        )

        bullets_output = self._summariser(
            bullet_prompt,
            max_length=max_tokens,
            min_length=max_tokens // 4,
            do_sample=False,
            truncation=True,  # safely cut inputs that are too long

        )

        bullets_text = bullets_output[0]["summary_text"].strip()

        # Parse the model output into a list of bullet strings.
        bullet_lines = []
        for line in bullets_text.splitlines():
            line = line.strip()
            if not line:
                continue
            # Remove leading bullet characters like "-", "•", etc.
            if line[0] in "-•*":
                line = line[1:].strip()
            bullet_lines.append(line)

        # Fallback: if model didn't break into lines, split by sentences.
        if len(bullet_lines) <= 1:
            parts = bullets_text.replace("•", "").split(". ")
            bullet_lines = [p.strip().strip(".") for p in parts if p.strip()]

        # Keep at most 5 bullet points
        bullet_points = bullet_lines[:5]

        return SummaryResult(tldr=tldr, bullet_points=bullet_points)

