from bs4 import BeautifulSoup
import re


def clean_html(text: str) -> str:

    if not text:
        return ""

    soup = BeautifulSoup(text, "html.parser")

    text = soup.get_text(separator=" ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()