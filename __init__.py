import argparse
from sanic import Sanic
from sanic.response import json, html, text
from jinja2 import Environment, FileSystemLoader, select_autoescape


parser = argparse.ArgumentParser(description='Run a webapp.')
parser.add_argument('--port', type=int, help='The tcp/ip port to use.')
args = parser.parse_args()
print(args.port)

views = Environment(
  loader=FileSystemLoader('views'),
  autoescape=select_autoescape(['html', 'xml'])
)

app = Sanic()


def rot13(text):
    for n, c in ((ord(c), c) for c in text):
      if 65 <= n <= 90:
        n += 13
        yield chr(n) if n <= 90 else chr(n - 26)
      elif 97 <= n <= 122:
        n += 13
        yield chr(n) if n <= 122 else chr(n - 26)
      else:
        yield c

@app.route("/", methods=['GET', 'POST'])
async def test(req):
  tmpl = views.get_template('index.html')
  text = req.form.get('text', '')
  # print(text)
  text = ''.join(rot13(text))

  return html(tmpl.render(text=text))

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=args.port or 8000)
