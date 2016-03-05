$(function(){


$('button').on('click', function() {

  if ($(this).hasClass("btn-dank")) {
    $.post("vote",
    {
      id: $(this).attr('id'),
      vote: "up"
    });
  } else if ($(this).hasClass("btn-dusty")) {
    $.post("vote",
    {
      id: $(this).attr('id'),
      vote: "down"
    });
  } else {}

})
});
