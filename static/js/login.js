/*
 * CopySwiftAI Login Page
 */

async function login(event) {

    event.preventDefault();

    const email = document
        .getElementById("email")
        .value
        .trim();

    if (!email) {
        alert("Please enter your email.");
        return;
    }

    try {

        const result = await API.login(email);

        localStorage.setItem(
            "copyswift_token",
            result.token,
        );

        localStorage.setItem(
            "copyswift_email",
            result.email,
        );

        alert("Login successful!");

        console.log(result);

    } catch (error) {

        console.error(error);

        alert("Login failed.");
    }

}

window.login = login;
