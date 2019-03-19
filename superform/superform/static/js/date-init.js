var start = new Date();
start.setMinutes(0);
start = new Date(start.getTime() + 60 * 60000 + 60 * 60000);
var end = new Date(start.getTime() + 60 * 60000);
datefrom = start.toISOString();
dateuntil = end.toISOString();
$('#datefrompost').val(dateuntil.substring(0, 10));
$('#dateuntilpost').val(dateuntil.substring(0, 10));
