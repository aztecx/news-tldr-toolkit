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

        # Call the transformer summarisation pipeline
        summary_output = self._summariser(
            text,
            max_length=max_tokens,
            min_length=max_tokens // 4,
            do_sample=False,  # deterministic
        )

        # The pipeline returns a list of dicts; we take the first one
        tldr = summary_output[0]["summary_text"].strip()

        # Bullet points: still dummy for this step
        bullet_points = [
            "This is a placeholder bullet list.",
            "The TL;DR above already comes from a real summarisation model.",
            "In the next step, we will also generate real bullet points.",
        ]

        return SummaryResult(tldr=tldr, bullet_points=bullet_points)
