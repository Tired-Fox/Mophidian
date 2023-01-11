Order:
1. config
2. file management
3. integration
4. component linking
5. layouts
6. flask

## Config
- Custom class decorators
  - define attributes with typing and values to specify variables in config with certain type and default value
  - Nested list and dictionary values
    - Dicts have keys equal to valid variables
    - tuples have valid types and valid value
    - each index of list is a tuple of valid type and values
  - Valid types class with list of possible types

## File Management
- read components
- read files in directory
- build paths and urls
- link components to pages

**Reference Svelte**
- layouts per directory
  - `~` == root layout/default
  - `~lyt-name` == Certain layout based on it's name
  - `<slot />` element to specify location of content
  - Inherit from parent unless `~` is used on layout
  - `@lyt-name` to specify the layout name.
- Grouping directory `(dir_name)`
  - layouts in this dir inherit the layout name == to the dir_name

