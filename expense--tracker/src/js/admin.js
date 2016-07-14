$(document).ready(function() {
    $(".glyphicon-remove").click(function() {
        var data = { to_delete : $(this).data("id") };
        var self = this;
        var message = "Are you sure you want to delete the transaction '" +
                  $(this).data("details") + "'?";
        var flag = confirm(message);
        if (!flag) {
            return;
        }
        $.post("/request", data).done(function() {
            $(self).closest("tr").hide();
        }).fail(function(response) {
            alert("Something went wrong..." + JSON.stringify(response));
        });
    });

    $("#delete-project").click(function(e) {
        var message = "Are you sure you want to delete this project?";
        var confirmDelete = confirm(message);
        if (!confirmDelete) {
            e.preventDefault();
        }
    });
});