$.get('http://218.244.133.87/api_fxly/api/ValidateGuest?guestName=%E7%8E%8B%E5%A9%B7%E5%A9%B72%E4%BA%BA&idCard=',function(a){a=$(a);
$('#div1').text(a.find('groupGuestId').text());$('#div2').text(a.find('guestName').text())})
SS
