---
layout: snippets
title: Components
description: Here are some snippets on how to make Mophidian components
---

# Components

Components are reusable parts of code, usually elements that you are recreating repeatedly.

A components can be as simple as this:

```html
<div 
    id="header"
    class="flex justify-between"
>
    <a class="no-underline" href="/">Home</a>
    <nav class="flex gap-2">
        <a href="/blog">Blog</a>
        <a href="/snippets">Code Snippets</a>
    </nav>
</div>
```