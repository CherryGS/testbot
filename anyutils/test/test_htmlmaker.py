from anyutils import htmlmaker as ts
from lxml import etree
from hypothesis.stateful import RuleBasedStateMachine, rule
from random import randint

node_list = ["a", "span", "img", "div", "br"]


def k():
    return node_list[randint(0, len(node_list))]


def geneHtml(deep, body: ts.DOMTree):
    if deep <= 0:
        return
    while randint(1, 100) < randint(1, 100):
        r = ts.DOMTree(k())
        geneHtml(deep - 1, r)
        body.add(r).add("br")
    for i in range(randint(1, 3)):
        body.add_props("test" + str(i), {str(i)})


class TestHtmlMaker:
    def test_1(self):
        r = ts.DOMTree("html").add("body")
        geneHtml(20, r)
        html = etree.HTML(r.output(), etree.HTMLParser(recover=False))
