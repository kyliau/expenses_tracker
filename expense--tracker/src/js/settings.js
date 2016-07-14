$(document).ready(function() {
    var form = $("#project-settings");
    var initialData = form.serialize();
    form
    .change(function() {
        var newData = form.serialize();
        $("button[type=submit]").prop("disabled",
                                      newData === initialData);
    })
    .submit(function(e) {
        var success = $(".alert-success");
        var failure = $(".alert-danger");
        var currentData = $(this).serialize();
        success.hide();
        failure.hide();
        $.post("/settings", currentData)
        .done(function(response) {
            initialData = currentData;
            success.text(response).slideDown();
        })
        .fail(function() {
            failure.slideDown();
        });
        e.preventDefault();
    });
});