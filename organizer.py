from pathlib import Path
import shlex
import argparse
import sys
import json

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
        ".htm"
    ],
    "Videos": [
        ".mp4",
        ".mov",
        ".mkv",
        ".webm",
        ".avo"
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
    ],
    "Other": [
        ".*"
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
    
def parse_interactive_input(user_input: str):
    try:
        tokens = shlex.split(user_input)
    except ValueError as e:
        print(f"Malformed quotes in your input: {e}")
        return None
    
    parser = argparse.ArgumentParser(exit_on_error=False)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--config", type=str, default=None)

    try:
        args, remaining_tokens = parser.parse_known_args(tokens)
    except argparse.ArgumentError as e:
        if "--config" in str(e):
            print("Error: The --config flag requires a path to a valid JSON config file.")
            print("Example: C:/Downloads --config C:/path/to/config.json")
        else:
            print(f"Invalid flags entered: {e}")
        return None
    
    if not remaining_tokens:
        print("Error: Please provide a valid target folder path along with your flags.")
        return None
    
    folder_str = " ".join(remaining_tokens)

    return {
        "folder_path": Path(folder_str),
        "dry_run": args.dry_run,
        "config_path": Path(args.config) if args.config else None
    }

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

def manage_subfolders(user_path, config):

    for folder_name, extensions in config.items():
        folder_path = user_path / folder_name
        folder_path.mkdir(exist_ok=True)

def build_plan(user_path, config):
    plan = {}

    ext_to_folder = {}
    for folder_name, extensions in config.items():
        for ext in extensions:
            ext_to_folder[ext.lower()] = folder_name

    # for each item in the directory, is_file() ensures it does not enter subfolders
    for file_path in user_path.iterdir():
        if file_path.is_file():
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

def main():
    # handle retrieving user path
    while True:
        try:
            # testing
            # user_path = "C:/Users/User/Downloads/test"
            user_input = input("Enter path to desired folder (or type 'quit' to exit): ").strip()

            if not user_input:
                print("Please enter a correct path before continuing.")
                continue

            if user_input.lower() in {"q", "quit", "exit"}:
                print("\nGoodbye.")
                break

            # parse input to check for arguments
            parsed = parse_interactive_input(user_input)
            if not parsed:
                continue

            # split into useful variables
            user_path = parsed["folder_path"]
            dry_run_flag = parsed["dry_run"]
            custom_config_path = parsed["config_path"]

            # check for and use custom config, else use or create default
            if custom_config_path:
                config = manage_user_config(custom_config_path)
            else:
                config = manage_default_config()

            manage_subfolders(user_path, config)
            plan = build_plan(user_path, config)

            # check for dry run
            if dry_run_flag:
                print_plan(plan)
                confirm = input("Confirm? (Y/N): ").strip().lower()
                if confirm in {"y", "yes"}:
                    print("Plan executed")
                else:
                    print("Organization cancelled.")
            else:
                print("Plan executed")

            break
            
        except ValueError as exc:
            print(str(exc))
        except RuntimeError as exc:
            print(str(exc))
        except KeyboardInterrupt:
            print("Folder lookup interrupted. Exiting gracefully.")
            return
        except EOFError:
            print("Input stream ended unexpectedly. Please run the command again.")
            return
        except Exception as exc:
            print("An unexpected error occured.", str(exc))

        
if __name__ == "__main__":
    main()