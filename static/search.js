var resultsButton = document.querySelector(".results-button");
var aiChatButton = document.querySelector(".ai-chat-button");
var blockResults = document.querySelector(".results");
var blockChat = document.querySelector(".ai-chat");

resultsButton.addEventListener("click", function() {
    resultsButton.classList.add("active");
    blockResults.classList.remove("hidden");

    aiChatButton.classList.remove("active");
    blockChat.classList.add("hidden");
});

aiChatButton.addEventListener("click", function() {
    resultsButton.classList.remove("active");
    blockResults.classList.add("hidden");

    aiChatButton.classList.add("active");
    blockChat.classList.remove("hidden");
});