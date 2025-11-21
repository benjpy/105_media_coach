import os
from google import genai
from google.genai import types
from PIL import Image
import io

def generate_journalist_portrait(persona):
    """Generates a journalist portrait based on the persona."""
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    prompt = f"""
    Professional headshot of a journalist. 
    Persona details: {persona}.
    High quality, realistic, professional lighting, 8k resolution.
    """
    
    try:
        response = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",
                safety_filter_level="block_low_and_above",
                person_generation="allow_adult",
            )
        )
        if response.generated_images:
            img_obj = response.generated_images[0].image
            # The SDK returns a Pydantic object, we need to convert it to PIL
            if hasattr(img_obj, 'image_bytes'):
                return Image.open(io.BytesIO(img_obj.image_bytes))
            return img_obj
        else:
            raise Exception("No image returned")
    except Exception as e:
        print(f"Error generating journalist portrait: {e}")
        raise

def generate_outlet_logo(outlet_name):
    """Generates a news outlet logo."""
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    prompt = f"""
    Modern, professional news outlet logo for '{outlet_name}'.
    Minimalist, trustworthy, bold typography.
    Vector art style, white background.
    """
    
    try:
        response = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",
                safety_filter_level="block_low_and_above",
            )
        )
        if response.generated_images:
            img_obj = response.generated_images[0].image
            # The SDK returns a Pydantic object, we need to convert it to PIL
            if hasattr(img_obj, 'image_bytes'):
                return Image.open(io.BytesIO(img_obj.image_bytes))
            return img_obj
        else:
            raise Exception("No image returned")
    except Exception as e:
        print(f"Error generating logo: {e}")
        raise

def generate_assets(persona, outlet_name):
    """Generates both journalist portrait and outlet logo."""
    try:
        journalist_img = generate_journalist_portrait(persona)
        logo_img = generate_outlet_logo(outlet_name)
        return journalist_img, logo_img
    except Exception as e:
        print(f"Error generating assets: {e}")
        return None, None
