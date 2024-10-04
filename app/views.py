import os
import cv2
import numpy as np
import shutil
import zipfile
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
from multiprocessing import Pool, cpu_count

# Utility functions
def save_map(obj, dst: str):
    try:
        img = Image.fromarray(obj)
        img.save(dst)
    except Exception as e:
        print(f"Error saving map: {e}")

def delete_existing_maps(current_image_name: str):
    generated_maps_dir = settings.MEDIA_ROOT
    for filename in os.listdir(generated_maps_dir):
        file_path = os.path.join(generated_maps_dir, filename)
        if filename != current_image_name and os.path.isfile(file_path):
            os.remove(file_path)

# Texture Map Classes
class NormalMap:
    def __init__(self, image_path: str, strength: int, invert_height: bool):
        self.strength: int = strength
        self.invert_height = invert_height
        self.blur_radius = 5
        self.normal_map = self.compute_normal_map(image_path)

    def compute_normal_for_pixel(self, data: list) -> tuple:
        normal_scaling_factor = 0.1

        x, y, grad_x, grad_y = data
        grad_x = grad_x[y, x] / 255.0
        grad_y = grad_y[y, x] / 255.0

        # Calculate normal vector
        nx = -grad_x * self.strength * normal_scaling_factor if self.invert_height else grad_x * self.strength * normal_scaling_factor
        ny = -grad_y * self.strength * normal_scaling_factor if self.invert_height else grad_y * self.strength * normal_scaling_factor
        nz = np.sqrt(1.0 - min(1.0, nx**2 + ny**2))
        normal = np.array([nx, ny, nz])
        normal /= np.linalg.norm(normal)

        return (y, x, (int(255 * (0.5 + 0.5 * normal[0])),
                       int(255 * (0.5 + 0.5 * normal[1])),
                       int(255 * (0.5 + 0.5 * normal[2]))))

    def compute_normal_map(self, image_path: str) -> np.ndarray:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError("Image not found or unable to load.")

        blurred_image = cv2.GaussianBlur(image, (self.blur_radius, self.blur_radius), 0)
        grad_x = cv2.Sobel(blurred_image, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(blurred_image, cv2.CV_64F, 0, 1, ksize=3)

        normal_map = np.zeros((image.shape[0], image.shape[1], 3), dtype=np.uint8)
        data = [(x, y, grad_x, grad_y) for y in range(image.shape[0]) for x in range(image.shape[1])]

        with Pool(cpu_count()) as pool:
            results = pool.map(self.compute_normal_for_pixel, data)

        for result in results:
            y, x, normal_pixel = result
            normal_map[y, x] = normal_pixel

        return normal_map


class RoughnessMap:
    def __init__(self, image_path: str, strength: int):
        self.strength: int = strength

        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Image not found or unable to load: {image_path}")

        self.roughness_map = self.generate(image)

    def generate(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Normalize the texture to the range [0, 1]
        texture_normalized = gray_image / 255.0

        # Apply specular strength
        roughness_map = (texture_normalized ** 1) * 255.0

        # Adjust brightness
        brightness_factor = int(self.strength) ** .5  # You can adjust this value to control the brightness
        brightened_roughness_map = np.clip(
            roughness_map * brightness_factor, 0, 255).astype(np.uint8)
        return brightened_roughness_map


# class MetalnessMap:
#     def __init__(self, image_path: str, strength: int):
#         self.strength = strength
#         self.metalness_map = self.compute_metalness_map(image_path)

#     def compute_metalness_map(self, image_path: str) -> np.ndarray:
#         image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#         if image is None:
#             raise ValueError("Image not found or unable to load.")

#         # Create a metalness map initialized to black (0)
#         metalness_map = np.zeros_like(image, dtype=np.uint8)

#         # Areas to be considered metallic (white)
#         metalness_map[image <= int(self.strength)] = 255  # Set areas to white if below or equal to strength
#         return metalness_map  # Return the generated metalness map


class MetalnessMap:
    def __init__(self, image_path: str, strength: int):
        self.strength: int = strength
        self.metalness_map = self.compute_metalness_map(image_path)

    def compute_metalness_map(self, image_path: str) -> np.ndarray:
        # Load the image in grayscale
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError("Image not found or unable to load.")

        # Apply thresholding to create a binary mask for metalness
        _, metalness_map = cv2.threshold(image, int(self.strength), 255, cv2.THRESH_BINARY)

        # Invert the metalness map to make metal areas black (0) and non-metal areas white (255)
        inverted_metalness_map = cv2.bitwise_not(metalness_map)

        return inverted_metalness_map


class DisplacementMap:
    def __init__(self, image_path: str, strength: int):
        self.strength = strength
        self.displacement_map = self.compute_displacement_map(image_path)

    def compute_displacement_map(self, image_path: str) -> np.ndarray:
        normal_scaling_factor = 0.5

        # Load the image in grayscale
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError("Image not found or unable to load.")

        # Normalize the image values to range [0, 1]
        normalized_image = image / 255.0

        # Apply the displacement strength to scale the height values
        displacement_map = normalized_image * self.strength * normal_scaling_factor

        # Convert back to 8-bit format for output (range [0, 255])
        displacement_map = (displacement_map * 255).astype(np.uint8)

        return displacement_map


class MapGenerator:
    def __init__(self, image_path: str, strength: int, map_type: str, invert_height: bool=False):
        self.image_path = image_path

        self.normal_strength = strength if map_type == 'normal' else 1
        self.roughness_strength = strength if map_type == 'roughness' else 1
        self.metalness_strength = strength if map_type == 'metalness' else 1
        self.displacement_strength = strength if map_type == 'displacement' else 1

        self.map_type = map_type
        self.map = self.generate_map(invert_height)

    def generate_map(self, invert_height: bool):
        """Generate the requested map based on the map type."""
        if self.map_type == 'normal':
            return NormalMap(self.image_path, strength=self.normal_strength, invert_height=invert_height).normal_map
        elif self.map_type == 'roughness':
            return RoughnessMap(self.image_path, strength=self.roughness_strength).roughness_map
        elif self.map_type == 'metalness':
            return MetalnessMap(self.image_path, strength=self.metalness_strength).metalness_map
        elif self.map_type == 'displacement':
            return DisplacementMap(self.image_path, strength=self.displacement_strength).displacement_map
        else:
            raise ValueError("Invalid map type. Choose from 'normal', 'roughness', or 'metalness'.")

# Views
@csrf_exempt
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_maps(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        # Normal map
        normal_strength = int(request.POST.get('normal_strength', 1))
        normal_invert_height = request.POST.get('normal_invert_height') == 'true'

        # Roughness map
        roughness_strength = int(request.POST.get('roughness_strength', 5))

        # Metalness map
        metalness_strength = int(request.POST.get('metalness_strength', 40))

        # Displacement map
        displacement_strength = int(request.POST.get('displacement_strength', 0))

        only_filename = os.path.splitext(image_file.name)[0]
        path_extension = os.path.splitext(image_file.name)[1]
        save_path = os.path.join(settings.MEDIA_ROOT, image_file.name)

        with open(save_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        delete_existing_maps(image_file.name)

        # Generate Normal, Roughness, and Metalness maps
        normal_map_generator = MapGenerator(
            image_path=save_path, strength=normal_strength, map_type='normal', invert_height=normal_invert_height)
        roughness_map_generator = MapGenerator(
            image_path=save_path, strength=roughness_strength, map_type='roughness')
        metalness_map_generator = MapGenerator(
            image_path=save_path, strength=metalness_strength, map_type='metalness')
        displacement_map_generator = MapGenerator(
            image_path=save_path, strength=displacement_strength, map_type='displacement')

        normal_map = normal_map_generator.map
        roughness_map = roughness_map_generator.map
        metalness_map = metalness_map_generator.map
        displacement_map = displacement_map_generator.map

        # Color
        color_map_filename = f'{only_filename}{path_extension}'

        # Save the Normal map
        normal_map_filename = f'{only_filename}_Normal{path_extension}'
        normal_map_path = os.path.join(settings.MEDIA_ROOT, normal_map_filename)
        save_map(obj=normal_map, dst=normal_map_path)

        # Save the Roughness map
        roughness_map_filename = f'{only_filename}_Roughness{path_extension}'
        roughness_map_path = os.path.join(settings.MEDIA_ROOT, roughness_map_filename)
        save_map(obj=roughness_map, dst=roughness_map_path)

        # Save the Metalness map
        metalness_map_filename = f'{only_filename}_Metalness{path_extension}'  # New line for metalness filename
        metalness_map_path = os.path.join(settings.MEDIA_ROOT, metalness_map_filename)  # New line for metalness path
        save_map(obj=metalness_map, dst=metalness_map_path)  # New line to save metalness map

        # Save the Displacement map
        displacement_map_filename = f'{only_filename}_Displacement{path_extension}'  # New line for displacement filename
        displacement_map_path = os.path.join(settings.MEDIA_ROOT, displacement_map_filename)  # New line for displacement path
        save_map(obj=displacement_map, dst=displacement_map_path)  # New line to save displacement map

        # Return URLs for all maps
        color_map_url = f'/media/{color_map_filename}'
        normal_map_url = f'/media/{normal_map_filename}'
        roughness_map_url = f'/media/{roughness_map_filename}'
        metalness_map_url = f'/media/{metalness_map_filename}'
        displacement_map_url = f'/media/{displacement_map_filename}'

        print('color_map_url:', color_map_url)

        return JsonResponse({
            'color_map_url': color_map_url,
            'normal_map_url': normal_map_url,
            'roughness_map_url': roughness_map_url,
            'metalness_map_url': metalness_map_url,
            'displacement_map_url': displacement_map_url
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def export_textures(request):
    if request.method == 'POST':
        generated_maps_dir = settings.MEDIA_ROOT

        # List of texture files in the directory
        texture_files = [f for f in os.listdir(generated_maps_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

        zip_filename = os.path.join(generated_maps_dir, 'textures.zip')

        with zipfile.ZipFile(zip_filename, 'w') as zip_file:
            for texture_file in texture_files:
                # Split the file into name and extension
                name, extension = os.path.splitext(texture_file)

                # Check if the current file is the original image
                if all(identifier not in name for identifier in ['_Metalness', '_Roughness', '_Normal', '_Displacement']):
                    # Create new name for the original image
                    new_texture_file = f"{name}_Color{extension}"
                    zip_file.write(os.path.join(generated_maps_dir, texture_file), arcname=new_texture_file)
                else:
                    # Add other textures as they are
                    zip_file.write(os.path.join(generated_maps_dir, texture_file), arcname=texture_file)

        # Return the zip file as a response
        with open(zip_filename, 'rb') as zip_file:
            response = HttpResponse(zip_file.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(zip_filename)}'

        # Delete the zip file after sending it
        os.remove(zip_filename)

        return response

    return JsonResponse({'error': 'Invalid request'}, status=400)
