# Topic 4. Homework

## Description

Write a Python script that reads all files in a user-specified source folder and distributes them into subfolders in the output folder based on their file extensions. The script should perform the sorting asynchronously for more efficient handling of a large number of files.

## Technical Task Description

1. Import the necessary asynchronous libraries.
2. Create an **ArgumentParser** object to handle command-line arguments.
3. Add the required arguments to specify the source and output folders.
4. Initialize asynchronous paths for the source and output folders.
5. Write an asynchronous function **read_folder** that recursively reads all files in the source folder and its subfolders.
6. Write an asynchronous function **copy_file** that copies each file into a corresponding subfolder in the output folder based on its extension.
7. Set up error logging.
8. Run the asynchronous **read_folder function** in the main block.
