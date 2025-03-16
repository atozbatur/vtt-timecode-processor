import os
import re
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from typing import List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor
import threading

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("vtt_processor.log")
    ]
)
logger = logging.getLogger(__name__)

# Precompile regex patterns for efficiency
VTT_TIMECODE_PATTERN = re.compile(
    r"(\d{2}):(\d{2}):(\d{2}\.\d{3}) --> (\d{2}):(\d{2}):(\d{2}\.\d{3})"
)
SRT_TIMECODE_PATTERN = re.compile(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})")

class FileProcessor:
    """Handles all file processing operations for VTT and SRT files."""
    
    @staticmethod
    def adjust_timecode_vtt(line: str) -> str:
        """
        Adjusts a VTT timecode line by setting the hour part to '00'.
        
        Args:
            line: A string potentially containing a VTT timecode
            
        Returns:
            The adjusted line with zeroed hour values
        """
        match = VTT_TIMECODE_PATTERN.search(line)
        if match:
            mm1, ss1, mm2, ss2 = match.group(2), match.group(3), match.group(5), match.group(6)
            new_timecode = f"00:{mm1}:{ss1} --> 00:{mm2}:{ss2}"
            return VTT_TIMECODE_PATTERN.sub(new_timecode, line)
        return line

    @staticmethod
    def convert_srt_to_vtt(input_path: str, output_path: str) -> bool:
        """
        Converts an SRT file to a VTT file by modifying timecodes and adding the VTT header.
        
        Args:
            input_path: Path to the SRT file
            output_path: Path where the VTT file will be saved
            
        Returns:
            True if conversion was successful, False otherwise
        """
        try:
            with open(input_path, "r", encoding="utf-8") as srt_file, \
                 open(output_path, "w", encoding="utf-8") as vtt_file:
                # Write the VTT header
                vtt_file.write("WEBVTT\n\n")
                for line in srt_file:
                    # Replace comma in timecode with period
                    line = SRT_TIMECODE_PATTERN.sub(lambda m: f"{m.group(1)}:{m.group(2)}:{m.group(3)}.{m.group(4)}", line)
                    vtt_file.write(line)
            logger.info(f"Converted {input_path} to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error converting {input_path}: {e}")
            return False
            
    @staticmethod
    def process_vtt_file(input_path: str, output_path: str) -> bool:
        """
        Processes a VTT file by zeroing the hour values in all timecodes.
        
        Args:
            input_path: Path to the input VTT file
            output_path: Path where the processed VTT file will be saved
            
        Returns:
            True if processing was successful, False otherwise
        """
        try:
            with open(input_path, "r", encoding="utf-8") as infile, \
                 open(output_path, "w", encoding="utf-8") as outfile:
                for line in infile:
                    outfile.write(FileProcessor.adjust_timecode_vtt(line))
            logger.info(f"Processed {input_path} -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error processing {input_path}: {e}")
            return False


class VTTTimecodeZeroerApp(tk.Tk):
    """Main application for processing VTT files and converting SRT to VTT."""
    
    def __init__(self):
        super().__init__()
        self.title("VTT Timecode Processor")
        self.geometry("600x400")
        self.minsize(500, 350)
        
        # Instance variables
        self.processor = FileProcessor()
        self.processing_thread = None
        self.is_processing = False
        
        # Create GUI elements
        self.create_widgets()
        self.apply_theme()
        
        # Set up protocol for window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def apply_theme(self):
        """Apply custom styling to the application."""
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", font=("Helvetica", 10))
        style.configure("TLabel", font=("Helvetica", 10))
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"))
        style.configure("TRadiobutton", font=("Helvetica", 10))
        style.configure("TProgressbar", thickness=8)
        
    def create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main frame with safe margins using padding
        self.main_frame = ttk.Frame(self, padding=(20, 20))
        self.main_frame.grid(row=0, column=0, sticky="NSEW")
        
        # Make the main frame expand with the window
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Setup grid columns in main_frame to scale proportionally
        self.main_frame.columnconfigure(1, weight=3)
        self.main_frame.columnconfigure(2, weight=1)

        # Title label centered at the top
        title_label = ttk.Label(self.main_frame, text="VTT Timecode Processor", style="Header.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="N")

        # Option selection using Radiobuttons
        ttk.Label(self.main_frame, text="Select operation:").grid(row=1, column=0, sticky="W", padx=5, pady=5)
        self.choice = tk.StringVar(value="vtt")
        ttk.Radiobutton(self.main_frame, text="Process VTT Files (Zero Hour Values)", variable=self.choice, value="vtt")\
            .grid(row=1, column=1, sticky="W", padx=5, pady=5)
        ttk.Radiobutton(self.main_frame, text="Convert SRT to VTT", variable=self.choice, value="srt")\
            .grid(row=1, column=2, sticky="W", padx=5, pady=5)

        # Input directory selection
        ttk.Label(self.main_frame, text="Input Directory:").grid(row=2, column=0, sticky="W", padx=5, pady=5)
        self.input_dir_var = tk.StringVar()
        ttk.Entry(self.main_frame, textvariable=self.input_dir_var).grid(row=2, column=1, sticky="EW", padx=5, pady=5)
        ttk.Button(self.main_frame, text="Browse...", command=self.select_input_directory)\
            .grid(row=2, column=2, padx=5, pady=5)

        # Output directory selection
        ttk.Label(self.main_frame, text="Output Directory:").grid(row=3, column=0, sticky="W", padx=5, pady=5)
        self.output_dir_var = tk.StringVar()
        ttk.Entry(self.main_frame, textvariable=self.output_dir_var).grid(row=3, column=1, sticky="EW", padx=5, pady=5)
        ttk.Button(self.main_frame, text="Browse...", command=self.select_output_directory)\
            .grid(row=3, column=2, padx=5, pady=5)

        # File handling options
        ttk.Label(self.main_frame, text="File Handling:").grid(row=4, column=0, sticky="W", padx=5, pady=5)
        
        # File naming frame for better organization
        file_frame = ttk.Frame(self.main_frame)
        file_frame.grid(row=4, column=1, columnspan=2, sticky="W", padx=5, pady=5)
        
        # File naming options
        self.rename_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(file_frame, text="Rename files during processing", variable=self.rename_var)\
            .grid(row=0, column=0, sticky="W")
            
        # Sequential numbering option
        self.sequential_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(file_frame, text="Use sequential numbering", variable=self.sequential_var)\
            .grid(row=1, column=0, sticky="W")
            
        # Prefix for sequential numbering
        ttk.Label(file_frame, text="Prefix (optional):").grid(row=1, column=1, sticky="W", padx=(20, 5))
        self.prefix_var = tk.StringVar(value="")
        ttk.Entry(file_frame, textvariable=self.prefix_var, width=10)\
            .grid(row=1, column=2, sticky="W", padx=5)
        
        # Batch processing options
        ttk.Label(self.main_frame, text="Multithreading:").grid(row=5, column=0, sticky="W", padx=5, pady=5)
        self.use_threads_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.main_frame, text="Use multithreading for faster processing", variable=self.use_threads_var)\
            .grid(row=5, column=1, sticky="W", padx=5, pady=5)

        # Start processing button
        self.start_button = ttk.Button(self.main_frame, text="Start Processing", command=self.start_processing)
        self.start_button.grid(row=6, column=0, columnspan=3, pady=(20, 10))

        # Progress information
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.grid(row=7, column=0, columnspan=3, sticky="EW", pady=10)
        self.progress_frame.columnconfigure(0, weight=1)
        
        self.progress_label = ttk.Label(self.progress_frame, text="Ready")
        self.progress_label.grid(row=0, column=0, sticky="W", padx=5, pady=(0, 5))
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky="EW", padx=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.grid(row=8, column=0, columnspan=3, sticky="W", pady=(10, 0))

    def select_input_directory(self):
        """Opens a file dialog to select the input directory."""
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            self.input_dir_var.set(directory)

    def select_output_directory(self):
        """Opens a file dialog to select the output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)

    def rename_file(self, output_directory: str, file_name: str, index: int) -> str:
        """
        Handles file naming based on selected options:
        1. Default naming: original_name_index.vtt
        2. User prompt: asks for a new name for each file
        3. Sequential numbering: prefix1.vtt, prefix2.vtt, etc.
        
        Args:
            output_directory: Directory where the file will be saved
            file_name: Original file name (without extension)
            index: Index of the file in the batch process
            
        Returns:
            Full path for the new file
        """
        # Sequential numbering takes precedence if enabled
        if self.sequential_var.get():
            prefix = self.prefix_var.get().strip()
            if prefix:
                new_name = f"{prefix}{index}"
            else:
                new_name = f"{index}"
            return os.path.join(output_directory, f"{new_name}.vtt")
            
        # If rename option is checked, prompt user for name
        elif self.rename_var.get():
            new_name = simpledialog.askstring(
                "Rename", 
                f"Enter new name for {file_name} (leave blank to keep original name):"
            )
            
            if new_name is None or new_name.strip() == "":
                new_name = file_name
            else:
                new_name = f"{new_name.strip()}_{index}"
                
            return os.path.join(output_directory, f"{new_name}.vtt")
            
        # Default naming scheme
        else:
            return os.path.join(output_directory, f"{file_name}_{index}.vtt")

    def start_processing(self):
        """Validates inputs and starts the processing thread."""
        if self.is_processing:
            messagebox.showinfo("Processing", "Already processing files. Please wait.")
            return
            
        input_dir = self.input_dir_var.get()
        output_dir = self.output_dir_var.get()
        
        if not input_dir or not output_dir:
            messagebox.showerror("Error", "Please select both input and output directories.")
            return
            
        if not os.path.exists(input_dir) or not os.path.isdir(input_dir):
            messagebox.showerror("Error", "Invalid input directory.")
            return
            
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create output directory: {e}")
                return
                
        self.is_processing = True
        self.start_button.config(state="disabled")
        self.status_var.set("Processing...")
        
        # Start processing in a separate thread to keep UI responsive
        self.processing_thread = threading.Thread(
            target=self.process_files_thread,
            args=(self.choice.get(), input_dir, output_dir)
        )
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def process_files_thread(self, choice: str, input_dir: str, output_dir: str):
        """
        Processes files in a separate thread to keep the UI responsive.
        
        Args:
            choice: Type of processing to perform ('vtt' or 'srt')
            input_dir: Input directory path
            output_dir: Output directory path
        """
        try:
            self.process_files(choice, input_dir, output_dir)
        except Exception as e:
            logger.error(f"Error during processing: {e}")
            self.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))
        finally:
            self.after(0, self.processing_complete)

    def processing_complete(self):
        """Resets the UI state after processing is complete."""
        self.is_processing = False
        self.start_button.config(state="normal")
        self.status_var.set("Ready")

    def process_files(self, choice: str, input_dir: str, output_dir: str):
        """
        Processes files based on the selected option: either adjusts VTT timecodes or converts SRT to VTT.
        
        Args:
            choice: Type of processing to perform ('vtt' or 'srt')
            input_dir: Input directory path
            output_dir: Output directory path
        """
        # Get list of files to process
        if choice == "vtt":
            files = [f for f in os.listdir(input_dir) if f.lower().endswith(".vtt")]
        else:  # choice == "srt"
            files = [f for f in os.listdir(input_dir) if f.lower().endswith(".srt")]

        total_files = len(files)
        if total_files == 0:
            self.after(0, lambda: messagebox.showinfo("Notice", "No matching files found in the input directory."))
            return

        # Update the UI with the total number of files
        self.after(0, lambda: self.progress_bar.config(maximum=total_files))
        self.after(0, lambda: self.progress_label.config(text=f"Processing {total_files} files..."))
        
        # Process files (with or without multithreading)
        processed_count = 0
        failed_count = 0
        
        if self.use_threads_var.get() and total_files > 1:
            # Use multithreading for faster processing
            with ThreadPoolExecutor(max_workers=min(os.cpu_count() or 2, 4)) as executor:
                futures = []
                
                # Submit all tasks to the executor
                for index, file_name in enumerate(files, start=1):
                    input_path = os.path.join(input_dir, file_name)
                    
                    if choice == "vtt":
                        # Clean up file name for VTT files
                        base_name = file_name.replace(".mp4.vtt", "").replace(".vtt", "")
                        output_path = self.rename_file(output_dir, base_name, index)
                        futures.append(
                            executor.submit(FileProcessor.process_vtt_file, input_path, output_path)
                        )
                    else:  # choice == "srt"
                        base_name = file_name.replace(".srt", "")
                        output_path = self.rename_file(output_dir, base_name, index)
                        futures.append(
                            executor.submit(FileProcessor.convert_srt_to_vtt, input_path, output_path)
                        )
                
                # Process results as they complete
                for i, future in enumerate(futures):
                    if future.result():
                        processed_count += 1
                    else:
                        failed_count += 1
                    
                    # Update progress bar
                    progress = (i + 1) / total_files * 100
                    self.after(0, lambda p=progress: self.progress_var.set(p))
                    self.after(0, lambda c=processed_count, f=failed_count: 
                              self.status_var.set(f"Processed: {c}, Failed: {f}"))
        else:
            # Process files sequentially
            for index, file_name in enumerate(files, start=1):
                input_path = os.path.join(input_dir, file_name)
                
                if choice == "vtt":
                    # Clean up file name for VTT files
                    base_name = file_name.replace(".mp4.vtt", "").replace(".vtt", "")
                    output_path = self.rename_file(output_dir, base_name, index)
                    result = FileProcessor.process_vtt_file(input_path, output_path)
                else:  # choice == "srt"
                    base_name = file_name.replace(".srt", "")
                    output_path = self.rename_file(output_dir, base_name, index)
                    result = FileProcessor.convert_srt_to_vtt(input_path, output_path)
                
                if result:
                    processed_count += 1
                else:
                    failed_count += 1
                
                # Update progress bar
                progress = index / total_files * 100
                self.after(0, lambda p=progress: self.progress_var.set(p))
                self.after(0, lambda c=processed_count, f=failed_count: 
                          self.status_var.set(f"Processed: {c}, Failed: {f}"))
        
        # Show completion message
        completion_message = f"Processing complete.\nSuccessfully processed: {processed_count}\nFailed: {failed_count}"
        self.after(0, lambda: messagebox.showinfo("Process Complete", completion_message))
        
    def on_closing(self):
        """Handles the window close event, ensuring clean shutdown even during processing."""
        if self.is_processing:
            if messagebox.askyesno("Exit", "Processing is in progress. Are you sure you want to exit?"):
                # If processing thread exists, we can't directly terminate it
                # But we can mark our flag so the UI updates properly on exit
                self.is_processing = False
                self.destroy()
        else:
            self.destroy()


if __name__ == "__main__":
    try:
        app = VTTTimecodeZeroerApp()
        app.mainloop()
    except Exception as e:
        # If application fails to start or encounters critical error
        logging.critical(f"Critical application error: {e}")
        messagebox.showerror("Critical Error", f"The application encountered a critical error: {e}")

def main():
    """Entry point for command-line execution via setup.py"""
    try:
        app = VTTTimecodeZeroerApp()
        app.mainloop()
    except Exception as e:
        logging.critical(f"Critical application error: {e}")
        print(f"Critical error: {e}")
        return 1
    return 0

