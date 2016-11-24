$(function()
{
    var saved_hints = [];

    $(document).on('click', '.btn-add', function(e)
    {
        e.preventDefault();

        var tbody = $(this).parents('tr').parents('tbody');

        var currentEntry = $(this).parents('tr');

        var newEntry = $(currentEntry.clone()).appendTo(tbody);

        var newLength = tbody[0].children.length;

        newEntry.find('input').val('');

        newEntry.find('input[name^=theme]').attr('name', 'theme' + newLength);

        currentEntry.find('.btn-add').removeClass('btn-add')
                                     .addClass('btn-remove')
                                     .addClass('btn-danger')
                    .html('<span class="glyphicon glyphicon-minus"></span>');
    }).
    on('click', '.btn-remove', function(e)
    {
        $(this).parents('tr').remove();
    })
    .on('click', '#pair-addition', function(e)
    {
        e.preventDefault();

        var hPairInfo = $(this).parents().find('#pair-form');

        var hint = hPairInfo.find('#hint').val();

        var answer = hPairInfo.find('#answer').val();

        if (hint == "" || answer == "")
        {
            console.log("No information to add for submission.");
            return;
        }

        var themeBody = hPairInfo.find('tbody');

        var themes = jQuery.map(themeBody.find('input'), 
                        function(n, i)
                        {
                            if (n.value != "" && n.value != undefined)
                                return n.value;
                        });

        saved_hints.push({
                                "hint" : hint,
                                "answer" : answer,
                                "themes" : themes
                         }
                        );

        var saved_hint = {
                            "hint" : hint,
                            "answer" : answer,
                            "themes" : themes
                         };

        console.log("Saved hints");

        for (var i = 0; i < saved_hints.length; i++)
            console.log(saved_hints[i]);

        var sTable= $('.for-submission').find('tbody');

        sTable.append(
            '<tr>' +
                '<td>' + hint + "</td>" +
                '<td>' + answer + "</td>" + 
                '<td>' +
                    '<button type="button" class="btn btn-primary edit-pair">Edit Pair</button>' +
                    '<a href="javascript:;" class="btn btn-danger btn-primary btn-remove">' +
                        '<span class="glyphicon glyphicon-minus"></span>' +
                    '</a>' +
                '</td>' +
            '</tr>'
        );

        var lastEntry = sTable.find('tr').last();

        lastEntry[0].saved_hint = saved_hint;

        //Clear hint/answer pair input form to allow for another hint/answer pair
        hPairInfo.find('#hint')[0].value = "";
        hPairInfo.find('#answer')[0].value = ""; 

        hPairInfo.find('tbody').empty();

        hPairInfo.find('tbody').append(
                '<tr>' +
                  '<td>' +
                    '<div class="ui-widget">' +
                        '<input type="text" name=\'theme1\' placeholder=\'Theme\' class="form-control theme-input"/>' +
                    '</div>' +
                  '</td>' +
                  '<td>' +
                    '<a href="javascript:;" class="btn btn-small btn-primary btn-add">' +
                        '<span class="glyphicon glyphicon-plus"></span>' +
                    '</a>' +
                  '</td>' +
                '</tr>'
        );
    })
    .on('click', '.edit-pair', function(e)
    {
        e.preventDefault();

        trElem = $(this).parents()[1];

        var savedHint = trElem.saved_hint["hint"];
    
        console.log("Saved Hint: " + savedHint);

        var savedAnswer = trElem.saved_hint["answer"];

        console.log("Saved Answer: " + savedAnswer);

        var savedThemes = trElem.saved_hint["themes"];

        console.log("Themes: " + savedThemes);

        var hPairInfo = $(this).parents().find('#pair-form'); 

        //Restore field information
        hPairInfo.find('#hint')[0].value = savedHint;

        hPairInfo.find('#answer')[0].value = savedAnswer; 

        hPairInfo.find('tbody').empty();

        for (var i = 0; i < savedThemes.length; i++)
        {
            hPairInfo.find('tbody').append(
                '<tr>' +
                  '<td>' +
                    '<div class="ui-widget">' +
                        '<input type="text" name=\'theme1\' placeholder=\'Theme\' class="form-control theme-input"/>' +
                    '</div>' +
                  '</td>' +
                  '<td>' +
                    '<a href="javascript:;" class="btn btn-small btn-primary btn-add">' +
                        '<span class="glyphicon glyphicon-plus"></span>' +
                    '</a>' +
                  '</td>' +
                '</tr>'
            );

            console.log("Saved Themes: " + savedThemes[i]);
            hPairInfo.find('tbody').last().find('input')[0].value = savedThemes[i];
        }

        
    })
    .on('keyup', '.theme-input', function(e)
    {
        e.preventDefault();

        console.log("Field keyed.");

        console.log($(this).find('input'));

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

                                    console.log(jsource);

                                    response(jsource["themes"]);
                                }
                        }
                    );
                }
        });
    });
});
