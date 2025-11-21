import yaml
import re
from schema import Schema, Optional, SchemaError, And, Or

non_empty_list_of_strings = And([str], lambda l: len(l) > 0, error='This list cannot be empty')

valid_image_name = And(str, lambda s: not re.search(r'\s', s), error='Image name cannot contain whitespace')

CONFIG_SCHEMA = Schema({
    "image": valid_image_name,
    Optional("variables"): {str: Or(int, str)},
    Optional("before_script"): [str],
    "scripts": non_empty_list_of_strings,
    Optional("after_script"): [str],
    Optional("artifacts"): {
        "paths": non_empty_list_of_strings
    }
})


def validate_config_from_file(file_path: str):
    try:
        with open(file_path, 'r') as f:
            configuration = yaml.safe_load(f)

        if configuration is None:
            return False, "Configuration file is empty or invalid."

        CONFIG_SCHEMA.validate(configuration)
        
        print(f"Configuration file {file_path} is valid.")
        return True, configuration

    except FileNotFoundError:
        return False, f"Configuration file '{file_path}' not found."
    except yaml.YAMLError as e:
        return False, f"YAML syntax error: {e}"
    except SchemaError as e:
        return False, f"Configuration error: {e}"