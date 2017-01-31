import argparse
from flask import Flask, request, render_template
# from jinja2 import Environment, FileSystemLoader, select_autoescape


parser = argparse.ArgumentParser(description='Run a webapp.')
parser.add_argument('--port', type=int, help='The tcp/ip port to use.')
args = parser.parse_args()
print(args.port)

# views = Environment(
#   loader=FileSystemLoader('views'),
#   autoescape=select_autoescape(['html', 'xml'])
# )

app = Flask(__name__, template_folder="views")


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
def test():
  text = request.form.get('text', '')
  # print(text)
  text = ''.join(rot13(text))

  return render_template('index.html', text=text)

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=args.port or 8000)
