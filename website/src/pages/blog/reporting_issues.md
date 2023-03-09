# Reporting Issues

This project is in constant development by a single developer. There are also four total first party repositories
being used. So if there are issues found by users it would be a huge help if they were reported in github issues.

## First party repositories

This project uses three other first party repositories to handle things like: typed configuration objects,
colored ansi terminal output, and a live reloading server. 

### TCFG

To handle typed configuration objects Mophidian utilizes a python library called [tcfg](https://github.com/Tired-Fox/tcfg/)
, which stands for typed configuration. It supports `yaml`, `json`, and `toml` out of the box and is customizable.
The point of using this is to load a configuration and automatically fill in defaults. It will also automatically
give detailed exceptions when a configuration type is an invalid type. There is an added bonus of being able to access
config values as attributes on an object. If the configuration gets large or requires multiple files and/or multiple
configuration types the library allows this without any additional setup. I encourage python developers to check out
the library if they are interested.

To report an issue or error involving tcfg please create a github issue to the [tcfg repo](https://github.com/Tired-Fox/tcfg/issues)
