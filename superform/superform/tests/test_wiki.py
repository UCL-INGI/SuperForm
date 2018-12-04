import os
import tempfile
import json
import pytest
import re

from urllib.parse import urlencode
from urllib.request import Request, urlopen
from superform import app, db, User, Post
from superform.models import Publishing, Channel
from superform.plugins import wiki

@pytest.fixture
def client():
    app.app_context().push()
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    client = app.test_client()
    with app.app_context():
        db.create_all()
    yield client
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


# def get_url_wiki():
#     return "http://localhost/pmwiki-2.2.110/pmwiki.php"


def get_url_wiki():
    c = db.session.query(Channel).filter(Channel.module == "superform.plugins.wiki").first()
    return get_url(c.config)


def test_wiki(client):
    url = get_url_wiki()
    post_fields = {'n': "PmWiki.Rododendron_au_pissenlit_imberbe_goulish_danger_and_intolerable_colony", 'text': "bleu \n  \nbleu aussi", 'action': 'edit', 'post': 1, 'author': 'Jean-Michel'}
    request = Request(url, urlencode(post_fields).encode())
    response = urlopen(request)
    mybytes = response.read()
    mystr = mybytes.decode("utf8")
    print(mystr)
    # response_text = response.read()
    assert 'bleu \n  \nbleu aussi' in mystr

# test = 'b\'<!DOCTYPE html \n    PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \n    \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n<html xmlns=\"http://www.w3.org/1999/xhtml\" >\n<head>\n  <title>PmWiki | PmWiki / Titre </title>\n  <meta http-equiv=\'Content-Style-Type\' content=\'text/css\' />\n  <link rel=\'stylesheet\' href=\'http://localhost:8001/pub/skins/pmwiki/pmwiki.css\' type=\'text/css\' />\n  <!--HTMLHeader--><style type=\'text/css\'><!--\n  ul, ol, pre, dl, p { margin-top:0px; margin-bottom:0px; }\n  code.escaped { white-space: nowrap; }\n  .vspace { margin-top:1.33em; }\n  .indent { margin-left:40px; }\n  .outdent { margin-left:40px; text-indent:-40px; }\n  a.createlinktext { text-decoration:none; border-bottom:1px dotted gray; }\n  a.createlink { text-decoration:none; position:relative; top:-0.5em;\n    font-weight:bold; font-size:smaller; border-bottom:none; }\n  img { border:0px; }\n  .editconflict { color:green; \n  font-style:italic; margin-top:1.33em; margin-bottom:1.33em; }\n\n  table.markup { border:2px dotted #ccf; width:90%; }\n  td.markup1, td.markup2 { padding-left:10px; padding-right:10px; }\n  table.vert td.markup1 { border-bottom:1px solid #ccf; }\n  table.horiz td.markup1 { width:23em; border-right:1px solid #ccf; }\n  table.markup caption { text-align:left; }\n  div.faq p, div.faq pre { margin-left:2em; }\n  div.faq p.question { margin:1em 0 0.75em 0; font-weight:bold; }\n  div.faqtoc div.faq * { display:none; }\n  div.faqtoc div.faq p.question \n    { display:block; font-weight:normal; margin:0.5em 0 0.5em 20px; line-height:normal; }\n  div.faqtoc div.faq p.question * { display:inline; }\n  td.markup1 pre { white-space: pre-wrap; }\n   \n    .frame \n      { border:1px solid #cccccc; padding:4px; background-color:#f9f9f9; }\n    .lfloat { float:left; margin-right:0.5em; }\n    .rfloat { float:right; margin-left:0.5em; }\na.varlink { text-decoration:none;}\n\n--></style>  <meta name=\'robots\' content=\'noindex,nofollow\' />\n\n</head>\n<body>\n<!--PageHeaderFmt-->\n  <div id=\'wikilogo\'><a href=\'http://localhost:8001/pmwiki.php\'><img src=\'http://localhost:8001/pub/skins/pmwiki/pmwiki-32.gif\'\n    alt=\'PmWiki\' border=\'0\' /></a></div>\n  <div id=\'wikihead\'>\n  <form action=\'http://localhost:8001/pmwiki.php\'>\n    <span class=\'headnav\'><a href=\'http://localhost:8001/pmwiki.php?n=PmWiki.RecentChanges\'\n      accesskey=\'c\'>Recent Changes</a> -</span>\n    <input type=\'hidden\' name=\'n\' value=\'PmWiki.Titre\' />\n    <input type=\'hidden\' name=\'action\' value=\'search\' />\n    <a href=\'http://localhost:8001/pmwiki.php?n=Site.Search\'>Search</a>:\n    <input type=\'text\' name=\'q\' value=\'\' class=\'inputbox searchbox\' />\n    <input type=\'submit\' class=\'inputbutton searchbutton\'\n      value=\'Go\' /></form></div>\n<!--/PageHeaderFmt-->\n  <table id=\'wikimid\' width=\'100%\' cellspacing=\'0\' cellpadding=\'0\'><tr>\n<!--PageLeftFmt-->\n      <td id=\'wikileft\' valign=\'top\'>\n        <ul><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=Main.HomePage\'>HomePage</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=Main.WikiSandbox\'>WikiSandbox</a>\n</li></ul><p class=\'vspace sidehead\'> <a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.PmWiki\'>PmWiki</a>\n</p><ul><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.InitialSetupTasks\'>Initial Setup Tasks</a>  \n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.BasicEditing\'>Basic Editing</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.DocumentationIndex\'>Documentation Index</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.FAQ\'>PmWiki FAQ</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.PmWikiPhilosophy\'>PmWikiPhilosophy</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.ReleaseNotes\'>Release Notes</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.ChangeLog\'>ChangeLog</a>\n</li></ul><p class=\'vspace sidehead\'> <a class=\'urllink\' href=\'http://www.pmwiki.org\' rel=\'nofollow\'>pmwiki.org</a>\n</p><ul><li><a class=\'urllink\' href=\'https://www.pmwiki.org/wiki/Cookbook/Cookbook\' rel=\'nofollow\'>Cookbook (addons)</a>\n</li><li><a class=\'urllink\' href=\'https://www.pmwiki.org/wiki/Cookbook/Skins\' rel=\'nofollow\'>Skins (themes)</a>\n</li><li><a class=\'urllink\' href=\'https://www.pmwiki.org/wiki/PITS/PITS\' rel=\'nofollow\'>PITS (issue tracking)</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.MailingLists\'>Mailing Lists</a>\n</li></ul><p class=\'vspace\'  style=\'text-align: right;\'> <span style=\'font-size:83%\'><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=Site.SideBar?action=edit\'>edit SideBar</a></span>\n</p>\n</td>\n<!--/PageLeftFmt-->\n      <td id=\'wikibody\' valign=\'top\'>\n<!--PageActionFmt-->\n        <div id=\'wikicmds\'><ul><li class=\'browse\'>      <a accesskey=\'\'  rel=\'nofollow\'  class=\'selflink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre\'>View</a>\n</li><li class=\'edit\'>      <a accesskey=\'e\'  rel=\'nofollow\'  class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=edit\'>Edit</a>\n</li><li class=\'diff\'>   <a accesskey=\'h\'  rel=\'nofollow\'  class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=diff\'>History</a>\n</li><li class=\'print\'>     <a accesskey=\'\'  rel=\'nofollow\'  class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=print\'>Print</a>\n</li><li class=\'backlinks\'> <a accesskey=\'\'  rel=\'nofollow\'  class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=search&amp;q=link=PmWiki.Titre\'>Backlinks</a>\n</li></ul>\n</div>\n<!--PageTitleFmt-->\n        <div id=\'wikititle\'>\n          <div class=\'pagegroup\'><a href=\'http://localhost:8001/pmwiki.php?n=PmWiki\'>PmWiki</a> /</div>\n          <h1 class=\'pagetitle\'>Titre</h1></div>\n<!--PageText-->\n<div id=\'wikitext\'>\n<p>\n<a name=\'trailstart\' id=\'trailstart\'></a> \n</p><div style=\'clear:right;\' >\n</div>\n<p>Texte\n \n<a name=\'trailend\' id=\'trailend\'></a>\n<br clear=\'all\' />\n</p><div  style=\'background-color: #ffe; border-top: 1px solid black; font-size: .8em;\' > \n<p>This page may have <span class=\'commentout-pmwikiorg\'> a more recent version on <a class=\'urllink\' href=\'http://www.pmwiki.org\' rel=\'nofollow\'>pmwiki.org</a>: <a class=\'urllink\' href=\'https://www.pmwiki.org/wiki/PmWiki/Titre\' rel=\'nofollow\'>PmWiki:Titre</a>, and </span> a talk page: <a class=\'urllink\' href=\'https://www.pmwiki.org/wiki/PmWiki/Titre-Talk\' rel=\'nofollow\'>PmWiki:Titre-Talk</a>.\n</p></div>\n</div>\n\n      </td>\n    </tr></table>\n<!--PageFooterFmt-->\n  <div id=\'wikifoot\'>\n    <div class=\'footnav\'>\n      <a rel=\"nofollow\" href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=edit\'>Edit</a> -\n      <a rel=\"nofollow\" href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=diff\'>History</a> -\n      <a rel=\"nofollow\" href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=print\' target=\'_blank\'>Print</a> -\n      <a href=\'http://localhost:8001/pmwiki.php?n=PmWiki.RecentChanges\'>Recent Changes</a> -\n      <a href=\'http://localhost:8001/pmwiki.php?n=Site.Search\'>Search</a></div>\n    <div class=\'lastmod\'>Page last modified on November 07, 2018, at 05:21 PM</div></div>\n<!--HTMLFooter-->\n</body>\n</html>\n'

# def test_wiki_different_request(client):
#     url = get_url_wiki()
#     post_fields = {'n': "Vide", 'text': "Texte", 'action': 'edit', 'post': 1}
#     request = Request(url, urlencode(post_fields).encode())
#     response = urlopen(request)
#     test = "b'<!DOCTYPE html \n    PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \n    \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n<html xmlns=\"http://www.w3.org/1999/xhtml\" >\n<head>\n  <title>PmWiki | PmWiki / Titre </title>\n  <meta http-equiv=\'Content-Style-Type\' content=\'text/css\' />\n  <link rel=\'stylesheet\' href=\'http://localhost:8001/pub/skins/pmwiki/pmwiki.css\' type=\'text/css\' />\n  <!--HTMLHeader--><style type=\'text/css\'><!--\n  ul, ol, pre, dl, p { margin-top:0px; margin-bottom:0px; }\n  code.escaped { white-space: nowrap; }\n  .vspace { margin-top:1.33em; }\n  .indent { margin-left:40px; }\n  .outdent { margin-left:40px; text-indent:-40px; }\n  a.createlinktext { text-decoration:none; border-bottom:1px dotted gray; }\n  a.createlink { text-decoration:none; position:relative; top:-0.5em;\n    font-weight:bold; font-size:smaller; border-bottom:none; }\n  img { border:0px; }\n  .editconflict { color:green; \n  font-style:italic; margin-top:1.33em; margin-bottom:1.33em; }\n\n  table.markup { border:2px dotted #ccf; width:90%; }\n  td.markup1, td.markup2 { padding-left:10px; padding-right:10px; }\n  table.vert td.markup1 { border-bottom:1px solid #ccf; }\n  table.horiz td.markup1 { width:23em; border-right:1px solid #ccf; }\n  table.markup caption { text-align:left; }\n  div.faq p, div.faq pre { margin-left:2em; }\n  div.faq p.question { margin:1em 0 0.75em 0; font-weight:bold; }\n  div.faqtoc div.faq * { display:none; }\n  div.faqtoc div.faq p.question \n    { display:block; font-weight:normal; margin:0.5em 0 0.5em 20px; line-height:normal; }\n  div.faqtoc div.faq p.question * { display:inline; }\n  td.markup1 pre { white-space: pre-wrap; }\n   \n    .frame \n      { border:1px solid #cccccc; padding:4px; background-color:#f9f9f9; }\n    .lfloat { float:left; margin-right:0.5em; }\n    .rfloat { float:right; margin-left:0.5em; }\na.varlink { text-decoration:none;}\n\n--></style>  <meta name=\'robots\' content=\'noindex,nofollow\' />\n\n</head>\n<body>\n<!--PageHeaderFmt-->\n  <div id=\'wikilogo\'><a href=\'http://localhost:8001/pmwiki.php\'><img src=\'http://localhost:8001/pub/skins/pmwiki/pmwiki-32.gif\'\n    alt=\'PmWiki\' border=\'0\' /></a></div>\n  <div id=\'wikihead\'>\n  <form action=\'http://localhost:8001/pmwiki.php\'>\n    <span class=\'headnav\'><a href=\'http://localhost:8001/pmwiki.php?n=PmWiki.RecentChanges\'\n      accesskey=\'c\'>Recent Changes</a> -</span>\n    <input type=\'hidden\' name=\'n\' value=\'PmWiki.Titre\' />\n    <input type=\'hidden\' name=\'action\' value=\'search\' />\n    <a href=\'http://localhost:8001/pmwiki.php?n=Site.Search\'>Search</a>:\n    <input type=\'text\' name=\'q\' value=\'\' class=\'inputbox searchbox\' />\n    <input type=\'submit\' class=\'inputbutton searchbutton\'\n      value=\'Go\' /></form></div>\n<!--/PageHeaderFmt-->\n  <table id=\'wikimid\' width=\'100%\' cellspacing=\'0\' cellpadding=\'0\'><tr>\n<!--PageLeftFmt-->\n      <td id=\'wikileft\' valign=\'top\'>\n        <ul><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=Main.HomePage\'>HomePage</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=Main.WikiSandbox\'>WikiSandbox</a>\n</li></ul><p class=\'vspace sidehead\'> <a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.PmWiki\'>PmWiki</a>\n</p><ul><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.InitialSetupTasks\'>Initial Setup Tasks</a>  \n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.BasicEditing\'>Basic Editing</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.DocumentationIndex\'>Documentation Index</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.FAQ\'>PmWiki FAQ</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.PmWikiPhilosophy\'>PmWikiPhilosophy</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.ReleaseNotes\'>Release Notes</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.ChangeLog\'>ChangeLog</a>\n</li></ul><p class=\'vspace sidehead\'> <a class=\'urllink\' href=\'http://www.pmwiki.org\' rel=\'nofollow\'>pmwiki.org</a>\n</p><ul><li><a class=\'urllink\' href=\'https://www.pmwiki.org/wiki/Cookbook/Cookbook\' rel=\'nofollow\'>Cookbook (addons)</a>\n</li><li><a class=\'urllink\' href=\'https://www.pmwiki.org/wiki/Cookbook/Skins\' rel=\'nofollow\'>Skins (themes)</a>\n</li><li><a class=\'urllink\' href=\'https://www.pmwiki.org/wiki/PITS/PITS\' rel=\'nofollow\'>PITS (issue tracking)</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.MailingLists\'>Mailing Lists</a>\n</li></ul><p class=\'vspace\'  style=\'text-align: right;\'> <span style=\'font-size:83%\'><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=Site.SideBar?action=edit\'>edit SideBar</a></span>\n</p>\n</td>\n<!--/PageLeftFmt-->\n      <td id=\'wikibody\' valign=\'top\'>\n<!--PageActionFmt-->\n        <div id=\'wikicmds\'><ul><li class=\'browse\'>      <a accesskey=\'\'  rel=\'nofollow\'  class=\'selflink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre\'>View</a>\n</li><li class=\'edit\'>      <a accesskey=\'e\'  rel=\'nofollow\'  class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=edit\'>Edit</a>\n</li><li class=\'diff\'>   <a accesskey=\'h\'  rel=\'nofollow\'  class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=diff\'>History</a>\n</li><li class=\'print\'>     <a accesskey=\'\'  rel=\'nofollow\'  class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=print\'>Print</a>\n</li><li class=\'backlinks\'> <a accesskey=\'\'  rel=\'nofollow\'  class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=search&amp;q=link=PmWiki.Titre\'>Backlinks</a>\n</li></ul>\n</div>\n<!--PageTitleFmt-->\n        <div id=\'wikititle\'>\n          <div class=\'pagegroup\'><a href=\'http://localhost:8001/pmwiki.php?n=PmWiki\'>PmWiki</a> /</div>\n          <h1 class=\'pagetitle\'>Titre</h1></div>\n<!--PageText-->\n<div id=\'wikitext\'>\n<p>\n<a name=\'trailstart\' id=\'trailstart\'></a> \n</p><div style=\'clear:right;\' >\n</div>\n<p>Texte\n \n<a name=\'trailend\' id=\'trailend\'></a>\n<br clear=\'all\' />\n</p><div  style=\'background-color: #ffe; border-top: 1px solid black; font-size: .8em;\' > \n<p>This page may have <span class=\'commentout-pmwikiorg\'> a more recent version on <a class=\'urllink\' href=\'http://www.pmwiki.org\' rel=\'nofollow\'>pmwiki.org</a>: <a class=\'urllink\' href=\'https://www.pmwiki.org/wiki/PmWiki/Titre\' rel=\'nofollow\'>PmWiki:Titre</a>, and </span> a talk page: <a class=\'urllink\' href=\'https://www.pmwiki.org/wiki/PmWiki/Titre-Talk\' rel=\'nofollow\'>PmWiki:Titre-Talk</a>.\n</p></div>\n</div>\n\n      </td>\n    </tr></table>\n<!--PageFooterFmt-->\n  <div id=\'wikifoot\'>\n    <div class=\'footnav\'>\n      <a rel=\"nofollow\" href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=edit\'>Edit</a> -\n      <a rel=\"nofollow\" href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=diff\'>History</a> -\n      <a rel=\"nofollow\" href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=print\' target=\'_blank\'>Print</a> -\n      <a href=\'http://localhost:8001/pmwiki.php?n=PmWiki.RecentChanges\'>Recent Changes</a> -\n      <a href=\'http://localhost:8001/pmwiki.php?n=Site.Search\'>Search</a></div>\n    <div class=\'lastmod\'>Page last modified on November 07, 2018, at 05:21 PM</div></div>\n<!--HTMLFooter-->\n</body>\n</html>\n'"
#     assert test != response
#
#
# def test_wiki_empty_fields(client):
#     url = get_url_wiki()
#     post_fields = {'n': "", 'text': "", 'action': 'edit', 'post': 1}
#     request = Request(url, urlencode(post_fields).encode())
#     response = urlopen(request)
#     test = "b'<!DOCTYPE html \n    PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \n    \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n<html xmlns=\"http://www.w3.org/1999/xhtml\" >\n<head>\n  <title>PmWiki | PmWiki / Titre </title>\n  <meta http-equiv=\'Content-Style-Type\' content=\'text/css\' />\n  <link rel=\'stylesheet\' href=\'http://localhost:8001/pub/skins/pmwiki/pmwiki.css\' type=\'text/css\' />\n  <!--HTMLHeader--><style type=\'text/css\'><!--\n  ul, ol, pre, dl, p { margin-top:0px; margin-bottom:0px; }\n  code.escaped { white-space: nowrap; }\n  .vspace { margin-top:1.33em; }\n  .indent { margin-left:40px; }\n  .outdent { margin-left:40px; text-indent:-40px; }\n  a.createlinktext { text-decoration:none; border-bottom:1px dotted gray; }\n  a.createlink { text-decoration:none; position:relative; top:-0.5em;\n    font-weight:bold; font-size:smaller; border-bottom:none; }\n  img { border:0px; }\n  .editconflict { color:green; \n  font-style:italic; margin-top:1.33em; margin-bottom:1.33em; }\n\n  table.markup { border:2px dotted #ccf; width:90%; }\n  td.markup1, td.markup2 { padding-left:10px; padding-right:10px; }\n  table.vert td.markup1 { border-bottom:1px solid #ccf; }\n  table.horiz td.markup1 { width:23em; border-right:1px solid #ccf; }\n  table.markup caption { text-align:left; }\n  div.faq p, div.faq pre { margin-left:2em; }\n  div.faq p.question { margin:1em 0 0.75em 0; font-weight:bold; }\n  div.faqtoc div.faq * { display:none; }\n  div.faqtoc div.faq p.question \n    { display:block; font-weight:normal; margin:0.5em 0 0.5em 20px; line-height:normal; }\n  div.faqtoc div.faq p.question * { display:inline; }\n  td.markup1 pre { white-space: pre-wrap; }\n   \n    .frame \n      { border:1px solid #cccccc; padding:4px; background-color:#f9f9f9; }\n    .lfloat { float:left; margin-right:0.5em; }\n    .rfloat { float:right; margin-left:0.5em; }\na.varlink { text-decoration:none;}\n\n--></style>  <meta name=\'robots\' content=\'noindex,nofollow\' />\n\n</head>\n<body>\n<!--PageHeaderFmt-->\n  <div id=\'wikilogo\'><a href=\'http://localhost:8001/pmwiki.php\'><img src=\'http://localhost:8001/pub/skins/pmwiki/pmwiki-32.gif\'\n    alt=\'PmWiki\' border=\'0\' /></a></div>\n  <div id=\'wikihead\'>\n  <form action=\'http://localhost:8001/pmwiki.php\'>\n    <span class=\'headnav\'><a href=\'http://localhost:8001/pmwiki.php?n=PmWiki.RecentChanges\'\n      accesskey=\'c\'>Recent Changes</a> -</span>\n    <input type=\'hidden\' name=\'n\' value=\'PmWiki.Titre\' />\n    <input type=\'hidden\' name=\'action\' value=\'search\' />\n    <a href=\'http://localhost:8001/pmwiki.php?n=Site.Search\'>Search</a>:\n    <input type=\'text\' name=\'q\' value=\'\' class=\'inputbox searchbox\' />\n    <input type=\'submit\' class=\'inputbutton searchbutton\'\n      value=\'Go\' /></form></div>\n<!--/PageHeaderFmt-->\n  <table id=\'wikimid\' width=\'100%\' cellspacing=\'0\' cellpadding=\'0\'><tr>\n<!--PageLeftFmt-->\n      <td id=\'wikileft\' valign=\'top\'>\n        <ul><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=Main.HomePage\'>HomePage</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=Main.WikiSandbox\'>WikiSandbox</a>\n</li></ul><p class=\'vspace sidehead\'> <a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.PmWiki\'>PmWiki</a>\n</p><ul><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.InitialSetupTasks\'>Initial Setup Tasks</a>  \n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.BasicEditing\'>Basic Editing</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.DocumentationIndex\'>Documentation Index</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.FAQ\'>PmWiki FAQ</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.PmWikiPhilosophy\'>PmWikiPhilosophy</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.ReleaseNotes\'>Release Notes</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.ChangeLog\'>ChangeLog</a>\n</li></ul><p class=\'vspace sidehead\'> <a class=\'urllink\' href=\'http://www.pmwiki.org\' rel=\'nofollow\'>pmwiki.org</a>\n</p><ul><li><a class=\'urllink\' href=\'https://www.pmwiki.org/wiki/Cookbook/Cookbook\' rel=\'nofollow\'>Cookbook (addons)</a>\n</li><li><a class=\'urllink\' href=\'https://www.pmwiki.org/wiki/Cookbook/Skins\' rel=\'nofollow\'>Skins (themes)</a>\n</li><li><a class=\'urllink\' href=\'https://www.pmwiki.org/wiki/PITS/PITS\' rel=\'nofollow\'>PITS (issue tracking)</a>\n</li><li><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.MailingLists\'>Mailing Lists</a>\n</li></ul><p class=\'vspace\'  style=\'text-align: right;\'> <span style=\'font-size:83%\'><a class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=Site.SideBar?action=edit\'>edit SideBar</a></span>\n</p>\n</td>\n<!--/PageLeftFmt-->\n      <td id=\'wikibody\' valign=\'top\'>\n<!--PageActionFmt-->\n        <div id=\'wikicmds\'><ul><li class=\'browse\'>      <a accesskey=\'\'  rel=\'nofollow\'  class=\'selflink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre\'>View</a>\n</li><li class=\'edit\'>      <a accesskey=\'e\'  rel=\'nofollow\'  class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=edit\'>Edit</a>\n</li><li class=\'diff\'>   <a accesskey=\'h\'  rel=\'nofollow\'  class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=diff\'>History</a>\n</li><li class=\'print\'>     <a accesskey=\'\'  rel=\'nofollow\'  class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=print\'>Print</a>\n</li><li class=\'backlinks\'> <a accesskey=\'\'  rel=\'nofollow\'  class=\'wikilink\' href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=search&amp;q=link=PmWiki.Titre\'>Backlinks</a>\n</li></ul>\n</div>\n<!--PageTitleFmt-->\n        <div id=\'wikititle\'>\n          <div class=\'pagegroup\'><a href=\'http://localhost:8001/pmwiki.php?n=PmWiki\'>PmWiki</a> /</div>\n          <h1 class=\'pagetitle\'>Titre</h1></div>\n<!--PageText-->\n<div id=\'wikitext\'>\n<p>\n<a name=\'trailstart\' id=\'trailstart\'></a> \n</p><div style=\'clear:right;\' >\n</div>\n<p>Texte\n \n<a name=\'trailend\' id=\'trailend\'></a>\n<br clear=\'all\' />\n</p><div  style=\'background-color: #ffe; border-top: 1px solid black; font-size: .8em;\' > \n<p>This page may have <span class=\'commentout-pmwikiorg\'> a more recent version on <a class=\'urllink\' href=\'http://www.pmwiki.org\' rel=\'nofollow\'>pmwiki.org</a>: <a class=\'urllink\' href=\'https://www.pmwiki.org/wiki/PmWiki/Titre\' rel=\'nofollow\'>PmWiki:Titre</a>, and </span> a talk page: <a class=\'urllink\' href=\'https://www.pmwiki.org/wiki/PmWiki/Titre-Talk\' rel=\'nofollow\'>PmWiki:Titre-Talk</a>.\n</p></div>\n</div>\n\n      </td>\n    </tr></table>\n<!--PageFooterFmt-->\n  <div id=\'wikifoot\'>\n    <div class=\'footnav\'>\n      <a rel=\"nofollow\" href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=edit\'>Edit</a> -\n      <a rel=\"nofollow\" href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=diff\'>History</a> -\n      <a rel=\"nofollow\" href=\'http://localhost:8001/pmwiki.php?n=PmWiki.Titre?action=print\' target=\'_blank\'>Print</a> -\n      <a href=\'http://localhost:8001/pmwiki.php?n=PmWiki.RecentChanges\'>Recent Changes</a> -\n      <a href=\'http://localhost:8001/pmwiki.php?n=Site.Search\'>Search</a></div>\n    <div class=\'lastmod\'>Page last modified on November 07, 2018, at 05:21 PM</div></div>\n<!--HTMLFooter-->\n</body>\n</html>\n'"
#     assert test != response


def get_url(config):
    json_data = json.loads(config)
    return json_data["Wiki's url"]