from pathlib import Path
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

def manage_default_config() -> dict:
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

def manage_subfolders(user_path, config):

    for folder_name, extensions in config.items():
        folder_path = user_path / folder_name
        folder_path.mkdir(exist_ok=True)

def build_plan(user_path, config):
    plan = []

    # for each item in the directory, does not enter subfolders
    for item in user_path.iterdir():
        if item.is_file():
            destination = find_destination(item, config)
            plan.append((item, destination))

    return plan

def find_destination(item, config):
    # create a reverse lookup dictionary to search for extensions as keys
    ext_to_folder = {}
    for folder, extensions in config.items():
        for ext in extensions:
            ext_to_folder[ext.lower()] = folder

    return ext_to_folder.get(item.suffix, "Other")

def print_plan(plan):
    for source, destination in plan:
        print(f"{source.name} -> {destination}")

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
                return
            
            # check for --config, ALSO, create default config

            # check for dry run            
            dry_run = False
            if "--dry-run" in user_input:
                dry_run = True
                user_input = user_input.replace("--dry-run", "").strip()

            print(user_input)

            if not user_input:
                print("Error: Please provide a valid path alongside the --dry-run flag.")
                continue
            
            # convert user path string into Path
            user_path = Path(user_input)
            config = manage_default_config()
            manage_subfolders(user_path, config)
            plan = build_plan(user_path, config)

            if dry_run:
                print_plan(plan)
                confirm_response = input("Confirm? (Y/N): ").strip().lower()

                if confirm_response in {"y", "yes"}:
                    # testing
                    # execute_plan()
                    print("Plan executed")
                else:
                    print("Organization cancelled.")
            else:
                # testing
                # execute plan()
                print("Plan executed")
            
            return
            
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