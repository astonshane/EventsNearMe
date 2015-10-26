$(function () {
$('#datetimepicker6').datetimepicker({
  showTodayButton: true,
  sideBySide: true,
  minDate: moment()
});
$('#datetimepicker7').datetimepicker({
    useCurrent: false, //Important! See issue #1075
    showTodayButton: true,
    sideBySide: true,
    minDate: moment()
});
$("#datetimepicker6").on("dp.change", function (e) {
    $('#datetimepicker7').data("DateTimePicker").minDate(e.date);
});
$("#datetimepicker7").on("dp.change", function (e) {
    $('#datetimepicker6').data("DateTimePicker").maxDate(e.date);
});
});
