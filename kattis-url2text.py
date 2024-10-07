#! /usr/bin/env python3

from bs4 import BeautifulSoup
from requests import get
import argparse
import pydetex.pipelines as pip

# argparse setup
parser = argparse.ArgumentParser(description='Convert a problem page to plaintext')
parser.add_argument('url', type=str, help='URL of the problem page')
parser.add_argument('-linewidth', '-l', type=int, help='Desired line width, set to 0 for no limit', default=80)

def limit_linewidth(text, width=80):
    out_lines = []
    words = []
    words_text = []
    current_word = []
    for word in text.split():
        if "(" in word:
            current_word.append(word)
            if ")" in word:
                words_text.append(" ".join(current_word))
                current_word = []
        elif current_word:
            current_word.append(word)
            if ")" in word:
                words_text.append(" ".join(current_word))
                current_word = []
        else:
            words_text.append(word)
    cur_width = 0
    for word in words_text:
        if cur_width + len(word) > width + 1:
            out_lines.append(" ".join(words))
            words = []
            cur_width = 0
        words.append(word)
        cur_width += len(word) + 1
    out_lines.append(" ".join(words))
    return "\n".join(out_lines)

# Substitue things that don't work well for pip.strict_eqn
LATEX_SUBSTITUTE = {
    r'\operatorname' : '',
    r'\sin ' : 'sin',
    r'\cos ' : 'cos',
    r'\sin' : 'sin',
    r'\cos' : 'cos',
}
def convert_tex(soup):
    for span in soup.find_all('span', {'class': 'tex2jax_process'}):
        tex_text = span.get_text()
        # Replace $ symbols and apply the LaTeX to Unicode substitutions
        for k, v in LATEX_SUBSTITUTE.items():
            tex_text = tex_text.replace(k, v)
        cleaned_text = pip.strict_eqn(tex_text)
        span.replace_with(cleaned_text)


def convert_to_plaintext(html, linewidth=80):
    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Remove unwanted 'illustration' and 'description' divs (like images)
    for div in soup.find_all('div', {'class': 'illustration'}):
        div.decompose()

    convert_tex(soup)

    # Collect text ensuring proper paragraph and section breaks
    output_lines = []

    # Extract and add the main heading to the output
    heading = soup.select_one('.book-page-heading')
    if heading:
        output_lines.append("# " + heading.get_text().strip())


    # Get the main problem body container
    problem_body = soup.select_one('.problembody')

    # If there's text directly inside the problem body, add it first
    if problem_body and problem_body.string:
        output_lines.append(problem_body.string.strip())

    non_tagged = []
    # Iterate through child elements of the problem body
    for element in problem_body.children if problem_body else []:
        # Handle direct text nodes not wrapped in tags
        if element.name is None and element.strip():
            raw_text = ' '.join(element.replace("\n", " ").split())
            non_tagged.append(raw_text)
            continue
        elif non_tagged:
            output_lines.append(f'\n{limit_linewidth(' '.join(non_tagged).replace(' ,', ','), linewidth)}\n')
            non_tagged = []

        # Handle paragraphs and headings properly
        if element.name in ['p', 'h2', 'h3']:
            element_text = ' '.join(element.get_text().replace("\n", " ").split())
            if linewidth > 0:
                element_text = limit_linewidth(element_text, linewidth)

            if element.name == 'h2':
                output_lines.append(f"\n## {element_text}")
            elif element.name == 'h3':
                output_lines.append(f"\n### {element_text}")
            else:
                output_lines.append(f"\n{element_text}\n")

        # Handle preformatted text (for sample inputs/outputs)
        elif element.name == 'pre':
            output_lines.append(f"\n{element.get_text().strip()}\n")
        elif element.name == 'ul':
            output_lines.append("\n")
            for li in element.children:
                if li.name != 'li':
                    continue
                element_text = ' '.join(li.get_text().replace("\n", " ").split())
                element_text = limit_linewidth(element_text, linewidth - 3)
                element_text = "\n".join("   " + text for text in element_text.splitlines())
                output_lines.append(" - " + element_text.lstrip() + "\n")
        elif element.name == 'ol':
            output_lines.append("\n")
            n = 1
            for li in element.children:
                if li.name != 'li':
                    continue
                element_text = ' '.join(li.get_text().replace("\n", " ").split())
                element_text = limit_linewidth(element_text, linewidth - 4)
                element_text = "\n".join("    " + text for text in element_text.splitlines())
                output_lines.append(f" {n}. " + element_text.lstrip() + "\n")
                n += 1


    # Join the lines with appropriate paragraph spacing (double newlines between sections)
    cleaned_text = "".join(output_lines)
    # Return the final cleaned-up text
    return cleaned_text


if __name__ == "__main__":
    args = parser.parse_args()
    address = args.url
    response = get(address)
    html = response.text
    try:
        print(convert_to_plaintext(html, args.linewidth))
    except Exception as e:
        print(f"Error: {e}")
        print("Could not convert the page to plaintext.")
        print("Please check the URL and try again.")
        exit(1)
