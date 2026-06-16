from pathlib import Path
import json

def load_config():
    with open('config.json', 'r') as file:
        config = json.load(file)

        return config

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
            user_path = "C:/Users/User/Downloads/test"
            # user_path = input("Enter path to desired folder (or type 'quit' to exit): ").strip()

            if not user_path:
                print("Please enter a correct path before continuing.")
                continue

            if user_path.lower() in {"q", "quit", "exit"}:
                print("\nGoodbye.")
                return
            
            # convert user path string into Path
            user_path = Path(user_path)

            config = load_config()

            manage_subfolders(user_path, config)

            plan = build_plan(user_path, config)

            print_plan(plan)
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
            print("An unexptected error occured.", str(exc))

        
if __name__ == "__main__":
    main()