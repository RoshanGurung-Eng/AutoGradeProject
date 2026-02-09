import easyocr
import re
def preprocess_image(image_path):
    # (your gentle preprocessing)
    #return enhanced_path
    pass

def run_ocr(image_path, use_preprocessing=False):
    if use_preprocessing:
        image_path = preprocess_image(image_path)
    reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    return reader.readtext(image_path, detail=0, paragraph=True)



def tokenize_lines(raw_results):
    """Split raw OCR lines into tokens using robust splitting."""
    all_tokens = []
    corrected_lines = []
    for line in raw_results:
        tokens = re.split(r'[_\s~@#$%^&*+=]+', line)
        cleaned_tokens = []
        for token in tokens:
            if len(token) == 0:
                continue
            if not any(c.isalpha() for c in token):
                continue
            if len(token) == 1 and token.lower() not in ['a', 'i']:
                continue
            all_tokens.append(token)
            cleaned_tokens.append(token)
        if cleaned_tokens:
            corrected_lines.append(" ".join(cleaned_tokens))
    return all_tokens, corrected_lines
