# Organizer CLI

`organizer.py` is a small interactive Python script that sorts loose files in a folder into category subfolders such as `Images`, `Documents`, `Videos`, and `Archives`.

## Features

- Creates category folders automatically from a JSON config.
- Moves files based on their extension.
- Skips the script itself and common system files like `desktop.ini`.
- Supports a dry-run mode so you can preview the plan before moving files.
- Supports a custom config file with your own categories and extensions.

## Requirements

- Python 3.10 or newer
- The packages listed in [requirements.txt](requirements.txt)

## Usage

Run the script from a terminal:

```bash
python organizer.py
```

When prompted, enter the path to the folder you want to organize.

Examples:

```bash
C:\Users\YourName\Downloads
C:\Users\YourName\Downloads --dry-run
C:\Users\YourName\Downloads --config C:\path\to\config.json
```

## Flags

- `--dry-run` shows the planned moves before anything is changed.
- `--config <path>` loads a custom JSON config instead of the default `config.json` in the script folder.

## Config File

The config file should be a JSON object where each key is a folder name and each value is a list of file extensions.

Example:

```json
{
    "Images": [".png", ".jpg"],
    "Documents": [".pdf", ".txt"],
    "Archives": [".zip", ".tar.gz"]
}
```

Any files not matching a folder in the config will be placed in an "Optional" folder.

If `config.json` does not exist, the script creates a default one automatically.

## Notes

- Files with duplicate names are renamed with a number suffix, such as `file (1).txt`.
- If a path does not exist or is not a folder, the script will stop and show an error.
- `.tar.gz` archives are detected correctly.

## Authors

Jonathan Kinney - [@Mewzok](https://github.com)

## Version History

* 1.0
    * Initial release

## License

This project is licensed under the [MIT License](LICENSE).