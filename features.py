from tqdm import tqdm
from openai import OpenAI
import os

from parsers import classifier_parser, parse_generated_text, extract_category
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Read the API key from the environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def classify_product_category(product_attributes, product_categories=None):

    # Initialize the OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)
  
    # Step 2: Generate important keywords from product attributes
    attribute_keywords = ", ".join([f"{key}: {value}" for key, value in product_attributes.items()])

    # Create a system message
    system_message = "You are an AI assistant specialized in classifying product categories."

    if product_categories:
      # Generate a prompt with the list of categories
      category_prompt = f"Based on the following attributes: {attribute_keywords}, choose the most relevant category strictly from the following list: {product_categories}. Category:"
    
    else:
      category_prompt = f"Based on the following attributes: {attribute_keywords}, assign the most relevant category on your own. Generate only one word. One word Category:"

    # Use Chat Completion API to select a category
    chat_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": category_prompt},
        ],
        max_tokens=32,  # Limit the response to a reasonable length
        n=1,
        stop=None,
        temperature=0.1,
    )

    # Extract and clean the predicted category
    predicted_category = chat_response.choices[0].message.content

    if product_categories:
      matching_category = extract_category(predicted_category)
      #matching_category = classifier_parser(predicted_category, product_categories)
    else:
      matching_category = predicted_category

    return matching_category


def generate_product_description(product_attributes, tone_of_voice="neutral"):
    # Initialize the OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # print(f"Product Attributes: {product_attributes}\n")

    # print(f"Tone of Voice: {tone_of_voice}\n")

    # Step 1: Use the Vision API to get an image description
    image_description_prompt = "Please analyze the following image and provide a concise textual description of the product:"

    image_url = product_attributes['ImageURL']
    
    vision_response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": image_description_prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        max_tokens=256,
    )

    # Extract the image description from the Vision API response
    image_description = vision_response.choices[0].message.content

    print(f"Image Description: {image_description}\n")


    # Step 2: Generate important keywords from product attributes
    attribute_keywords = ", ".join([f"{key}: {value}" for key, value in product_attributes.items()])

    print(f"Product Keywords: {attribute_keywords}\n")

    # Step 3: Use the Chat Completion API to generate a product description
    system_message = "You are an AI assistant specialized in creating product descriptions."
    product_description_prompt = f"Generate an SEO-optimized product description for the product with the following attributes: {attribute_keywords}. Image Description: {image_description}. Tone of Voice: {tone_of_voice}. Product Description:"

    chat_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": product_description_prompt},
        ],
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Extract and return the generated product description
    generated_product_description = parse_generated_text(chat_response.choices[0].message.content)
    return generated_product_description
