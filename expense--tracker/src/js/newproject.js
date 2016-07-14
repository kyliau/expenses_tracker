function renumberRows() {
    $("tbody th").each(function(index) {
        $(this).text(index);
    });
}

$(document).ready(function() {
    $("#addrow").click(function() {
        $("#template-row").clone(true)
                          .removeClass("hidden")
                          .appendTo("tbody");
        renumberRows();
    });
    $(".glyphicon-remove").click(function() {
        $(this).closest("tr").remove();
        renumberRows();
    });
    $("form").submit(function() {
        //e.preventDefault();
        var participants = [];
        $("input[type=email]").each(function() {
            var email = this.value.trim();
            var isAdmin = $(this).closest("td")
                                 .next()
                                 .children()
                                 .is(":checked");
            if (email) {
                participants.push({
                    email   : email,
                    isAdmin : isAdmin
                });
            }
        });
        $("input[name=participants]").val(JSON.stringify(participants));
    });
});