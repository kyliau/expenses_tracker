function getTodayDate() {
    // Return today's date in yyyy-mm-dd format.
    let today = new Date();
    let dd = today.getDate();
    let mm = today.getMonth() + 1;
    let yyyy = today.getFullYear();
    if (dd < 10) {
        dd = "0" + dd;
    }
    if (mm < 10) {
        mm = "0" + mm;
    }
    return yyyy + "-" + mm + "-" + dd;
}

function calculateSplit() {
    // Write the amount of each individual to the input element when
    // amount is split equally.
    let amountInput = $("input[name=amount]");
    let total = parseFloat(amountInput.val());
    let count = $(".participant:checked").length;
    $(".participant").each(function() {
        let amount = this.checked ? total / count : 0;
        $("input[name=" + this.value + "]").val(amount);
    });
}

$(document).ready(function() {
    let numParticipants = $("option").length;

    $("input[name=date]").val(getTodayDate());

    $(".participant").change(function() {
        let inputElem = $("input[name=" + this.value + "]");
        if (this.checked) {
            inputElem.closest(".form-group").show();
        } else {
            inputElem.closest(".form-group").hide();
        }
        let flag = $(".participant:checked").length === numParticipants;
        $("#splitAll").prop("checked", flag);
    });

    $("#splitAll").click(function() {
        $(".participant").prop("checked", this.checked)
                         .trigger("change");
    });

    let previousPerson = "";
    $("select[name=paid_by]").click(function() {
        previousPerson = this.value;
    }).change(function() {
        if (!$("#splitAll").is(":checked")) {
            let currentPerson = this.value;
            $("#" + previousPerson).prop("checked", false)
                                   .trigger("change");
            $("#" + currentPerson).prop("checked", true).trigger("change");
        }
    }).trigger("change");

    $("#splitEqually").click(function() {
        if (this.checked) {
            $("#individualAmount").hide();
        } else {
            $("#individualAmount input").val("");
            $("#individualAmount").show();
        }
    });
});

$(document).ready(function() {
    $("form").submit(function(event) {
        let splitWith = $(".participant").filter(() => this.checked)
                                         .map(() => this.value)
                                         .get();
        $("input[name=split_with]").val(splitWith.join(","));
        let details = $("input[name=details]").val().trim();
        if (details.length === 0) {
            alert("Please enter transaction details");
            event.preventDefault();
            return;
        }

        let amountInput = $("input[name=amount]");
        let total = parseFloat(amountInput.val());
        if (isNaN(total) || total <= 0) {
            alert("Amount is invalid");
            event.preventDefault();
            return;
        }

        if ($("#splitEqually").is(":checked")) {
            if ($(".participant:checked").length === 0) {
                alert("Must choose at least one person to split");
                event.preventDefault();
                return;
            }
            calculateSplit();
        } else {
            let sum = 0;
            $("#individualAmount input").each(function() {
                let amount = parseFloat(this.value);
                if (!isNaN(amount)) {
                    sum += amount;
                }
            });
            if (Math.abs(sum - total) > 0.01) {
                alert("Amount does not tally");
                event.preventDefault();
            }
        }
    });
});
