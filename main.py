import yaml

with open("config.yml", "r") as yamlfile:
    data = yaml.load(yamlfile, Loader=yaml.FullLoader)
    print("Config read successful")


print(data["bot_token"])
