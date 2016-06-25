function getTodayDate() {
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth() + 1;
    var yyyy = today.getFullYear();
    if (dd < 10) {
        dd = '0' + dd;
    }
    if (mm < 10) {
        mm = '0' + mm;
    }
    return yyyy + '-' + mm + '-' + dd;
}

function foo() {
  var list = $('.participant').filter(function() {
    return this.checked;
  }).map(function() {
    return this.value;
  }).get();
  return list;
};

function calculateSplit() {
    var amountInput = $('input[name=amount]');
    var total = parseFloat(amountInput.val());
    var splits = $('.participant:checked');
    var count = splits.length;
    splits.each(function() {
        $('input[name=' + this.value + ']').val(total / count);
    });
}

$(document).ready(function() {
    var NUM_PARTICIPANT = $('option').length;

    $('input[name=date]').val(getTodayDate());

    $('.participant').change(function() {
        var inputElem = $('input[name=' + this.value + ']');
        if (this.checked) {
            inputElem.closest('.form-group').show();
        } else {
            inputElem.closest('.form-group').hide();
        }
        var flag = $('.participant:checked').length === NUM_PARTICIPANT;
        $('#splitAll').prop('checked', flag);
    });

    $('#splitAll').click(function() {
        $('.participant').prop('checked', this.checked)
                         .trigger('change');
    });

    var previousPerson = '';
    $('select[name=paid_by]').click(function() {
        previousPerson = this.value;
    }).change(function() {
        if (!$('#splitAll').is(':checked')) {
            var currentPerson = this.value;
            $('#' + previousPerson).prop('checked', false)
                                   .trigger('change');
            $('#' + currentPerson).prop('checked', true).trigger('change');
        }
    }).trigger('change');

    $("#splitEqually").click(function() {
        if (this.checked) {
            $('#individualAmount').hide();
        } else {
            $('#individualAmount input').val('');
            $('#individualAmount').show();
        }
    });
});

$(document).ready(function() {
    $('form').submit(function(event) {
        $('input[name=split_with]').val(foo().join(','));
        var details = $('input[name=details]').val().trim();
        if (details.length === 0) {
            alert("Please enter transaction details");
            event.preventDefault();
            return;
        }

        var amountInput = $('input[name=amount]');
        var total = parseFloat(amountInput.val());
        if (isNaN(total) || total <= 0) {
            alert("Amount is invalid");
            event.preventDefault();
            return;
        }
            
        if ($("#splitEqually").is(':checked')) {
            if ($('.participant:checked').length === 0) {
                alert("Must choose at least one person to split");
                event.preventDefault();
                return;
            }
            calculateSplit();
        } else {
            var sum = 0;
            $('#individualAmount input').each(function() {
                var amount = parseFloat(this.value);
                if (!isNaN(amount)) {
                    sum += amount;
                }
            });
            if (sum !== total) {
                alert("Amount does not tally");
                event.preventDefault();
            }
        }
    });
});