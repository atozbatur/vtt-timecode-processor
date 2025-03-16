# VTT Timecode Processor

A Python utility for processing WebVTT subtitle files and converting SRT files to VTT format.

<img width="596" alt="Screenshot 2025-03-16 at 21 31 08" src="https://github.com/user-attachments/assets/00d8b406-ce2b-4c67-8fe9-19ef16ba9870" />


## Features

- **Zero Hour Values**: Set the hour part of VTT timecodes to '00'
- **SRT to VTT Conversion**: Convert SRT subtitle files to WebVTT format
- **Batch Processing**: Process multiple files at once
- **Multithreading**: Optional parallel processing for faster operation
- **Custom File Naming**:
  - Sequential numbering (1.vtt, 2.vtt, 3.vtt)
  - Custom prefixes (ex1.vtt, ex2.vtt, ex3.vtt)
  - Interactive renaming

## Requirements

- Python 3.6 or higher
- Tkinter (included in standard Python installation)

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/vtt-timecode-processor.git
cd vtt-timecode-processor
```

2. Run the script:
```
python vtt_processor.py
```

No additional dependencies required!

## Usage

### Basic Operation

1. Launch the application
2. Select your operation mode (Process VTT or Convert SRT)
3. Choose input and output directories
4. Configure file naming options
5. Click "Start Processing"
6. Monitor progress on the status bar

### File Naming Options

- **Default**: Original filenames with an index suffix
- **Manual Rename**: Prompts for a new name for each file
- **Sequential Numbering**: Automatically numbers files (with optional prefix)

### Processing Options

- **Multithreading**: Enable/disable parallel processing
- Progress tracking with success/failure reporting

## Use Cases

- **Video Content Creators**: Fix subtitle timing issues
- **Content Distributors**: Convert between subtitle formats
- **Educators**: Prepare subtitles for lecture videos
- **Media Archivists**: Standardize subtitle collections

## Logging

The application logs all operations to:
- Console output
- Log file (`vtt_processor.log`)

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
