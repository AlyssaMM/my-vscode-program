import pytesseract
from PIL import Image
import os
import re

def extract_ingredients_from_image(image_path, debug=False):
    """
    Extract text from an image and return the ingredients categorized as active and inactive.
    Preserves asterisks in ingredient names and removes newlines.
    
    Args:
        image_path (str): Path to the image file
        debug (bool): If True, prints debugging information
        
    Returns:
        str: Formatted string with active and inactive ingredients
    """
    try:
        # Open the image
        img = Image.open(image_path)
        
        # Extract text from the image with improved configuration
        text = pytesseract.image_to_string(
            img, 
            config='--psm 6'  # Assume a single uniform block of text
        )
        
        if debug:
            print("=== RAW EXTRACTED TEXT ===")
            print(text)
            print("==========================")
        
        # Process the entire text to find Active and Inactive sections
        active_section = None
        inactive_section = None
        
        # Define more flexible regex patterns for ingredient sections
        active_pattern = r'(?:active|main)\s+ingredients?[\s:;.,]*'
        inactive_pattern = r'(?:inactive|other|excipient)\s+ingredients?[\s:;.,]*'
        
        # Look for Active Ingredients section with more flexible matching
        active_match = re.search(active_pattern, text, re.IGNORECASE)
        if active_match:
            active_start = active_match.end()
            
            # Look for Inactive Ingredients section after Active section
            inactive_match = re.search(inactive_pattern, text[active_start:], re.IGNORECASE)
            if inactive_match:
                # We found both sections
                active_end = active_start + inactive_match.start()
                active_section = text[active_start:active_end].strip()
                inactive_section = text[active_start + inactive_match.end():].strip()
                
                if debug:
                    print(f"Found Active and Inactive sections")
                    print(f"Active section: {active_section}")
                    print(f"Inactive section: {inactive_section}")
            else:
                # Only found Active section - look for end markers
                end_markers = ["uses", "directions", "warnings", "purpose", "keep out of reach"]
                lowest_pos = len(text)
                
                for marker in end_markers:
                    marker_match = re.search(r'\b' + marker + r'\b', text[active_start:], re.IGNORECASE)
                    if marker_match and active_start + marker_match.start() < lowest_pos:
                        lowest_pos = active_start + marker_match.start()
                
                if lowest_pos < len(text):
                    active_section = text[active_start:lowest_pos].strip()
                else:
                    active_section = text[active_start:].strip()
                
                if debug:
                    print(f"Found only Active section: {active_section}")
        else:
            # No Active section found, look for just Inactive section
            inactive_match = re.search(inactive_pattern, text, re.IGNORECASE)
            if inactive_match:
                inactive_start = inactive_match.end()
                
                # Look for end markers
                end_markers = ["uses", "directions", "warnings", "purpose", "keep out of reach"]
                lowest_pos = len(text)
                
                for marker in end_markers:
                    marker_match = re.search(r'\b' + marker + r'\b', text[inactive_start:], re.IGNORECASE)
                    if marker_match and inactive_start + marker_match.start() < lowest_pos:
                        lowest_pos = inactive_start + marker_match.start()
                
                if lowest_pos < len(text):
                    inactive_section = text[inactive_start:lowest_pos].strip()
                else:
                    inactive_section = text[inactive_start:].strip()
                
                if debug:
                    print(f"Found only Inactive section: {inactive_section}")
        
        # If no sections found with regex, try to extract everything
        if not active_section and not inactive_section:
            if debug:
                print("No ingredient sections found with regex, attempting different approach")
            
            # Try to find ingredient lists based on common patterns
            ingredient_lists = re.findall(r'[\w\s\*\(\)\.,-]+(?:,|\.|\band\b)[\w\s\*\(\)\.,-]+', text)
            if ingredient_lists:
                combined_ingredients = " ".join(ingredient_lists)
                # If "active" appears anywhere in text, assume we found at least some active ingredients
                if re.search(r'active', text, re.IGNORECASE):
                    active_section = combined_ingredients
                else:
                    inactive_section = combined_ingredients
        
        # Process active ingredients if found
        active_clean = []
        if active_section:
            # Remove any pipe characters and replace newlines with spaces
            active_section = active_section.replace('|', ',').replace('\n', ' ')
            
            # Split by commas, semicolons, periods, "and", and multiple spaces
            active_raw = re.split(r'[,;.]+|\s+and\s+|\s{2,}', active_section)
            
            for ingredient in active_raw:
                ingredient = ingredient.strip()
                # Filter out empty strings and section headers
                if ingredient and len(ingredient) > 1:
                    # Skip strings that are just numbers or sections with common non-ingredient words
                    if not re.match(r'^[\d\s.%]+$', ingredient) and not any(word in ingredient.lower() for word in ["purpose", "uses", "directions", "warnings"]):
                        # Clean up percentages at the end of ingredients
                        match = re.match(r'(.*?)\s+\d+\.?\d*\s*%', ingredient)
                        if match:
                            ingredient = match.group(1).strip()
                        
                        # Only add if it looks like an ingredient (contains letters)
                        if re.search(r'[a-zA-Z]', ingredient):
                            active_clean.append(ingredient)
        
        # Process inactive ingredients if found
        inactive_clean = []
        if inactive_section:
            # Remove any pipe characters and replace newlines with spaces
            inactive_section = inactive_section.replace('|', ',').replace('\n', ' ')
            
            # Split by commas, semicolons, periods, "and", and multiple spaces
            inactive_raw = re.split(r'[,;.]+|\s+and\s+|\s{2,}', inactive_section)
            
            for ingredient in inactive_raw:
                ingredient = ingredient.strip()
                # Filter out empty strings and section headers
                if ingredient and len(ingredient) > 1:
                    # Skip strings that are just numbers or sections with common non-ingredient words
                    if not re.match(r'^[\d\s.%]+$', ingredient) and not any(word in ingredient.lower() for word in ["purpose", "uses", "directions", "warnings"]):
                        # Clean up percentages at the end of ingredients
                        match = re.match(r'(.*?)\s+\d+\.?\d*\s*%', ingredient)
                        if match:
                            ingredient = match.group(1).strip()
                        
                        # Only add if it looks like an ingredient (contains letters)
                        if re.search(r'[a-zA-Z]', ingredient):
                            inactive_clean.append(ingredient)
        
        # Format the output
        output = ""
        if active_clean:
            output += "Active Ingredients: " + ", ".join(active_clean) + "."
        
        if inactive_clean:
            if output:  # Add a space if active ingredients exist
                output += "\nInactive Ingredients: " + ", ".join(inactive_clean) + "."
            else:
                output += "Inactive Ingredients: " + ", ".join(inactive_clean) + "."
        
        # If no ingredients were found, provide feedback
        if not output:
            return "No ingredients were detected in the image. Try adjusting the image quality or clarity."
        
        return output
    
    except Exception as e:
        return f"Error processing image: {str(e)}"

def main():
    # Get image path from user
    image_path = input("Enter the path to your image: ")
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return
    
    # Ask about debug mode
    debug_option = input("Enable debug mode to see extraction details? (y/n): ")
    debug_mode = debug_option.lower() == 'y'
    
    # For Windows users who need to specify Tesseract path
    # Uncomment and modify the next line if needed
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    # Process the image and get formatted ingredients
    print("\nProcessing image. Please wait...")
    formatted_ingredients = extract_ingredients_from_image(image_path, debug=debug_mode)
    
    # Print the formatted output
    print("\nExtracted Ingredients:")
    print(formatted_ingredients)
    
    # Option to save to file
    save_option = input("\nDo you want to save the ingredients to a text file? (y/n): ")
    if save_option.lower() == 'y':
        output_path = input("Enter output file path (or press Enter for default 'ingredients.txt'): ")
        if not output_path:
            output_path = "ingredients.txt"
        
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(formatted_ingredients)
        print(f"Ingredients saved to {output_path}")

if __name__ == "__main__":
    # Check if pytesseract is properly configured
    try:
        pytesseract.get_tesseract_version()
        print(f"Tesseract version: {pytesseract.get_tesseract_version()}")
    except:
        print("Error: Tesseract OCR is not installed or not in PATH.")
        print("Please install Tesseract OCR and ensure it's in your system PATH.")
        print("On Windows, you may need to set the path with:")
        print("pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
        exit(1)
    
    main()