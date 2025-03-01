import os
import subprocess
import argparse
import tempfile
import shutil
import zipfile
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Define full paths to executables
DDJVU_PATH = r"C:\Program Files (x86)\DjVuLibre\ddjvu.exe"
DJVUSED_PATH = r"C:\Program Files (x86)\DjVuLibre\djvused.exe"  # Add path to djvused.exe

def get_page_count(input_file):
    """Get the number of pages in a DJVU file."""
    try:
        # Try using djvused to get page count
        cmd = [DJVUSED_PATH, input_file, "-e", "n"]
        process = subprocess.run(cmd, capture_output=True, text=True)
        if process.returncode == 0 and process.stdout.strip().isdigit():
            return int(process.stdout.strip())
    except Exception as e:
        print(f"Error getting page count with djvused: {str(e)}")
    
    try:
        # Alternative method: use ddjvu to dump info and count pages
        cmd = [DDJVU_PATH, "-l", input_file]
        process = subprocess.run(cmd, capture_output=True, text=True)
        if process.returncode == 0:
            # Count lines that start with "Page"
            pages = [line for line in process.stdout.split('\n') if line.strip().startswith('Page ')]
            if pages:
                return len(pages)
    except Exception as e:
        print(f"Error getting page count with ddjvu -l: {str(e)}")
    
    # If all else fails, return a default value
    print("Could not determine page count, using default value")
    return 100  # Reasonable default

def extract_page(ddjvu_path, input_file, output_file, page, quality=85):
    """Extract a single page from a DJVU file."""
    try:
        # Try direct extraction to PNG
        cmd = [
            ddjvu_path,
            "-page=" + str(page),
            "-format=png",
            "-mode=color",
            "-quality=" + str(quality),
            "-skip",  # Skip errors
            input_file,
            output_file
        ]
        
        process = subprocess.run(cmd, capture_output=True, text=True)
        if process.returncode == 0 and os.path.exists(output_file):
            return True
        
        # If direct extraction failed, try alternative method
        cmd = [
            ddjvu_path,
            "-page=" + str(page),
            "-format=tiff",  # Try TIFF format
            "-mode=color",
            "-quality=" + str(quality),
            "-skip",
            input_file,
            output_file.replace(".png", ".tiff")
        ]
        
        process = subprocess.run(cmd, capture_output=True, text=True)
        if process.returncode == 0 and os.path.exists(output_file.replace(".png", ".tiff")):
            # Convert TIFF to PNG
            tiff_file = output_file.replace(".png", ".tiff")
            from PIL import Image
            Image.open(tiff_file).save(output_file)
            os.remove(tiff_file)  # Clean up TIFF file
            return True
        
        return False
    except Exception as e:
        print(f"Error extracting page {page}: {str(e)}")
        return False

def convert_djvu_to_cbz(input_file, output_file, quality=85):
    """
    Convert a DJVU file to CBZ format.
    
    Args:
        input_file: Path to the DJVU file
        output_file: Path to save the CBZ file
        quality: Image quality (1-100), higher means better quality but larger file
    """
    print(f"Converting: {input_file} to {output_file}")
    
    # Create a temporary directory to store the extracted images
    temp_dir = tempfile.mkdtemp()
    print(f"Created temporary directory: {temp_dir}")
    
    try:
        # Get the number of pages in the DJVU file
        num_pages = get_page_count(input_file)
        print(f"Document has {num_pages} pages")
        
        # Extract each page as a separate image
        successful_pages = 0
        for page in range(1, num_pages + 1):
            # Create output filename with leading zeros for proper sorting
            page_filename = os.path.join(temp_dir, f"page_{page:04d}.png")
            
            print(f"Extracting page {page}/{num_pages}...")
            if extract_page(DDJVU_PATH, input_file, page_filename, page, quality):
                successful_pages += 1
            else:
                print(f"Warning: Failed to extract page {page}")
        
        if successful_pages == 0:
            print(f"Error: Could not extract any pages from {input_file}")
            return False
        
        # Create the CBZ file (which is just a ZIP file with images)
        print(f"Creating CBZ file: {output_file}")
        with zipfile.ZipFile(output_file, 'w') as zipf:
            # Get all the PNG files in the temp directory
            png_files = [f for f in os.listdir(temp_dir) if f.endswith('.png')]
            png_files.sort()  # Sort to ensure correct page order
            
            # Add each image to the ZIP file
            for png_file in png_files:
                png_path = os.path.join(temp_dir, png_file)
                zipf.write(png_path, png_file)
        
        print(f"Successfully converted {input_file} to CBZ format with {len(png_files)} pages")
        return True
        
    except Exception as e:
        print(f"Error converting {input_file}: {str(e)}")
        return False
    finally:
        # Clean up the temporary directory
        print(f"Cleaning up temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir)

def process_folder(input_folder, output_folder=None, quality=85, max_workers=4):
    """
    Process all DJVU files in a folder and convert them to CBZ.
    
    Args:
        input_folder: Folder containing DJVU files
        output_folder: Folder to save CBZ files (defaults to input_folder if None)
        quality: Image quality (1-100)
        max_workers: Maximum number of parallel conversions
    """
    print(f"Starting process with the following parameters:")
    print(f"Input folder: {input_folder}")
    print(f"Output folder: {output_folder}")
    print(f"Quality: {quality}")
    print(f"Max workers: {max_workers}")
    
    # Check if input folder exists
    if not os.path.exists(input_folder):
        print(f"Input folder '{input_folder}' does not exist.")
        return
    
    if output_folder is None:
        output_folder = input_folder
    
    # Check if output folder exists, create if not
    if not os.path.exists(output_folder):
        print(f"Creating output folder: {output_folder}")
        os.makedirs(output_folder)
    
    # Find all DJVU files
    djvu_files = []
    print(f"Searching for DJVU files in: {input_folder}")
    
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('.djvu', '.djv')):
                print(f"Found DJVU file: {file}")
                input_path = os.path.join(root, file)
                # Create relative path for output
                rel_path = os.path.relpath(root, input_folder)
                output_subdir = os.path.join(output_folder, rel_path)
                
                if not os.path.exists(output_subdir):
                    os.makedirs(output_subdir)
                
                output_path = os.path.join(output_subdir, os.path.splitext(file)[0] + '.cbz')
                djvu_files.append((input_path, output_path))
    
    if not djvu_files:
        print("No DJVU files found in the input folder.")
        return
    
    print(f"Found {len(djvu_files)} DJVU files to convert.")
    
    # Check if executables exist
    if not os.path.exists(DDJVU_PATH):
        print(f"Error: ddjvu executable not found at {DDJVU_PATH}")
        return
    
    # Install required Python packages if needed
    try:
        from PIL import Image
    except ImportError:
        print("Installing required Python package: Pillow")
        subprocess.run(["pip", "install", "Pillow"], check=True)
    
    # Convert files in parallel or sequentially
    if max_workers > 1:
        print(f"Starting parallel conversion with {max_workers} workers")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create a list of futures
            futures = [executor.submit(convert_djvu_to_cbz, input_file, output_file, quality) 
                      for input_file, output_file in djvu_files]
            
            # Process with progress bar
            successful = 0
            for future in tqdm(futures, total=len(futures), desc="Converting"):
                if future.result():
                    successful += 1
    else:
        # Sequential processing
        print("Starting sequential conversion")
        successful = 0
        for input_file, output_file in tqdm(djvu_files, desc="Converting"):
            if convert_djvu_to_cbz(input_file, output_file, quality):
                successful += 1
    
    print(f"Conversion completed. Successfully converted {successful} out of {len(djvu_files)} files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert DJVU files to CBZ for Komga")
    parser.add_argument("input_folder", help="Folder containing DJVU files")
    parser.add_argument("-o", "--output_folder", help="Folder to save CBZ files (defaults to input folder)")
    parser.add_argument("-q", "--quality", type=int, default=85, 
                        help="Image quality (1-100, higher is better quality but larger file size)")
    parser.add_argument("-w", "--workers", type=int, default=1, 
                        help="Maximum number of parallel conversions (default: 1)")
    
    args = parser.parse_args()
    
    # Print arguments for debugging
    print(f"Arguments received:")
    print(f"input_folder: {args.input_folder}")
    print(f"output_folder: {args.output_folder}")
    print(f"quality: {args.quality}")
    print(f"workers: {args.workers}")
    
    process_folder(args.input_folder, args.output_folder, args.quality, args.workers)
