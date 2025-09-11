import re
from bs4 import BeautifulSoup, NavigableString, Comment
import html

def clean_newsletter_html(input_html: str) -> str:
    """
    Cleans a Microsoft Word HTML export for newsletter import.
    Returns cleaned HTML as a string.
    """
    soup = BeautifulSoup(input_html, 'html.parser')

    # Remove all CSS definitions
    for style in soup.find_all('style'):
        style.decompose()

    # Remove all HTML comments
    for comments in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comments.extract()

    # Normalize quotes and decode any remaining HTML entities.
    for element in soup.find_all(string=True):
        if isinstance(element, NavigableString):
            cleaned_text = html.unescape(element)
            cleaned_text = cleaned_text.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
            if element != cleaned_text:
                element.replace_with(cleaned_text)

    # Truncate at "Previous SmartDrivingCars" marker
    cutoff_element = soup.find(string=re.compile(r"^\s*Previous SmartDrivingCars", re.IGNORECASE))
    if cutoff_element:
        parent_block = cutoff_element.find_parent(['p', 'div', 'tr'])
        if parent_block:
            for element in list(parent_block.find_next_siblings()):
                element.decompose()
            parent_block.decompose()

    # Consolidate timecode paragraphs into a bulleted list
    timecode_paragraphs = []
    for p in soup.find_all('p'):
        link = p.find('a')
        if link and re.match(r'^\d{1,2}:\d{2}(:\d{2})?$', link.get_text(strip=True)):
            timecode_paragraphs.append(p)

    if timecode_paragraphs:
        ul = soup.new_tag('ul')
        for p in timecode_paragraphs:
            link = p.find('a')
            if link and link.get_text(strip=True):
                link_text = link.get_text(strip=True)
                description = p.get_text(strip=True).replace(link_text, '', 1).strip()
                li = soup.new_tag('li')
                new_a = soup.new_tag('a', href=link.get('href'))
                new_a.string = link_text
                li.append(new_a)
                li.append(NavigableString(f" {description}"))
                ul.append(li)
        if ul.contents:
            timecode_paragraphs[0].replace_with(ul)
            for p in timecode_paragraphs[1:]:
                p.decompose()

    # Remove meta tags
    for tag in soup.find_all('meta'):
        tag.decompose()
    if soup.head:
        soup.head.insert(0, soup.new_tag('meta', charset='UTF-8'))

    # Whitelist tags
    allowed_tags = {'html', 'head', 'title', 'meta', 'body', 'h1', 'h2', 'h3', 'p', 'a', 'br', 'ul', 'li'}
    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            tag.unwrap()
        else:
            allowed_attrs = {'href'} if tag.name == 'a' else set()
            current_attrs = list(tag.attrs)
            for attr in current_attrs:
                if attr not in allowed_attrs:
                    del tag[attr]

    # Remove empty paragraphs
    for p in soup.find_all('p'):
        if not p.get_text(strip=True) and not p.find():
            p.decompose()

    # Remove footer content
    footer_markers = [
        re.compile(r'^\*{5,}$'),
        re.compile(r'^\s*This list is maintained by', re.IGNORECASE),
        re.compile(r'^\s*To unsubscribe from this list', re.IGNORECASE)
    ]
    elements_to_remove = []
    footer_found = False
    if soup.body:
        for element in soup.body.find_all(['p', 'div'], recursive=True):
            if footer_found:
                elements_to_remove.append(element)
                continue
            text_content = element.get_text(strip=True)
            for marker in footer_markers:
                if marker.search(text_content):
                    footer_found = True
                    elements_to_remove.append(element)
                    for sibling in element.find_next_siblings():
                        elements_to_remove.append(sibling)
                    break
    for element in set(elements_to_remove):
        if hasattr(element, 'decompose') and not getattr(element, 'decomposed', False):
            element.decompose()

    return str(soup)
