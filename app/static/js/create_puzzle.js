$(function()
{
    function getSuggests(theme)
    {
        //var theme = $('.theme-input')[0].value;

        console.log("getSuggests");
        console.log("Theme " + theme);

        var ajax_params = {};

        if (theme == "" || theme == undefined)
        {
            ajax_params =
                {
                    "num_suggests" : 6
                };
        }
        else
        {
            ajax_params =
                {
                    "num_suggests" : 6,
                    "theme" : theme
                };
        }

        $.ajax({
            url : '/suggests',
            type : 'GET',
            data :
                {
                    "num_suggests" : 6,
                    "theme" : theme
                }
            ,
            success : function(data)
                    {
                        var json_hints = JSON.parse(data);

                        if (json_hints == {})
                            return;

                        $('tbody').empty();

                        var suggestForm = $('tbody');

                        //console.log(json_hints);

                        for (var hint_num in json_hints)
                        {
                            var suggest = json_hints[hint_num];

                            //console.log(suggest);

                            suggestForm.append(
                                '<tr>' +
                                    '<td>' + suggest['hint'] + '</td>' +
                                    '<td>' + suggest['answer'] + '</td>' +
                                    '<td>' + suggest['author'] + '</td>' +
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
                    }
        });
    };

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
        $(this).parents('.entry_wrap').remove();

        var entries = $('.entry_wrap'); 

        entries.each(function( index )
        {
            console.log("Each index: " + index);
            console.log("H3 value: " + $(this).find('h3').val());
            $(this).find('h3').text('Pair ' + index);
            $(this).find('input[name^=hint]').attr("name", "hint_" + index);
            $(this).find('input[name^=answer]').attr("name", "answer_" + index);
        });

        /*
        for (var i = 0; i < entries.length; i++)
        {
            entries.get(i).find('h2').val('Pair ' + i);
            entries.get(i).find('input[name^=hint]').attr("name", "hint_" + i);
            entries.get(i).find('input[name^=answer]').attr("name", "answer_" + i);
        }*/

        /*
        for (var i = 0; i < pairForm.children().length - 3; i++)
        {
            pairForm.children().get(i+3).find('h2').val('Pair ' + i);
            pairForm.children().get(i+3).find('input[name^=hint]').attr("name", "hint_" + i); 
            pairForm.children().get(i+3).find('input[name^=answer]').attr("name", "answer_" + i);
        }*/
    })
    .on('click', '.btn-small.btn-add', function(e)
    {
        var pairForm = $('#pair_form');

        var formLength = pairForm.children().length;

        console.log(formLength);

        var hint = $(this).parents('tr').children()[0].innerText;

        var answer = $(this).parents('tr').children()[1].innerText;

        pairForm.append(
        '<div class="entry_wrap">' +
            '<h3>Pair ' + (formLength - 3) + '</h3>' +
            '<div class="entry input-group col-s-3">' +
                '<input class="form-control" readonly name="hint_' + (formLength - 3) + '" type="text" value="' + hint + '"/>' +
                '<input class="form-control" readonly name="answer_' + (formLength - 3) + '" type="text" value="' + answer + '"/>' +
                '<span class="input-group-btn">' +
                    '<button class="btn btn-danger btn-remove btn-primary" type="button">' +
                        '<span class="glyphicon glyphicon-minus"></span>' +
                    '</button>' +
                '</span>' +
            '</div>' +
        '</div>'
        );
    })
    /*.on('click', '.btn-small.btn-add', function(e)
    {
        e.preventDefault();

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

        // Remove the current element from the suggestion table
        $(this).parents('tr').remove();

        // Update the suggestion table with new suggestions
    })*/.on('click', '.btn-small.btn-remove', function(e)
    {
        e.preventDefault();

        $(this).parents('tr').remove();

        var theme = $('.theme-input')[0].value;

        getSuggests(theme);

    }).on('click', '#new_suggests', function(e)
    {
        var theme = $('.theme-input')[0].value;

        getSuggests(theme);

    })
    .on('keyup', '.theme-input', function(e)
    {
        e.preventDefault();

        //console.log("Field keyed.");

        //console.log($(this).find('input'));

        var prefix = $(this)[0].value;

        $(this).autocomplete( {

            source: function (request, response)
                {
                    $.ajax({
                        url : '/themes',
                        type : 'GET',
                        data :
                            {
                                "num_themes" : 10,
                                "prefix" : prefix
                            },
                        success : function(data)
                                {
                                    var jsource = JSON.parse(data);

                                    //console.log(jsource);

                                    response(jsource["themes"]);
                                }
                        }
                    );
                },
            select: function (evt, ui)
                {
                    //console.log(ui);
                    //console.log(ui.item.value);
                    getSuggests(ui.item.value);
                },
            response: function (evt, ui)
                {
                    //console.log("response");
                    //console.log("prefix " + prefix);
                    //console.log(ui.content);

                    for (var i = 0; i < ui.content.length; i++)
                    {
                        if (prefix == ui.content[i].value)
                            getSuggests(ui.content[i].value);
                    }
                }
        });
    });
});
