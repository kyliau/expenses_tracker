function renumberRows() {
  $("tbody th").each(function(index) {
    $(this).text(index);
  });
};

$(document).ready(function() {
  $('#addrow').click(function(e) {
    $("#template-row").clone(true).removeClass("hidden").appendTo("tbody");
    renumberRows();
  });
  $('.glyphicon-remove').click(function(e) {
    $(this).closest('tr').remove();
    renumberRows();
  });
  $('form').submit(function(e) {
    //e.preventDefault();
    var participants = [];
    var moderators   = [];
    $('input[type=email]').each(function() {
      var value = this.value.trim();
      var isModerator = $(this).closest('td').next().children().is(':checked');
      if (value) {
        participants.push(value);
        if (isModerator) {
          moderators.push(value);
        }
      }
    });
    $('input[name=num_participants]').val(participants.length);
    $('input[name=participants]').val(participants.join(','));
    $('input[name=moderators]').val(moderators.join(','));
    $('input[name=num_moderators]').val(moderators.length);
  });
});