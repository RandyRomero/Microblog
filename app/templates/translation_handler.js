// cache loading gif beforehand
// The Image() constructor creates a new HTMLImageElement instance.
// It is functionally equivalent to document.createElement('img').
let loading_gif = new Image();
loading_gif.src = '{{ url_for('static', filename='loading.gif') }}';

// to store text of post before it was translated to be able to get it back later
originalPosts = {};


// Substitute text of a post with its translation to a language user have set in his browser as main
// And put link to a tranlation service (required to use this service)
function translate(destElem, postID, button) {
    let text = destElem.text();
    originalPosts[postID] = text; // save original text of the post
    $(destElem).html(loading_gif);
    $.post('/translate', {
        text: text,
        postID: postID
    }).done((response) => {
        // insert text from server into post
        $(destElem).text(response['text']);

        // add promotion link in post
        let promotion_link = '<p><a class="yandex-plug" href="http://translate.yandex.com/">' +
            'Powered by Yandex.Translate</a></p>';
        $(destElem).after(promotion_link);

        // Change button to show user that he can get back original text of post
        button.text('{{ _('Original text')}}' );

        // Get rid of focus state
        button.blur();
    }).fail(() => { $(destElem).text('{{ _('Sorry, translations service is not available now.') }}');
    });
}

// get post back how it was before its translation
function getOrigTextBack(postID, destElem, button) {

    // get rid of promotion link of yandex translate service
    $(`#post${postID} > p > a.yandex-plug`).closest('p').remove();
    // get back original text of a post
    destElem.text(originalPosts[postID]);

    // get button back how it looked like
    button.text('{{ _('Translate') }}');
    button.blur();
}

function postClickHandler(event) {

    // find text to translate
    let destElem = ($(event.target).closest('td').find('p').first());

    // find post id to get source language of a post from a database
    let re = /post(\d+)/g;
    let postID = re.exec(destElem.closest('td').attr('id'))[1];

    // Choose between translating post and getting it back how it was before translation.
    // If text of a button says Original text - get it back, otherwise - translate.
    if ($(event.target).text() === '{{ _('Original text') }}') {
        getOrigTextBack(postID, destElem, $(event.target));
    } else {
        translate(destElem, postID, $(event.target));
    }
}

$('.container').on('click', '.translation', postClickHandler);