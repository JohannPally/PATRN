var express = require("express");
var snoowrap = require('snoowrap');
var path = require('path');

var routes =  require('routes');

var app = express();

app.set("port", process.env.PORT || 3000)
app.use(routes)

app.listen(app.get("port"), function(){
    console.log("Server started on port " + app.get("port"));
});

const r = new snoowrap({
    user_agent: "Reddit: PATRN:1.0 (by u/<uwukungfuwu>)",
    client_id: "d-7c-MSgBBHA0Mirq5Z3cw",
    client_secret: "EZzaLo5N0p-jmXJYdSF74j7Z7er1VQ",
    username: 'mace_user_account',
    password: 'macebot123'
});

function get_post() {
    temp = r.getSubmission(url).comments.map(comment => comment.body).then(console.log)
    alert(temp);
}


// // // r.getHot().map(post => post.title).then(console.log);
// var btn = document.getElementById("link_button");
// // add event listener for the button, for action "click"
// btn.addEventListener("click", get_post());


// function get_post() {
//     url = document.getElementById("link").body
//     temp = r.getSubmission(url).comments.map(comment => comment.body).then(console.log)
//     alert(temp);
// }
