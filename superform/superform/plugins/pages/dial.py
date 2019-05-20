import urllib.error
import urllib.parse
import urllib.request
from ast import literal_eval

from flask import Blueprint, render_template, request
from superform.posts import new_post

dial_page = Blueprint('dial', __name__)


@dial_page.route('/dial_search', methods=['GET', 'POST'])
def dial_search():
    if request.method == 'GET':
        return render_template("dial.html")
    else:
        action = request.form.get('@action', '')
        if action == "search":
            title = request.form.get('title')
            creator = request.form.get('author')
            year = request.form.get('year')
            document_type = request.form.get('document_type')
            language = request.form.get('language')
            # number_entries = request.form.get('number_entries')
            base_query = 'https://dial.uclouvain.be/solr6/repository/select?&start=0&rows=999999&qt=standard&wt=python'
            arguments = ""
            need_and = False

            if title is not "":
                if need_and:
                    arguments += " AND "
                arguments += "sm_title:\"" + title + "\""
                need_and = True
            if creator is not "":
                if need_and:
                    arguments += " AND "
                arguments += "sm_creator:\"" + creator + "\""
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
            returned_page = urllib.request.urlopen(url)

            string_dict = returned_page.read().decode(returned_page.headers._charset or "utf-8")
            python_dict = literal_eval(string_dict)

            search_result = []
            message = ""
            if 'response' not in python_dict or 'docs' not in python_dict['response']:
                message = "Got an incorrect answer"
            else:
                message = "Found " + str(python_dict['response']['numFound']) + " matching result(s)."
                search_result = sorted(python_dict['response']['docs'], key=lambda k: k.get('sm_date', ["-"]),
                                       reverse=True)

            return render_template("dial.html", search_result=search_result, message_result=message)
        elif action == "import":
            title = request.form.get('title')
            description = request.form.get('description')
            link = request.form.get('link')
            return new_post([title, description, link])
