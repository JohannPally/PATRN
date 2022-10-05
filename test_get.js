import snoowrap from 'snoowrap'

const r = new snoowrap({
    user_agent: "Reddit: PATRN:1.0 (by u/<uwukungfuwu>)",
    client_id: "d-7c-MSgBBHA0Mirq5Z3cw",
    client_secret: "EZzaLo5N0p-jmXJYdSF74j7Z7er1VQ",
    username: 'mace_user_account',
    password: 'macebot123'
});

// r.getHot().map(post => post.title).then(console.log);
r.getSubmission('xvtdv2').comments.map(comment => comment.body).then(console.log)
