from pathlib import Path
import argparse
import sys
import json
import shutil
import os
import stat

DEFAULT_CONFIG = {
    "Images": [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".avif",
        ".gif",
        ".tif",
        ".tiff",
        ".raw",
        ".cr2",
        ".nef",
        ".svg",
        ".eps"
    ],
    "Documents": [
        ".docx",
        ".doc",
        ".pdf",
        ".txt",
        ".rtf",
        ".odt",
        ".xlsx",
        ".xls",
        ".ods",
        ".csv",
        ".pptx",
        ".ppt",
        ".odp",
        ".indd",
        ".pub",
        ".html",
        ".htm",
        ".json"
    ],
    "Videos": [
        ".mp4",
        ".mov",
        ".mkv",
        ".webm",
        ".avi"
    ],
    "Archives": [
        ".zip",
        ".zipx",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".gzip",
        ".tar.gz",
        ".tgz"
    ]
}

def manage_default_config():
    # filepath is at root of this python script
    filepath = Path(__file__).resolve().parent / "config.json"

    # if config doesn't exist, create default
    if not filepath.exists():
        print(f"Config not found. Creating a default one at: {filepath}")
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(json.dumps(DEFAULT_CONFIG, indent=4), encoding="utf-8")
        return DEFAULT_CONFIG

    # if config exists
    try:
        content = filepath.read_text(encoding="utf-8")
        if not content.strip():
            raise json.JSONDecodeError("Config file is empty", content, 0)
        
        config_data = json.loads(content)

        # verify config_data is a dictionary structure
        if not isinstance(config_data, dict):
            raise ValueError("Config root is not a JSON object (dictionary)")
        
        return config_data
    
    except (json.JSONDecodeError, ValueError) as exc:
        # this only creates the path in memory
        print(f"Config file at {filepath} is malformed. Error: {exc}")
        backup_path = filepath.with_suffix(".json.bak")
        print(f"Backing up corrupted config to: {backup_path}")

        # this actually renames the file to the backup path created
        if filepath.exists():
            filepath.replace(backup_path)

        # generate fresh default config file
        filepath.write_text(json.dumps(DEFAULT_CONFIG, indent=4), encoding="utf-8")
        print("Generated a fresh default configuration file.")

        return DEFAULT_CONFIG

def manage_user_config(config_path):
    # if config doesn't exist, create default
    if not config_path.exists():
        print(f"Specified config not found at '{config_path}'\n"
              f"Please check the file path and try again."
        )
        sys.exit(1)

    # if config exists
    try:
        content = config_path.read_text(encoding="utf-8")
        if not content.strip():
            raise ValueError("Config file is empty.")
        
        config_data = json.loads(content)

        # verify config_data is a dictionary structure
        if not isinstance(config_data, dict):
            raise ValueError("Config root is not a JSON object (dictionary)")
        
        return config_data
    
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"Config file at {config_path} is invalid or malformed.\n"
              f"Details: {exc}\n"
              f"Please fix formatting errors before rerunning."
        )
        sys.exit(1)

def build_plan(user_path, config):
    plan = {}

    ext_to_folder = {}
    for folder_name, extensions in config.items():
        for ext in extensions:
            ext_to_folder[ext.lower()] = folder_name

    # for each item in the directory, is_file() ensures it does not enter subfolders
    for file_path in user_path.iterdir():
        if file_path.is_file():
            # ensure script itself is not included in organization
            if file_path.name == Path(sys.argv[0]).name:
                continue

            # skip system files
            if file_path.name.startswith(".") or file_path.name.lower() == "desktop.ini":
                continue

            ext = "".join(file_path.suffixes).lower()
            target_folder_name = ext_to_folder.get(ext)
            if target_folder_name is None:
                ext = file_path.suffix.lower()
                target_folder_name = ext_to_folder.get(ext, "Other")
            target_folder_path = user_path / target_folder_name

            safe_destination = get_unique_destination(target_folder_path, file_path.name)

            plan[file_path] = safe_destination

    return plan

def get_unique_destination(target_folder, filename):
    destination = target_folder / filename

    # check if file name already exists and rename if it does
    if not destination.exists():
        return destination
    
    stem = destination.stem
    suffix = destination.suffix

    counter = 1

    while True:
        new_filename = f"{stem} ({counter}){suffix}"
        destination = target_folder / new_filename

        if not destination.exists():
            return destination
        
        counter += 1

def print_plan(plan):
    if not plan:
        print("No files found to organize.")
        return
    
    for src_path, dest_path in plan.items():
        # extract original file name
        original_name = src_path.name
        # extract destination folder name
        dest_folder = dest_path.parent.name
        # extract final file name (if file was renamed due to duplicate)
        final_name = dest_path.name

        if original_name == final_name:
            print(f"{original_name} -> {dest_folder}")
        else:
            print(f"{original_name} -> {dest_folder} (Renamed to: {final_name})")

def execute_plan(plan):
    if not plan:
        print("No files found to organize.")
        return
    
    print("\nOrganizing files...")
    success_count = 0
    
    for src_path, dest_path in plan.items():
        try:
            # check/create target folder
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # remove potential read-only flag to ensure all files can be moved
            if src_path.exists():
                os.chmod(src_path, stat.S_IWRITE)

            shutil.move(src_path, dest_path)
            success_count += 1

        except PermissionError:
            print(f"Skipped: '{src_path.name}' File is currently open or locked by another app.")
        except Exception as e:
            print(f"Failed to move '{src_path.name}'. Error: {e}")

    print(f"\nDone. Successfully organized {success_count} of {len(plan)} files.")

def main():
    parser = argparse.ArgumentParser(
        description="Organize files in a folder into category subfolders."
    )

    parser.add_argument(
        "folder",
        type=Path,
        help="Path to the folder you want to organize."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would happen without moving any files."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to a custom JSON config file."
    )

    args = parser.parse_args()
    user_path = args.folder
    dry_run_flag = args.dry_run
    custom_config_path = args.config

    if not user_path.exists():
        print(f"Error: The folder '{user_path}' does not exist.")
        sys.exit(1)

    if not user_path.is_dir():
        print(f"Error: '{user_path}' is not a folder.")
        sys.exit(1)

     # check for and use custom config, else use or create default
    if custom_config_path:
        config = manage_user_config(custom_config_path)
    else:
        config = manage_default_config()

    plan = build_plan(user_path, config)

    # check for dry run
    if dry_run_flag:
        print_plan(plan)
    else:
        execute_plan(plan)

        
if __name__ == "__main__":
    main()