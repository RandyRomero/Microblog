import os
import click

# To add a new language, you use
# flask translate init <language-code>

# To update all the languages after making changes to the _() and _l() language markers
# flask translate update

# To compile all languages after updating the translation files:
# flask translate compile


def register(app):
    @app.cli.group()
    def translate():
        """Translation and localization command"""
        # Since this is a parent command that only exists to provide a
        # base for the sub-commands, the function itself does not need to do anything
        pass

    @translate.command()
    def update():
        """Update all languages"""

        # extract gets all the choosen strings from the code and put it to one file
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            # os.system send a command to terminal and should return 0 if everything's fine
            raise RuntimeError('extract command failed')

        # The update call takes the new messages.pot file and merges it into all
        # the messages.po files associated with the project. This is going to be an intelligent merge, in
        # which any existing texts will be left alone, while only entries that were added or removed in
        # messages.pot will be affected.
        # After the messages.po are updated, you can go ahead and translate any new tests, then compile
        # the messages one more time to make them available to the application.
        if os.system('pybabel update -i messages.pot -d app/translations'):
            raise RuntimeError('update command failed')
        os.remove('messages.pot')

    @translate.command()
    def compile_lang():
        """
        Compile all languages

        This operation adds a messages.mo file next to messages.po in each language repository. The
        .mo file is the file that Flask-Babel will use to load translations for the application.
        After you create the messages.mo file for Spanish or any other languages you added to the
        project, these languages are ready to be used in the application.
        """
        if os.system('pybabel compile -d app/translations'):
            raise RuntimeError('compile command failed')


    @translate.command()
    @click.argument('lang')
    def init(lang):
        """Initialize a new language

        The pybabel init command takes the messages.pot file as input and writes a new language
        catalog to the directory given in the -d option for the language specified in the -l option.
        I’m going to be installing all the translations in the app/translations directory, because that is
        where Flask-Babel will expect translation files to be by default. The command will create a es
        subdirectory inside this directory for the Spanish data files. In particular, there will be a new file
        named app/translations/es/LC_MESSAGES/messages.po, that is where the translations need to
        be made.
        """

        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system('pybabel init -i messages.pot -d app/translations -l ' + lang):
            raise RuntimeError('init command failed')
        os.remove('messages.pot')
