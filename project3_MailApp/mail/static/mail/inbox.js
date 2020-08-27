document.addEventListener('DOMContentLoaded', function () {

    // Use buttons to toggle between views
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
    document.querySelector('#compose').addEventListener('click', compose_email);
    document.querySelector('#compose-form').addEventListener('submit', send_email);

    // By default, load the inbox
    load_mailbox('inbox');
});

function compose_email() {
    document.querySelector('#recipient-error').style.display = 'none';

    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';

    // Clear out composition fields
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
    document.querySelector('#email-list').innerHTML = '';

    // Show the mailbox and hide other views
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'none';

    // Show the mailbox name
    document.querySelector('#mailbox-name').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
    fetch('/emails/' + mailbox)
        .then(response => response.json())
        .then(emails => {
            // Print emails
            render_emails(mailbox, emails)
        });
}

function render_emails(mailbox, emails) {
    for (const email of emails) {
        var clone = document.querySelector('#org-email-node').cloneNode(true);
        clone.id = 'email-' + email.id;
        clone.classList.add('email');
        clone.children.sender.innerHTML = email.sender;
        clone.children.subject.innerHTML = email.subject;
        clone.children.timestamp.innerHTML = email.timestamp;
        if (email.read) {
            clone.classList.add('bg-light');
        }
        clone.addEventListener('click', event => {
            if (event.target.classList.contains('email')) {
                mark_as_read(event.target.id);
                show_email(event.target.id, mailbox);
            } else {
                mark_as_read(event.target.parentNode.id);
                show_email(event.target.parentNode.id, mailbox);
            }
        });
        document.querySelector('#email-list').append(clone);
    }
}

function send_email(event) {
    event.preventDefault();
    var recipients = document.querySelector('#compose-recipients').value;
    var subject = document.querySelector('#compose-subject').value;
    var body = document.querySelector('#compose-body').value;

    fetch('/emails', {
        method: 'POST',
        body: JSON.stringify({
            recipients: recipients,
            subject: subject,
            body: body
        })
    })
        .then(response => response.json())
        .then(result => {
            // Print result
            if ('error' in result) {
                document.querySelector('#recipient-error').innerHTML = result.error;
                document.querySelector('#recipient-error').style.display = 'block';
            } else {
                load_mailbox('sent');
            }
        });
}

function show_email(id, mailbox) {
    document.querySelector('#email-view').innerHTML = '';

    // Show email view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'block';

    var email_id = id.slice(6);
    fetch('/emails/' + email_id)
        .then(response => response.json())
        .then(email => {
            // Print email
            document.querySelector('#email-view').innerHTML += '<p><strong>From: </strong>' + email.sender + '</p>';
            document.querySelector('#email-view').innerHTML += '<p><strong>To: </strong>' + email.recipients.toString() + '</p>';
            document.querySelector('#email-view').innerHTML += '<p><strong>Subject: </strong>' + email.subject + '</p>';
            document.querySelector('#email-view').innerHTML += '<p><strong>Timestamp: </strong>' + email.timestamp + '</p>';
            document.querySelector('#email-view').innerHTML += '<span id="reply-placeholder"></span>';
            document.querySelector('#email-view').innerHTML += '<span id="archive-placeholder"></span>'
            document.querySelector('#email-view').innerHTML += '<hr/>';
            document.querySelector('#email-view').innerHTML += '<pre>' + email.body + '</pre>';

            const replyButton = document.createElement('button');
            replyButton.classList.add('btn', 'btn-sm', 'btn-outline-success');
            replyButton.innerHTML = 'Reply';
            replyButton.addEventListener('click', function (e) {
                e.preventDefault();
                reply_email(email);
            });
            document.querySelector('#reply-placeholder').append(replyButton);

            if (mailbox != 'sent') {
                const archiveButton = document.createElement('button');
                archiveButton.classList.add('btn', 'btn-sm', 'btn-outline-warning');
                if (mailbox == 'inbox') {
                    archiveButton.innerHTML = 'Archive';
                } else if (mailbox == 'archive') {
                    archiveButton.innerHTML = 'Unarchive';
                }
                archiveButton.addEventListener('click', function (e) {
                    e.preventDefault();
                    archive_email(email_id, email.archived);
                });
                document.querySelector('#archive-placeholder').append(archiveButton);
            }
        });
}

function reply_email(email) {
    const userEmail = document.querySelector('#user-email').innerHTML;
    if (email.recipients.includes(userEmail)) {
        //Target email's recipient includes logged-in user -> prefill recipient with target email's sender
        compose_email();
        document.querySelector('#compose-recipients').value = email.sender;
        document.querySelector('#compose-subject').value = 'Re: ' + email.subject;
        document.querySelector('#compose-body').value = 'On ' + email.timestamp + ' ' + email.sender + ' wrote:\n\t' + email.body;
    } else {
        //Target email's recipient does not include logged-in user -> prefill recipient with target email's recipients (replying a sent email)
        compose_email();
        document.querySelector('#compose-recipients').value = email.recipients.toString();
        document.querySelector('#compose-subject').value = 'Re: ' + email.subject;
        document.querySelector('#compose-body').value = 'On ' + email.timestamp + ' ' + email.sender + ' wrote:\n\t' + email.body;
    }
}

function mark_as_read(id) {
    var email_id = id.slice(6);
    fetch('/emails/' + email_id, {
        method: 'PUT',
        body: JSON.stringify({
            read: true
        })
    })
}

function archive_email(email_id, archived) {
    fetch('/emails/' + email_id, {
        method: 'PUT',
        body: JSON.stringify({
            archived: !archived
        })
    })
    .then(setTimeout(function(){
        load_mailbox('inbox');
    }, 100));
}

