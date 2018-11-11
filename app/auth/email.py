# -*- coding: utf-8 -*-

"""
Module that forms emails for the user
"""

from flask import render_template
from flask_babel import _
from app.email import send_email


def send_password_reset_email(user):
    """
    Make email for resetting password
    :param user: User class from database, particular user who asked to reset his password
    :return: None
    """
    token = user.get_reset_password_token()
    send_email(_('[Microblog] Reset your password'), recipients=[user.email],
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token))


def send_greeting_email(user):
    """
    Make greeting email for user that just signed up. It can help him to remember which email address he used
    when he was signing up.
    :param user: User class from database, particular user who signed up
    :return: None
    """
    send_email(_('[Microblog] Welcome!'), recipients=[user.email],
               text_body=render_template('email/greeting_email.txt', user=user),
               html_body=render_template('email/greeting_email.html', user=user)
               )
