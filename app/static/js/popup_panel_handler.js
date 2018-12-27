// function for showing popup panel with information about the user when mouse is on a someone's nickname

$(function() {
    let timer = null;
    let xhr = null;
    // hover takes two arguments - handler for in and handler for out
    $('.user_popup').hover(
        function(event) {
            // mouse is in event handler
            let elem = $(event.currentTarget);
            timer = setTimeout(() => {
                timer = null;
                xhr = $.ajax(`/user/${elem.first().text().trim()}/popup`)
                    .done((data) => {
                        xhr = null;
                        elem.popover({
                            trigger: 'manual',
                            html: true,
                            animation: false,
                            container: elem,
                            content: data
                        }).popover('show');
                        flask_moment_render_all();
                    })
            }, 1000);
        },
        function(event) {
            //mouse is out of event handler
            let elem = $(event.currentTarget);
            if (timer) {
                clearTimeout(timer);
                timer = null;
            } else if (xhr) {
                xhr.abort();
                xhr = null;
            } else {
                elem.popover('destroy');
            }
        }
    )
} );