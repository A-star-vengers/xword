$(function()
{
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
