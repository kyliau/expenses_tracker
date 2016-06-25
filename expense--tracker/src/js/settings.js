$(document).ready(function() {
  var form = $("#project-settings");
  var initialData = form.serialize();
  form.change(function() {
    var newData = form.serialize();
    $("button[type=submit]").prop("disabled", newData === initialData);
  }).submit(function(e) {
    $.post("/settings", $(this).serialize()).done(function(response) {
      $(".alert-success").text(response).slideDown();
    }).fail(function(response) {
      $(".alert-danger").slideDown();
    });
    e.preventDefault();
  });
});