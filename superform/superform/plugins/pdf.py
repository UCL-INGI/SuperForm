"""
author: Team 06
date: December 2018
Plugin for the PDF feature
"""

import glob
import json
import os
import time
import webbrowser

from flask import flash, redirect, render_template, send_file, send_from_directory, url_for
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from pathlib import Path
from reportlab.lib.pagesizes import A4, A5, A3
from superform.models import Channel, Post, db, Publishing, StatusCode

FIELDS_UNAVAILABLE = []

CONFIG_FIELDS = ["Format", "Logo"]

FORMATS = ["A5", "A4", "A3"]

LOGOS = ["UCL", "EPL", 'INGI']


def pdf_plugin(id, c, config_fields):
    return render_template("pdf_configuration.html", channel=c,
                           config_fields=config_fields, formats=FORMATS,
                           logos=LOGOS)


def run(publishing, channel_config, debug=False):
    """ Gathers the informations in the config column and launches the
    posting process
    channel_config format = {image : ??, size : "A4"}"""
    json_data = json.loads(channel_config)
    title = publishing.title
    body = publishing.description
    if 'Logo' not in json_data and debug is False:
        return StatusCode.ERROR, "This channel is not configured yet"
    image = json_data['Logo']
    size = json_data['Format']
    try:
        datas = create_pdf(title, body, image, size)
    except OSError:
        return StatusCode.ERROR, "A pdf file with the same name is already opened."
    except BaseException:
        return StatusCode.ERROR, "An unknown error occured whie creating the pdf."

    path = datas[0]
    outputFile = datas[1]

    data_folder = Path("superform/plugins/pdf")
    file_to_delete = Path("superform/plugins/pdf/" + outputFile)
    file_size = os.stat(file_to_delete).st_size
    current_dir = os.getcwd()
    os.chdir(data_folder)

    for file in glob.glob("*.pdf"):
        if time.time() - os.stat(file).st_atime > 3600:
            os.remove(file)
    os.chdir(current_dir)

    if path is not None and outputFile is not None:
        return StatusCode.OK, outputFile, file_size
    else:
        return StatusCode.ERROR, "PDF not created"


def export(post_id, idc):
    pdf_Channel = db.session.query(Channel).filter(
        Channel.id == idc).first()
    if pdf_Channel is not None:
        channel_config = pdf_Channel.config
    else:
        flash("PDF channel not found", category='success')
        return redirect(url_for('index'))
    myPost = db.session.query(Post).filter(
        Post.id == post_id).first()
    myPub = Publishing()
    myPub.description = myPost.description
    myPub.title = myPost.title
    code = run(myPub, channel_config)

    if code[0].value != StatusCode.OK.value:
        flash(code[1], category='error')
        return redirect(url_for('index'))
    else:
        # flash("The PDF has successfully been generated.", category='success')
        return send_from_directory("plugins/pdf/", code[1], as_attachment=True, attachment_filename=code[1])


def create_pdf(titre, corps, image="UCL", size=A4):
    empryString = ""
    fileTitle = empryString.join(e for e in titre if e.isalnum())
    if (len(fileTitle)) == 0:
        fileTitle = "DEFAULT"
    outfilename = image + "-" + size + "-" + fileTitle + ".pdf"  # every pdf channel should have different output
    localPath = os.path.dirname(__file__) + "/pdf/" + outfilename

    if size == "A5":
        mySize = A5
    elif size == "A4":
        mySize = A4
    elif size == "A3":
        mySize = A3
    else:
        mySize = "A4"  # Default value

    doc = SimpleDocTemplate(localPath, pagesize=mySize,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)

    Story = []

    # Adding logo
    # print("image path=", image)
    imagePath = Path("superform/plugins/logos/" + image + ".png")
    im = Image(imagePath)  # , 2 * inch, 2 * inch)
    Story.append(im)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, leading=15))
    Story.append(Spacer(1, 20))

    # Adding title
    p_font = 24
    Story.append(Spacer(1, 30))
    # ptext = '<font name=HELVETICA>'+title+'</font>' % p_font
    rr = """<font name=times-roman size=%s>{}</font>
        """.format(titre) % p_font
    Story.append(Paragraph(rr, styles["Normal"]))
    Story.append(Spacer(6, 26))

    # Adding body
    p_font = 13
    text = """<font name=times-roman size=%s>{}</font>
        """.format(corps) % p_font
    Story.append(Paragraph(text, styles["Justify"]))
    Story.append(Spacer(6, 12))

    # Saving pdf
    doc.build(Story)
    datas = [localPath, outfilename]
    return datas
