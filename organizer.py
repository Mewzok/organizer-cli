from pathlib import Path

SUBFOLDERS = ["Images", "Documents", "Videos", "Archives", "Other"]

def scan_folder(user_path):
    # for each item in the directory, does not enter subfolders
    for item in user_path.iterdir():
        if item.is_file():
            print(item.name)

    return

def manage_subfolders(user_path):

    for subfolder in SUBFOLDERS:
        new_folder_path = user_path / subfolder
        new_folder_path.mkdir(exist_ok=True)

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
            
            scan_folder(user_path)
            manage_subfolders(user_path)
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