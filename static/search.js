var resultsButton = document.querySelector(".results-button");
var aiChatButton = document.querySelector(".ai-chat-button");
var blockResults = document.querySelector(".results");
var commentButtons = document.querySelectorAll(".comment-button");
var blockChat = document.querySelector(".ai-chat");
var textArea = document.querySelector(".text-edit");
var sendBox = document.querySelector(".send");
var commentItem  = document.querySelector(".item-comment");
var sendButton = document.getElementById("send-button");
var messages = document.querySelector(".messages");

var reasoning = false;

resultsButton.addEventListener("click", function() {moveToResults()});

aiChatButton.addEventListener("click", function() {moveToMessages()});

function moveToResults() {
    resultsButton.classList.add("active");
    blockResults.classList.remove("hidden");

    aiChatButton.classList.remove("active");
    blockChat.classList.add("hidden");
}

function moveToMessages(item_id=0) {
    resultsButton.classList.remove("active");
    blockResults.classList.add("hidden");

    aiChatButton.classList.add("active");
    blockChat.classList.remove("hidden");
    if (item_id !== 0) {
        commentItem.classList.remove("hidden");
        console.log("title_"+item_id);
        let item = document.getElementById("title_"+item_id);
        console.log(item);
        commentItem.textContent = item.textContent;
    }
}

for (let i = 0; i < commentButtons.length; i++) {
    var commentButton = commentButtons[i];
    commentButton.addEventListener("click", onCommentButtonClick, commentButton);
}

function onCommentButtonClick(commentButton) {
    moveToMessages(item_id=this.id);
    console.log(this.id);
}

textArea.addEventListener("input", function() {
    if (textArea.value && !reasoning) {
        sendButton.classList.remove("inactive");
    } else {
        sendButton.classList.add("inactive");
    }
});

sendButton.addEventListener("click", function() {
    if (textArea.value && !reasoning) {
        reasoning = true;
        sendButton.classList.add("inactive");
        sendMessage(textArea.value);
        textArea.value = "";
    }
});

function sendMessage(messageText) {
    addMessageToHTML("user", messageText);

    let user_id = getUserId();

    let formData = new FormData();
    formData.append("user_id", user_id);
    formData.append("text", messageText);
    formData.append("user_id", user_id);

    fetch(`/send_message`, {
        method: "POST",
        body: formData,
    })
        .then(res => res.json())
        .then(result => {
            var message_id = result.id;
            console.log(message_id);

            if (result.status_code === 400) {
                throw new Error("Ошибка сервера");
            }

            let timer;

            timer = setInterval(() => {
                fetch(`/get_message_answer?user_id=${user_id}&message_id=${message_id}`, {
                    method: "GET",
                })
                    .then(res => res.json())
                    .then(result => {
                        var has_answer = result.has_answer;
                        var text = result.text;

                        console.log(has_answer);
                        console.log(text);

                        if (has_answer === "true") {
                            addMessageToHTML("ai", text);
                            clearInterval(timer);
                        }
                    });
            }, 3000);
        })
        .catch(error => console.error("Ошибка отправки:", error));
}

function addMessageToHTML(sender, message) {
    var messageBox = document.createElement("div");
    var newMessage = document.createElement("div");
    newMessage.textContent = message;
    if (sender === "user") {
        messageBox.classList.add("user-message-box");
        newMessage.classList.add("user-message");
    } else if (sender === "ai") {
        messageBox.classList.add("ai-message-box");
        newMessage.classList.add("ai-message");
        reasoning = false;
        sendButton.classList.remove("inactive");
    }
    messageBox.appendChild(newMessage);
    messages.appendChild(messageBox);
}

function getUserId() {
    var cookies = document.cookie.split("; ");
    for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i];
        if (cookie.includes("user_id")) {
            return cookie.split("=")[1];
        }
    }
}

function getResult() {
    let user_id = getUserId();
    fetch(`/get_result?user_id=${user_id}`, {
        method: 'GET',
    })
        .then(res => res.json())
        .then(result => {
            console.log(result);
            insertResult(result.result);
        });
}

function insertResult(result) {
    for (let i = 0; i < result.length; i++) {
        let id = i;
        let title = result[i][0];
        let item = result[i][1];
    }
}