$("button").click(function() {
  console.log("hello");
  $('#startTimePicker').data("DateTimePicker") = $('#startTimePicker').data("DateTimePicker").date().toDate().toUTCString();
  $('#endTimePicker').data("DateTimePicker") = $('#endTimePicker').data("DateTimePicker").date().toDate().toUTCString();
});
