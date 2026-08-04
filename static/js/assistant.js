/*
 * CopySwiftAI Assistant
 */

async function sendMessage(event) {

    event.preventDefault();

    const customer =
        localStorage.getItem("copyswift_email") || "Guest";

    const message = document
        .getElementById("message")
        .value
        .trim();

    if (!message) {
        alert("Please enter a message.");
        return;
    }

    try {

        const result = await API.assistant(
            customer,
            "general",
            message,
        );

        console.log(result);

        const response =
            result.conversation?.response ||
            "No response received.";

        document.getElementById(
            "assistant-response"
        ).textContent = response;

    } catch (error) {

        console.error(error);

        document.getElementById(
            "assistant-response"
        ).textContent =
            "Unable to contact the AI Assistant.";
    }

}

window.sendMessage = sendMessage;
