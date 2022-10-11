Inspired from remark and rehype:
Will support options and plugins similar to both remark and rehype.

[HighlightJS Styles](https://unpkg.com/browse/@highlightjs/cdn-assets@11.6.0/styles/)

## Basic Markdown

https://www.markdownguide.org/basic-syntax/

## Custom Parsing:
* start with basic tokens
* Paragraph tokens and separating them.
* Then loop over paragraph searching for next level of tokens creating new tokens
* repeat for basic things and for plugins
* combine tokens into new tokens

Tokens:
**Staring:**
* Paragraph
* ! => negate
* sbracket => Group
  + Grouping of text
* paranthesis => link attribute
  + url
  + `""` surround the target
* curlybracket - attribute
  + `name` => boolean (true)
  + `name="value"` => string value
  + `name=value => Attempt to do best evaluation to bool or number before converting to string

*Composite tokens:*
+ `[]{}` => attribute on paragraph
+ `[]()` => link
+ `[](){}` => link with attributes
+ `![]()` => Image
+ `![](){}` => Image with attributes

### ***All tokens must return their string value***

Rules will be held in a dict to allow for rule overrides
