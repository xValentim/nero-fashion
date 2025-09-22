import os
from typing import List, Optional
from io import BytesIO
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()  # Carrega variáveis de ambiente do arquivo .env


class ImageRemixService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.5-flash-image-preview"

    def _bytes_to_genai_part(self, image_bytes: bytes, mime_type: str) -> types.Part:
        """Converts image bytes to GenAI Part object."""
        return types.Part(
            inline_data=types.Blob(data=image_bytes, mime_type=mime_type)
        )

    def _detect_mime_type(self, image_bytes: bytes) -> str:
        """Detects MIME type from image bytes."""
        # Check image signature to determine format
        if image_bytes.startswith(b'\xff\xd8'):
            return 'image/jpeg'
        elif image_bytes.startswith(b'\x89PNG'):
            return 'image/png'
        elif image_bytes.startswith(b'GIF'):
            return 'image/gif'
        elif image_bytes.startswith(b'WEBP', 8):
            return 'image/webp'
        else:
            return 'image/jpeg'  # default fallback

    def remix_images_from_bytes(
        self,
        image1_bytes: bytes,
        image2_bytes: bytes,
        prompt: str,
        stream: bool = False
    ) -> BytesIO:
        """
        Remixes two images from bytes using Gemini AI.

        Args:
            image1_bytes: First image as bytes
            image2_bytes: Second image as bytes
            prompt: Text prompt for remixing
            stream: Whether to use streaming response

        Returns:
            BytesIO: The remixed image as BytesIO object
        """
        # Detect MIME types
        mime_type1 = self._detect_mime_type(image1_bytes)
        mime_type2 = self._detect_mime_type(image2_bytes)

        # Create GenAI parts
        contents = [
            self._bytes_to_genai_part(image1_bytes, mime_type1),
            self._bytes_to_genai_part(image2_bytes, mime_type2),
            types.Part.from_text(text=prompt)
        ]

        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        )

        if stream:
            return self._process_stream_response(contents, generate_content_config)
        else:
            return self._process_response(contents, generate_content_config)

    def _process_response(self, contents: List[types.Part], config: types.GenerateContentConfig) -> BytesIO:
        """Process non-streaming response and return image as BytesIO."""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config,
        )

        # Extract image from response
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                image_bytesio = BytesIO(part.inline_data.data)
                image_bytesio.seek(0)  # Reset position to beginning
                return image_bytesio

        raise ValueError("No image found in response")

    def _process_stream_response(self, contents: List[types.Part], config: types.GenerateContentConfig) -> BytesIO:
        """Process streaming response and return image as BytesIO."""
        stream = self.client.models.generate_content_stream(
            model=self.model_name,
            contents=contents,
            config=config,
        )

        for chunk in stream:
            if (
                chunk.candidates is None
                or chunk.candidates[0].content is None
                or chunk.candidates[0].content.parts is None
            ):
                continue

            for part in chunk.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytesio = BytesIO(part.inline_data.data)
                    image_bytesio.seek(0)  # Reset position to beginning
                    return image_bytesio

        raise ValueError("No image found in streaming response")


def remix_images_service(
    image1_bytes: bytes,
    image2_bytes: bytes,
    prompt: str,
    api_key: Optional[str] = None,
    stream: bool = False
) -> BytesIO:
    """
    Convenience function to remix two images.

    Args:
        image1_bytes: First image as bytes
        image2_bytes: Second image as bytes
        prompt: Text prompt for remixing
        api_key: Optional API key (uses env var if not provided)
        stream: Whether to use streaming response

    Returns:
        BytesIO: The remixed image as BytesIO object
    """
    service = ImageRemixService(api_key)
    return service.remix_images_from_bytes(image1_bytes, image2_bytes, prompt, stream)

class ImageDescriptionService:
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model_name: str="gemini-2.5-flash-image-preview"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

    def _bytes_to_genai_part(self, image_bytes: bytes, mime_type: str) -> types.Part:
        """Converts image bytes to GenAI Part object."""
        return types.Part(
            inline_data=types.Blob(data=image_bytes, mime_type=mime_type)
        )

    def _detect_mime_type(self, image_bytes: bytes) -> str:
        """Detects MIME type from image bytes."""
        if image_bytes.startswith(b'\xff\xd8'):
            return 'image/jpeg'
        elif image_bytes.startswith(b'\x89PNG'):
            return 'image/png'
        elif image_bytes.startswith(b'GIF'):
            return 'image/gif'
        elif image_bytes.startswith(b'WEBP', 8):
            return 'image/webp'
        else:
            return 'image/jpeg'  # default fallback

    def describe_image_from_bytes(self, image_bytes: bytes, prompt: Optional[str] = None, stream: bool = False) -> str:
        """Descreve uma imagem a partir de bytes usando Gemini AI e retorna texto."""
        mime_type = self._detect_mime_type(image_bytes)
        content = [
            self._bytes_to_genai_part(image_bytes, mime_type),
            types.Part.from_text(text=prompt) if prompt else types.Part.from_text(text="Describe this image."),
        ]
        generate_content_config = types.GenerateContentConfig(response_modalities=["TEXT"])
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=content,
            config=generate_content_config,
        )
        # Extrai texto do response
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text') and part.text:
                return part.text
            elif hasattr(part, 'inline_data') and part.inline_data and part.inline_data.data:
                try:
                    return part.inline_data.data.decode('utf-8')
                except Exception:
                    pass
        raise ValueError("No text found in response")

def describe_image_service(image_bytes: bytes, 
                           prompt: str, 
                           api_key: Optional[str] = None,
                           model_name: str="gemini-2.5-flash-image-preview") -> str:
    """Função simples para descrever uma imagem usando Gemini AI."""
    service = ImageDescriptionService(api_key,
                                      model_name=model_name)
    return service.describe_image_from_bytes(image_bytes, prompt)

# Lista explícita dos produtos que podem ser usados ou vestidos
POSSIBLE_PRODUCTS = [
    "Sunglasses",  # óculos de sol
    "Tank Top",    # regata/camiseta
    "Watch",       # relógio
    "Loafers"      # sapatos/mocassins
]

IDS = {
    "Sunglasses": "OLJCESPC7Z",
    "Tank Top": "66VCHSJNUP",
    "Watch": "1YMWWN1N4O",
    "Loafers": "L9ECAV7KIM",
    "None": "None"
}

class ProductChoice(BaseModel):
    product: str = Field(..., description="Escolha do produto: Sunglasses, Tank Top, Watch, Loafers ou Nenhum.", example=["Sunglasses", "Tank Top", "Watch", "Loafers", "Nenhum"])

def analyze_product_choice(text: str, 
                           model_name: str="gemini-2.5-flash") -> list[ProductChoice]:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = (
        "Você é um assistente muito útil. Analise o texto do usuário e responda de forma clara e objetiva qual produto ele deseja vestir ou usar dentre as opções abaixo. "
        "Se não quiser nenhum, responda explicitamente 'Nenhum'.\n"
        "Produtos disponíveis:\n"
        "- Sunglasses (óculos de sol)\n"
        "- Tank Top (regata/camiseta)\n"
        "- Watch (relógio)\n"
        "- Loafers (sapatos/mocassins)\n"
        "\nTexto do usuário: '" + text + "'\nResposta:"
    )
    response = client.models.generate_content(
        model=model_name,
        contents=[prompt],
        config={
            "response_mime_type": "application/json",
            "response_schema": list[ProductChoice],
        },
    )
    return response.parsed

class ImageSellProductService:
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model_name: str="gemini-2.5-flash-image-preview",
                 text: str="I really like sunglasses, can you help me?"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        # print(self.api_key)
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name
        self.text = text

    def _classify_text(self, text: str) -> str:
        """Classifies the text using the GenAI model."""
        response = analyze_product_choice(text, 
                                          model_name="gemini-2.5-flash")
        return response

    def _bytes_to_genai_part(self, image_bytes: bytes, mime_type: str) -> types.Part:
        """Converts image bytes to GenAI Part object."""
        return types.Part(
            inline_data=types.Blob(data=image_bytes, mime_type=mime_type)
        )

    def _detect_mime_type(self, image_bytes: bytes) -> str:
        """Detects MIME type from image bytes."""
        if image_bytes.startswith(b'\xff\xd8'):
            return 'image/jpeg'
        elif image_bytes.startswith(b'\x89PNG'):
            return 'image/png'
        elif image_bytes.startswith(b'GIF'):
            return 'image/gif'
        elif image_bytes.startswith(b'WEBP', 8):
            return 'image/webp'
        else:
            return 'image/jpeg'  # default fallback

    def _format_product(self, product: dict) -> str:
        return f"ID: {product['id']}, Nome: {product['name']}, Descrição: {product['description']}, Preço: {product['price']}, Categoria: {product['categories']}"

    def extract_product_from_text(self, text: str) -> dict:
        """Extracts the product choice from text."""
        choices = self._classify_text(text)
        if choices and choices[0].product in POSSIBLE_PRODUCTS:
            return {"name": choices[0].product,
                    "id": IDS[choices[0].product]}
        return {"name": "None",
                "id": IDS["None"]}

    def sell_product_from_image_from_bytes(self, 
                                           image_bytes: bytes, 
                                           prompt: Optional[str] = None, 
                                           product: dict = {},
                                           stream: bool = False) -> str:
        """Descreve uma imagem a partir de bytes usando Gemini AI e retorna texto."""
        mime_type = self._detect_mime_type(image_bytes)
        content = [
            self._bytes_to_genai_part(image_bytes, mime_type),
            types.Part.from_text(text="User Text: " + self.text),
            types.Part.from_text(text="Recommended Product: " + self._format_product(product)),
            types.Part.from_text(text=prompt) if prompt else types.Part.from_text(text="Describe this image."),
        ]
        generate_content_config = types.GenerateContentConfig(response_modalities=["TEXT"])
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=content,
            config=generate_content_config,
        )
        # Extrai texto do response
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text') and part.text:
                return part.text
            elif hasattr(part, 'inline_data') and part.inline_data and part.inline_data.data:
                try:
                    return part.inline_data.data.decode('utf-8')
                except Exception:
                    pass
        raise ValueError("No text found in response")
    
def sell_product_from_image_service(image_bytes: bytes, 
                                    text: str,
                                    product: dict,
                                    prompt: str, 
                                    api_key: Optional[str] = None,
                                    model_name: str="gemini-2.5-flash-image-preview") -> str:
    """Função simples para descrever uma imagem usando Gemini AI."""
    service = ImageSellProductService(api_key,
                                      model_name=model_name,
                                      text=text)
    return service.sell_product_from_image_from_bytes(image_bytes, prompt, product)