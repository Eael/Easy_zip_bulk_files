import os
import shutil
import datetime
import zipfile


def display_loader(current, total, message="Progress"):
    """Display a progress loader with hash marks."""
    progress = int((current / total) * 50)  # Scale to 50 hash marks
    loader = f"[{'#' * progress}{'.' * (50 - progress)}] {current}/{total} {message}"
    print(f"\r{loader}", end="")  # Overwrite the current line


def create_zip_with_loader(source_dir, output_zip):
    """Create a zip archive with a loader to show progress."""
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        total_items = sum(len(files) for _, _, files in os.walk(source_dir))
        current_item = 0
        for foldername, subfolders, filenames in os.walk(source_dir):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
                current_item += 1
                display_loader(current_item, total_items, "Zipping")
    print("\nZip creation complete.")


try:
    # Step 1: Get user inputs
    print("Welcome to the Backup Program!")
    destinationdir = input("Enter the source directory (where files and folders are located): ").replace("\\", "/")
    backup_base_dir = input("Enter the backup base directory (where backups should be saved): ").replace("\\", "/")

    # Check if directories exist
    if not os.path.exists(destinationdir):
        raise FileNotFoundError(f"Source directory not found: {destinationdir}")
    if not os.path.exists(backup_base_dir):
        raise FileNotFoundError(f"Backup base directory not found: {backup_base_dir}")

    # Step 2: Generate unique backup folder name
    current_month = datetime.datetime.now().strftime('%B')
    new_location = f'{backup_base_dir}/{current_month}'
    i = 1
    while os.path.exists(new_location):
        new_location = f'{backup_base_dir}/{current_month}_{i}'
        i += 1

    zip_file_name = f"{new_location}.zip"
    i = 1
    while os.path.exists(zip_file_name):
        zip_file_name = f"{new_location}_{i}.zip"
        i += 1

    # Confirm backup location with user
    print(f"Backup will be saved in: {new_location}")
    print(f"Zip file will be saved as: {zip_file_name}")
    # input("Press Enter to continue or Ctrl+C to cancel...")

    # Step 3: Create the backup directory
    os.makedirs(new_location)
    print(f"Backup directory created: {new_location}")

    # Step 4: Scan everything in the source directory
    print("Scanning source directory for files and folders...")
    items = os.listdir(destinationdir)

    if not items:
        raise ValueError("No files or folders found in the source directory to back up.")

    print(f"Found {len(items)} item(s) to back up.")
    # input("Press Enter to start copying or Ctrl+C to cancel...")

    # Step 5: Copy items with a loader
    total_items = len(items)
    for idx, item in enumerate(items, start=1):
        item_path = os.path.join(destinationdir, item)
        try:
            if os.path.isfile(item_path):
                shutil.copy2(item_path, os.path.join(new_location, item))
            elif os.path.isdir(item_path):
                shutil.copytree(item_path, os.path.join(new_location, item))
            else:
                print(f"\nSkipping unknown item type: {item}")
        except Exception as e:
            print(f"\nError copying {item}: {e}")

        # Update the loader
        display_loader(idx, total_items, "Backing up")

    print("\nAll items copied successfully!")

    # Step 6: Create a zip archive with loader
    print("Creating a zip archive of the backup...")
    create_zip_with_loader(new_location, zip_file_name)

    # Step 7: Remove the temporary backup directory
    try:
        print("Removing temporary backup directory...")
        shutil.rmtree(new_location)
        print("Temporary directory removed successfully.")
    except Exception as e:
        print(f"Error removing temporary backup directory: {e}")

    input("Backup process completed successfully!")

except KeyboardInterrupt:
    print("\nOperation interrupted by the user.")
    confirm_quit = input("Do you really want to quit? (y/n): ").lower()
    if confirm_quit != 'y':
        print("Resuming operation...")
    else:
        print("Exiting program. Goodbye!")

except Exception as e:
    print(f"An error occurred: {e}")
