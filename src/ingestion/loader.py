import fitz  # PyMuPDF
import os
from pathlib import Path

def load_pdfs_from_folder(folder_path: str) -> list[dict]:
    """
    Loads all PDFs from a folder.
    Returns a list of {text, metadata} dicts — one per page.
    """
    all_pages = []
    pdf_files = list(Path(folder_path).glob("*.pdf"))

    if not pdf_files:
        print(f"No PDFs found in {folder_path}")
        return []

    for pdf_path in pdf_files:
        print(f"Loading: {pdf_path.name}")
        try:
            doc = fitz.open(str(pdf_path))
            for page_num, page in enumerate(doc):
                text = page.get_text().strip()
                if len(text) < 50:   # skip blank/header-only pages
                    continue
                all_pages.append({
                    "text": text,
                    "metadata": {
                        "source_file": pdf_path.name,
                        "page_num": page_num + 1,
                        "subject_tag": pdf_path.stem.split("_")[0].lower()
                    }
                })
            doc.close()
        except Exception as e:
            print(f"Error loading {pdf_path.name}: {e}")

    print(f"\nLoaded {len(all_pages)} pages from {len(pdf_files)} PDFs")
    return all_pages