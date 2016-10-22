$(function()
{
    $(document).on('click', '.btn-add', function(e)
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
    }).on('click', '.btn-remove', function(e)
    {
        $(this).parents('.entry:first').remove();

        e.preventDefault();
        return false;
    });
});
