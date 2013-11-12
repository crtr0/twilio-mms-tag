var c = require('twilio')();

c.sendMessage({
    to:'+16042565585',
    from:'+16042565549',
    body:'tag 7679',
    mediaUrl:'http://images.politico.com/global/blogs/110813_vanilla_ice_465_ap.jpg'
}, function(err, data) {
    console.log(data);
});