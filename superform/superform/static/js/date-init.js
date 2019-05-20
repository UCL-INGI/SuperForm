start = new Date();
start.setDate(start.getDate() + 1);
end = new Date(start.getTime());
end.setDate(end.getDate() + 7); //+7 jours
datefrom = start.toISOString();
dateuntil = end.toISOString();
$('#datefrompost').val(datefrom.substring(0, 10));
$('#dateuntilpost').val(dateuntil.substring(0, 10));

/*
var start = new Date();
start.setMinutes(0);
start.setHours(start.getHours() + 2);
var end = new Date(start.getTime()); //+7 jours
end.setHours(end.getHours() + 2);
end.setDate(end.getDate() + 7);
datefrom = start.toISOString();
dateuntil = end.toISOString();
$('#datefrompost').val(datefrom.substring(0, 10));
$('#dateuntilpost').val(dateuntil.substring(0, 10));
console.log(datefrom.substring(11, 16));
$('#starthour').val(datefrom.substring(11, 16));
$('#endhourt').val(dateuntil.substring(11, 16));
 */
