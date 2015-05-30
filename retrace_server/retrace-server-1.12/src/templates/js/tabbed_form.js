$(function() {

    $('#create-by-bugid-form-link').click(function(e) {
        $("#create-by-bugid-form").delay(100).fadeIn(100);
        $("#create-by-url-form").fadeOut(100);
        $('#create-by-url-form-link').removeClass('active');
        $(this).addClass('active');
        e.preventDefault();
    });
    $('#create-by-url-form-link').click(function(e) {
        $("#create-by-url-form").delay(100).fadeIn(100);
        $("#create-by-bugid-form").fadeOut(100);
        $('#create-by-bugid-form-link').removeClass('active');
        $(this).addClass('active');
        e.preventDefault();
    });

});

