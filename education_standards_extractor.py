#!/usr/bin/python
from bs4 import BeautifulSoup, NavigableString
import requests
import sys
reload(sys)
sys.setdefaultencoding('utf8')

invalid_tags = ['b', 'i', 'u', 'em']
concepts = []

def strip_tags(soup, invalid_tags):
    for tag in soup.findAll(True):
        if tag.name in invalid_tags:
            s = ""
            for c in tag.contents:
                if not isinstance(c, NavigableString):
                    c = strip_tags(unicode(c), invalid_tags)
                s += unicode(c)

            tag.replaceWith(s)
    return soup

core = "http://www.corestandards.org/"
main_portal = BeautifulSoup(requests.get(core + 'read-the-standards/').text, 'lxml')
#print portal.prettify()
ela_url = main_portal.find('a',text='English Language Arts Standards').get('href')
math_url = main_portal.find('a',text='Mathematics Standards').get('href')
ela_portal = BeautifulSoup(requests.get(ela_url).text, 'lxml')
superclass = None

for menu in ela_portal.find('div',id='sidebar').findAll('ul', {'class': 'menu'} ) :
    for link in menu.find_all('a') :
        if 'pdf' in link.get('href') : continue
        headers_portal = BeautifulSoup(requests.get(link.get('href')).text, 'lxml')
        for header in headers_portal.findAll('span', {'class':'identifier'}):
            index = header.get_text().rfind('.')
            if superclass == None :
                superclass = header.get_text()[0:index]
                if not superclass in concepts :
                    print ":" + superclass + " rdf:type owl:Class ;"
                    print "    rdfs:label \"" + link.get_text() + "\"^^xsd:string ;"
                    print "    prov:wasQuotedFrom <" + link.get('href') + "> .\n"
                    concepts.append(superclass)
            if not header.get_text() in concepts :
                print ":" + header.get_text() + " rdf:type owl:Class ;"
                print "    rdfs:subClassOf :" + superclass + " ;"
                ref_link = str(link.get('href')) + header.get_text()[index+1:] + "/"
                print "    prov:wasQuotedFrom <" + ref_link + "> ;"
                ref_label = BeautifulSoup(requests.get(ref_link).text, 'lxml').find('h1').get_text()
                ref_comment = BeautifulSoup(requests.get(ref_link).text, 'lxml').find('section', {'class':'content clearfix'}).find('p').get_text().replace('"','\'')
                print "    rdfs:label \"" + "".join([x if ord(x) < 128 else "-" for x in ref_label ]) + "\"^^xsd:string ;"
                print "    rdfs:comment \"" + "".join([x if ord(x) < 128 else "-" for x in ref_comment ]) + "\"^^xsd:string .\n"
                concepts.append(header.get_text())
            superclass = None

for submenu in ela_portal.find('div',id='sidebar').findAll('ul', {'class': 'sub-menu'} ) :
    for link in submenu.find_all('a') :
        #print "Link: ", link.get_text(), ' : ', link.get('href'), '\n' 
        standards_portal = BeautifulSoup(requests.get(link.get('href')).text, 'lxml')
        for standard in strip_tags(standards_portal,invalid_tags).findAll('div', {'class':['standard','substandard']}) :
            class_ref = standard.find_next('a').get_text()
            index = class_ref.rfind('.')
            superclass = class_ref[0:index]
            if not superclass in concepts :
                print ":" + superclass + " rdf:type owl:Class ;"
                print "    rdfs:label \"" + superclass + "\"^^xsd:string ;"
                print "    prov:wasQuotedFrom <" + link.get('href') + "> .\n"
                concepts.append(superclass)
            if not class_ref in concepts :
                print ":" + class_ref + " rdf:type owl:Class ;"
                print "    prov:wasQuotedFrom <" + standard.find_next('a').get('href') + "> ;"
                print "    rdfs:subClassOf :" + superclass + " ;"
                for attribute in standard.findAll('a') :
                    attribute.decompose()
                print "    rdfs:comment \"" + standard.get_text().replace('"','\'') + "\"^^xsd:string .\n"
                concepts.append(class_ref)
            superclass = None

math_portal = BeautifulSoup(requests.get(math_url).text, 'lxml')
for menu in math_portal.find('div',id='sidebar').findAll('ul', {'class': 'menu'} ) :
    for item in menu.find_all('li', {'class' : 'menu-item'}) : #-has-children
        link = item.findNext("a")
        if 'pdf' in link : continue
        headers_portal = BeautifulSoup(requests.get(link.get('href')).text, 'lxml')
        for header in headers_portal.findAll('a', {'class':'identifier'}):
            index = header.get_text().rfind('.')
            superclass = header.get_text()[0:index]
            if not superclass in concepts :
                print ":" + superclass + " rdf:type owl:Class ;"
                print "    rdfs:label \"" + link.get_text() + "\"^^xsd:string ;"
                print "    prov:wasQuotedFrom <" + link.get('href') + "> .\n"
                concepts.append(superclass)
            if not header.get_text() in concepts :
                ref_link = str(link.get('href')) + header.get_text()[index+1:] + "/"
                ref_portal = BeautifulSoup(requests.get(ref_link).text, 'lxml')
                ref_label = ref_portal.find('h1').get_text()
                if ref_portal.find('section', {'class':'content clearfix'}) is not None : 
                    ref_comment = ref_portal.find('section', {'class':'content clearfix'}).find('p').get_text().replace('"','\'')
                else :
                    ref_comment = ""
                print ":" + header.get_text() + " rdf:type owl:Class ;"
                print "    rdfs:subClassOf :" + superclass + " ;"
                print "    prov:wasQuotedFrom <" + ref_link + "> ;"
                print "    rdfs:label \"" + "".join([x if ord(x) < 128 else "-" for x in ref_label ]) + "\"^^xsd:string ;"
                print "    rdfs:comment \"" + "".join([x if ord(x) < 128 else "-" for x in ref_comment ]) + "\"^^xsd:string .\n"
                concepts.append(header.get_text())
