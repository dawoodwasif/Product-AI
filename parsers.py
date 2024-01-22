import re

def extract_category(input_string):
    # Use regex to find the text inside double quotes
    match = re.search(r'"([^"]*)"', input_string)
    
    # If a match is found, return the extracted text; otherwise, return None
    return match.group(1) if match else None


def classifier_parser(predicted_category, product_categories):
  
    predicted_category = re.sub(r'[^a-zA-Z0-9 ]', '', predicted_category)  # Remove non-alphanumeric characters

    # Split words based on capitalization
    predicted_category = re.sub(r'([a-z])([A-Z])', r'\1 \2', predicted_category)

    matching_category = None

    # Iterate through product categories and check for a match
    for category in product_categories:
        if category.lower() in predicted_category.lower():
            matching_category = category
            break
    
    return matching_category

def parse_generated_text(generated_text):
    # Split the text into paragraphs based on double line breaks
    paragraphs = generated_text.split("\n\n")

    # Select the first paragraph
    first_paragraph = paragraphs[0] if paragraphs else ""

    # Split the paragraph into sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', first_paragraph)

    # Limit to the first 4 sentences if there are more
    if len(sentences) > 5:
        first_paragraph = ' '.join(sentences[:4])

    # Remove extra whitespaces and line breaks
    cleaned_text = " ".join(first_paragraph.split())

    return cleaned_text