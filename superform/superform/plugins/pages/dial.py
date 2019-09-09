import urllib.error
import urllib.parse
import urllib.request
import re
from ast import literal_eval

from flask import Blueprint, render_template, request, flash
from superform.posts import new_post

dial_page = Blueprint('dial', __name__)


def escape_special_characters(string):
    special_characters = ["\\", " ", "+", "-", "&&", "||", "!", "(", ")", "{", "}", "[", "]", "^", '"', "~", "*", "?",
                          ":", "/"]
    for car in special_characters:
        string = string.replace(car, "\\" + car)
    return string


@dial_page.route('/dial_search', methods=['GET', 'POST'])
def dial_search():
    if request.method == 'GET':
        return render_template("dial.html")
    else:
        action = request.form.get('@action', '')
        if action == "search":
            title = escape_special_characters(request.form.get('title'))
            creator = ""
            if request.form.get('author_name') and request.form.get('author_firstname'):
                creator = request.form.get('author_name').capitalize() + ",\\ " + request.form.get(
                    'author_firstname').capitalize()
            elif request.form.get('author_name'):
                creator = request.form.get('author_name').capitalize() + "*"
            elif request.form.get('author_firstname'):
                creator = request.form.get('author_firstname').capitalize() + "*"
            # if request.form.get('author_name'):
            #     creator += request.form.get('author_name').capitalize() + "*"
            # if request.form.get('author_firstname'):
            #     creator += request.form.get('author_firstname').capitalize() + "*"
            year = request.form.get('year')
            document_type = request.form.get('document_type')
            language = request.form.get('language')

            if title == "" and creator == "" and year == "" and document_type == "" and language == "":
                flash("Search need at least one parameter.", category='info')
                return render_template("dial.html")

            base_query = 'https://dial.uclouvain.be/solr6/repository/select?&start=0&rows=500&qt=standard&wt=python'
            arguments = ""
            need_and = False

            if title is not "":
                if need_and:
                    arguments += " AND "
                arguments += "sm_title:" + title + "~5"
                need_and = True
            if creator is not "":
                if need_and:
                    arguments += " AND "
                arguments += "sm_creator:" + creator + "~3"
                need_and = True
            if year is not "":
                if need_and:
                    arguments += " AND "
                arguments += "sm_date:\"" + year + "\""
            if document_type is not "":
                if need_and:
                    arguments += " AND "
                arguments += "sm_contentmodel:\"" + document_type + "\""
            if language is not "":
                if need_and:
                    arguments += " AND "
                arguments += "sm_isolang:\"" + language + "\""

            url = '%s&sort=&q=%s' % (base_query, urllib.parse.quote(arguments))

            try:
                returned_page = urllib.request.urlopen(url)
            except urllib.error.URLError:
                flash("Error while connecting to Dial.", category='error')
                message = "Found no matching result."
                return render_template("dial.html", search_result=[], message_result=message)

            string_dict = returned_page.read().decode(returned_page.headers._charset or "utf-8", 'surrogateescape')
            python_dict = literal_eval(string_dict)
            search_result = []
            message = ""
            if 'response' not in python_dict or 'docs' not in python_dict['response']:
                message = "Got an incorrect answer"
            else:
                message = "Found " + str(python_dict['response']['numFound']) + " matching result(s)."
                search_result = sorted(python_dict['response']['docs'], key=lambda k: k.get('sm_date', ["-"]),
                                       reverse=True)

            return render_template("dial.html", search_result=search_result[:300], message_result=message)
        elif action == "import":
            title = request.form.get('title')
            description = request.form.get('description')
            link = request.form.get('link')
            return new_post([title, description, link])
