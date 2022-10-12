from __future__ import annotations

class WebObject:
    '''Base web object that translate the attributes and tag to a html element
        Arguments:
            - dashed_attrs (tuple[str, str]): This allows for attributes with dashes in their name to be added.
                Ex. ("http-equiv", "X-UA-Compatible")
            - attrs (Any): This allow for attributes to be added.
                Ex. charset="UTF-8"
    '''
    def __init__(self, *dashed_attrs: tuple[str, str], **attrs):
        self.attrs = {}
        
        for key, value in dashed_attrs:
            self.attrs[key] = value
        
        for key, value in attrs.items():
            self.attrs[key] = value
    
    def compileAttrs(self) -> str:
        return [f'{key}="{value}"' for key, value in self.attrs.items()]
        
    def __repr__(self) -> str:
        return f"{self.tag}(attrs:[{','.join(self.compileAttrs())}])"

class Element(WebObject):
    def __init__(self, tag: str ,*dashed_attrs: tuple[str, str], **attrs):
        super().__init__(*dashed_attrs, **attrs)
        self.tag = tag
        self.child_nodes = None
    
    def get_chldren(self, indent: int = 0) -> str:
        output = []
        if self.child_nodes is not None:
            for childNode in self.child_nodes:
                output.append(childNode.html(indent + 2))
        return '\n'.join(output)
    
    def __enter__(self):
        #ttysetattr etc goes here before opening and returning the file object
        self.child_nodes = []
        return self
    
    def __exit__(self, type, value, traceback):
        #Exception handling here
        pass
    
    def html(self, indent: int = 0) -> str:
        if self.child_nodes is not None:
            return f"<{self.tag} {' '.join(self.compileAttrs())} />"
        else:
            return (
f'''{indent*' '}<{self.tag} {' '.join(self.compileAttrs())}>
{self.getChildren(indent) if self.child_nodes is not None else ''}
{indent*' '}</{self.tag}>'''
            )

class Link(Element):
    def __init__(self, href: str, rel: str ,*dashed_attrs: tuple[str, str], **attrs):
        super().__init__(tag="link", *dashed_attrs, **attrs)
        
        self.attrs.update({
            href: href,
            rel: rel,
        })
        
        
class Meta(Element):
    '''HTML <meta /> tag.
    '''
    def __init__(self, *dashed_attrs: tuple[str, str], **attrs):
        super().__init__(*dashed_attrs, **attrs)
        self.tag = "meta"
    
    def suggested() -> list[Meta]:
        return [
            Meta(charset="UTF-8"),
            Meta(("http-equiv", "X-UA-Compatible"), content="IE=edge"),
            Meta(name="viewport", content="width=device-width initial-scale=1.0")
        ]
          
    def __str__(self) -> str:
        return f"<meta {' '.join(self.compileAttrs())} />"
    
class Script(Element):
    pass

class Title(Element):
    pass

class Text(Element):
    def html(indent: int = 0) -> str:
        return f"{indent * ' '}{self.innerText}"
    
class Head(Element):
    def __init__(self, *dashed_attrs: tuple[str, str], **attrs):
        super().__init__(*dashed_attrs, **attrs)
        self.tag = "head"

if __name__ == "__main__":
    print(Meta.suggested()[0])
    with Head() as head:
        head.child_nodes.extend(Meta.suggested())
        head.child_nodes.extend([
            
        ])