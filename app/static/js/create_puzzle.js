$(function()
{
    $(document).on('click', '.btn-add.btn-success', function(e)
    {
        e.preventDefault();

        var controlForm = $('.controls form:first'),
            currentEntry = $(this).parents('.entry:first'),
            newEntry = $(currentEntry.clone()).appendTo(controlForm);

        var newLength = $('.controls .entry').length;

        newEntry.find('input').val('');
        newEntry.find(':submit').val('Create Puzzle!');
        newEntry.find('input[name^=hint]').attr("name", "hint_" + newLength);
        newEntry.find('input[name^=answer]').attr("name", "answer_" + newLength);
        controlForm.find('.entry:not(:last) .btn-add')
            .removeClass('btn-add').addClass('btn-remove')
            .removeClass('btn-success').addClass('btn-danger')
            .html('<span class="glyphicon glyphicon-minus"></span>');
        controlForm.find('.entry:not(:last) .btn-primary')
            .remove();
    }).on('click', '.btn-remove.btn-danger', function(e)
    {
        var test = $(this).parents('.entry:first')[0];
        if ( test.suggestion )
        {
            console.log(test.hint);
            console.log(test.answer);
            console.log(test.author);
            // Clone the item back into the suggestion table
            var suggestForm = $('tbody');

            suggestForm.append(
                '<tr>' +
                    '<td>' + test.hint + '</td>' +
                    '<td>' + test.answer + '</td>' +
                    '<td>' + test.author + '</td>' +
                    '<td class="td-actions">' +
                        '<a href="javascript:;" class="btn btn-small btn-primary btn-add">' +
                            '<span class="glyphicon glyphicon-plus"></span>' +
                        '</a>' +
                        '<a href="javascript:;" class="btn btn-small btn-primary btn-remove">' +
                            '<span class="glyphicon glyphicon-minus"></span>' +
                        '</a>' +

                    '</td>' +
                '</tr>'
            );
        }

        $(this).parents('.entry:first').remove();

        e.preventDefault();
        return false;
    }).on('click', '.btn-small.btn-add', function(e)
    {
        e.preventDefault();

        /* Update hint/answer pair addition part of the page */
        var hint = $(this).parents('tr').children()[0].innerText;

        var answer = $(this).parents('tr').children()[1].innerText;

        var author = $(this).parents('tr').children()[2].innerText;

        var controlForm = $('.controls form:first')[0];

        var lastEntry = controlForm.children[controlForm.children.length-1];

        var controlForm2 = $('.controls form:first');
        var currentEntry = controlForm2.find('.entry:last');

        var newEntry = $(currentEntry.clone()).appendTo(controlForm2);

        var lastEntryHint = lastEntry.children[0];
        var lastEntryAnswer = lastEntry.children[1];

        lastEntryHint.value = hint;
        lastEntryAnswer.value = answer;

        //Create an arbitrary attribute to query for when this is removed
        //When removed place back in table
        lastEntry.hint = hint;
        lastEntry.answer = answer;
        lastEntry.suggestion = true;
        lastEntry.author = author;

        var newLength = $('.controls .entry').length;

        newEntry.find('input').val('');
        newEntry.find(':submit').val('Create Puzzle!');

        newEntry.find('input[name^=hint]').attr("name", "hint_" + newLength);
        newEntry.find('input[name^=answer]').attr("name", "answer_" + newLength);

        controlForm2.find('.entry:not(:last) .btn-add')
            .removeClass('btn-add').addClass('btn-remove')
            .removeClass('btn-success').addClass('btn-danger')
            .html('<span class="glyphicon glyphicon-minus"></span>');
        controlForm2.find('.entry:not(:last) .btn-primary')
            .remove();

        /* Update the suggestion part of the page */

        // Remove the current element from the suggestion table
        $(this).parents('tr').remove();

        // Update the suggestion table with new suggestions
    }).on('click', '.btn-small.btn-remove', function(e)
    {
        //Remove the suggestion and retrieve a new one
        $(this).parents('tr').remove();

        //Send ajax query containing GET request with removed suggestion
        //as well as number of new suggestions to retrieve
    });
});
