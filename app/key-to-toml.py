import toml
import os

cert_file = "amro-partners-firebase-adminsdk-syddx-7de4edb3c4.json" # certification file for firebase authentication
output_file = "amro-partners-firebase-adminsdk-syddx-7de4edb3c4.toml"

with open(os.path.join(os.path.realpath('./'), cert_file)) as json_file:
    json_text = json_file.read()

config = {"textkey": json_text}
toml_config = toml.dumps(config)

with open((os.path.join(os.path.realpath('./'), output_file)), "w") as target:
    target.write(toml_config)
